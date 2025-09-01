import sys
import time
import uvicorn
import logging

from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from pymongo.errors import WriteError

from src.config_loader import reload_yaml
from src.model.MitigationActionRequest import MitigationActionRequest
from src.model.MitigationActionResponse import MitigationActionResponse
from src.dispatch.http import dispatch, DispatchError
from src.utils import mongo
from bson import json_util

logger = logging.getLogger("uvicorn.error")
app = FastAPI(
    title="DOC API",
    description="Domain-Orchestrator-Connector API for 5G/6G Security Testbeds",
    version="1.0.0",
    swagger_ui_parameters={"useLocalAssets": True}
)

start_time = time.time()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    intent_id = payload['intent_id']
    action = payload.get("action")

    err = exc.errors()[0]
    loc = err['loc']
    msg = err['msg']

    if err["type"] == "value_error.missing" and len(loc) >= 3:
        missing_key = loc[-1]
        if action:
            final_msg = f"Missing field {missing_key} for action {action}"
        else:
            final_msg = f"Missing field '{missing_key}'."
    elif err["type"].startswith("value_error") and msg.lower().startswith("value error,"):
        final_msg = msg.split(",", 1)[1].strip()
    else:
        final_msg = msg

    body = {
        "status": "error",
        "intent_id": intent_id,
        "message": final_msg,
    }

    return JSONResponse(status_code=422, content=body)


@app.get("/reload_config")
def reload_config():
    reload_yaml()


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/api/mitigate", response_model=MitigationActionResponse)
async def mitigate(req: MitigationActionRequest):
    # Persist for auditing
    try:
        record = req.model_dump()
        record["_id"] = str(uuid4())
        raw_doc = req.model_dump()
        raw_doc["action"] = json_util.dumps(raw_doc["action"])
        mongo.insert_raw(record)
    except WriteError as we:
        logger.error(we.details)

    # Forward to testbed, and await reply
    try:
        upstream_reply = await dispatch(req)
    except DispatchError as e:
        logger.error(e)
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

    return MitigationActionResponse(
        status="success",
        testbed=req.testbed.value,
        intent_id=req.intent_id,
        message="Action forwarded for processing.",
        upstream=upstream_reply,
    )
#
if __name__ == '__main__':
    print(mongo)
    if not mongo.ping():
        logger.error("MongoDB unreachable; exiting.")
        sys.exit(1)
    else:
        logger.info("MongoDB reachable")
        uvicorn.run(app, host='0.0.0.0', port=8000)