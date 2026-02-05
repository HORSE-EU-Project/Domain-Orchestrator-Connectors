import sys
import time
import uvicorn
import logging

from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from pymongo.errors import WriteError

from src.config_loader import reload_yaml, DOMAIN_ROUTING
from src.model.MitigationActionRequest import MitigationActionRequest
from src.model.MitigationActionResponse import MitigationActionResponse
from src.dispatch.http import dispatch, DispatchError
from src.utils import mongo
from src.utils.callback import send_status_update
from bson import json_util
import httpx

logger = logging.getLogger("uvicorn.error")
app = FastAPI(
    title="DOC API",
    description="Domain-Orchestrator-Connector API for 5G/6G Security Testbeds",
    version="1.0.0",
    swagger_ui_parameters={"useLocalAssets": True}
)

start_time = time.time()


async def forward_to_doc(target_domain: str, payload: dict) -> dict:
    """
    Forward mitigation request to another DOC instance in a different domain.
    """
    doc_url = DOMAIN_ROUTING.get("doc_instances", {}).get(target_domain.lower())
    if not doc_url:
        raise ValueError(f"No DOC instance configured for domain '{target_domain}'")
    
    endpoint = f"{doc_url}/api/mitigate"
    logger.info(f"Forwarding request to DOC in '{target_domain}' at {endpoint}")
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(endpoint, json=payload, timeout=30)
        
        if not resp.is_success:
            raise DispatchError(f"DOC at {endpoint} responded {resp.status_code}: {resp.text}")
        
        return resp.json()
    except httpx.RequestError as e:
        raise DispatchError(f"Failed to forward to DOC at {endpoint}: {str(e)}")


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
async def mitigate(req: MitigationActionRequest, request: Request):
    # Auto-populate callback_url from requesting client if not provided
    if not req.callback_url:
        from src.config_loader import RTR_API_CFG
        client_host = request.client.host if request.client else "localhost"
        client_port = request.client.port if request.client else 8000
        callback_endpoint = RTR_API_CFG.get("callback_endpoint", "/update_action_status")
        req.callback_url = f"http://{client_host}:{client_port}{callback_endpoint}"
        logger.info(f"Auto-populated callback_url from client: {req.callback_url}")
    
    # Persist for auditing
    try:
        record = req.model_dump()
        record["_id"] = str(uuid4())
        raw_doc = req.model_dump()
        raw_doc["action"] = json_util.dumps(raw_doc["action"])
        mongo.insert_raw(record)
    except WriteError as we:
        logger.error(we.details)

    # Handle multi-domain execution
    if isinstance(req.target_domain, list):
        from src.config_loader import TESTBED_CFG, TestBedEnum
        results = {}
        failed_domains = []
        current_domain = DOMAIN_ROUTING.get("current_domain", "").lower()
        
        for domain in req.target_domain:
            domain_lower = domain.lower()
            
            # Check if domain is valid (exists in config)
            if domain_lower not in TESTBED_CFG:
                logger.warning(f"Skipping invalid domain: {domain}")
                results[domain] = {"status": "skipped", "reason": "Invalid domain"}
                continue
            
            # Check if this domain should be forwarded to another DOC instance
            if current_domain and domain_lower != current_domain:
                logger.info(f"Forwarding domain '{domain}' to remote DOC instance")
                try:
                    # Create payload for forwarding with single target_domain
                    forward_payload = req.model_dump()
                    forward_payload["target_domain"] = domain  # Single domain for remote DOC
                    
                    forwarded_response = await forward_to_doc(domain_lower, forward_payload)
                    results[domain] = {"status": "forwarded", "response": forwarded_response}
                except DispatchError as e:
                    logger.error(f"Failed to forward to DOC in {domain}: {e}")
                    results[domain] = {"status": "error", "reason": f"Forwarding failed: {str(e)}"}
                    failed_domains.append(domain)
                except Exception as e:
                    logger.error(f"Unexpected error forwarding to {domain}: {e}")
                    results[domain] = {"status": "error", "reason": str(e)}
                    failed_domains.append(domain)
                continue
            
            # Create a copy of the request for this specific domain
            domain_req = req.model_copy()
            # Convert string to TestBedEnum
            domain_req.testbed = TestBedEnum[domain_lower.upper()]
            domain_req.message_type = TESTBED_CFG[domain_lower]["message_type"]
            
            # Attempt dispatch to this domain
            try:
                upstream_reply, status_code, success = await dispatch(domain_req)
                results[domain] = {
                    "status": "success" if success else "error",
                    "response": upstream_reply,
                    "http_status": status_code
                }
                if not success:
                    failed_domains.append(domain)
            except DispatchError as e:
                logger.error(f"Failed to dispatch to {domain}: {e}")
                results[domain] = {"status": "error", "reason": str(e)}
                failed_domains.append(domain)
            except Exception as e:
                logger.error(f"Unexpected error dispatching to {domain}: {e}")
                results[domain] = {"status": "error", "reason": str(e)}
                failed_domains.append(domain)
        
        # Return aggregated response
        overall_status = "partial_success" if failed_domains and len(failed_domains) < len(req.target_domain) else (
            "success" if not failed_domains else "error"
        )
        
        # Send callback to RTR
        success_count = len(results) - len(failed_domains)
        total_count = len(req.target_domain)
        
        # Build detailed info message
        info_parts = [f"Multi-domain execution: {success_count}/{total_count} successful"]
        for domain, result in results.items():
            if result["status"] == "success":
                info_parts.append(f"✓ Action enforced in {domain.upper()} testbed")
            elif result["status"] == "forwarded":
                info_parts.append(f"→ Action forwarded to {domain.upper()} domain")
            else:
                reason = result.get("reason", "Unknown error")
                info_parts.append(f"✗ Action failed in {domain.upper()} testbed: {reason}")
        
        callback_status = "completed" if overall_status == "success" else (
            "partial" if overall_status == "partial_success" else "failed"
        )
        callback_info = " | ".join(info_parts)
        
        await send_status_update(
            callback_url=req.callback_url,
            intent_id=req.intent_id,
            status=callback_status,
            info=callback_info
        )
        
        return MitigationActionResponse(
            status=overall_status,
            testbed="multi-domain",
            intent_id=req.intent_id,
            message=f"Multi-domain execution completed. Success: {len(results) - len(failed_domains)}/{len(req.target_domain)}",
            upstream=results,
        )

    # Single domain execution (original behavior)
    current_domain = DOMAIN_ROUTING.get("current_domain", "").lower()
    target_domain = req.target_domain.lower() if isinstance(req.target_domain, str) else ""
    
    # Check if we need to forward to another DOC instance
    if current_domain and target_domain and target_domain != current_domain:
        logger.info(f"Forwarding single-domain request to DOC in '{target_domain}'")
        try:
            forward_payload = req.model_dump()
            forwarded_response = await forward_to_doc(target_domain, forward_payload)
            
            return MitigationActionResponse(
                status="success",
                testbed=target_domain,
                intent_id=req.intent_id,
                message="Action forwarded to remote DOC instance.",
                upstream={"forwarded": forwarded_response},
            )
        except DispatchError as e:
            logger.error(f"Failed to forward to DOC in {target_domain}: {e}")
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error forwarding to {target_domain}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Dispatch locally to the testbed in this domain
    try:
        upstream_reply, status_code, success = await dispatch(req)
        
        # Send callback to RTR
        testbed_name = req.testbed.value.upper()
        if success:
            callback_status = "completed"
            callback_info = f"Action successfully enforced in {testbed_name} testbed"
        else:
            callback_status = "failed"
            error_msg = upstream_reply.get("error", upstream_reply.get("raw", "Unknown error"))
            callback_info = f"Action failed in {testbed_name} testbed: {error_msg}"
        
        await send_status_update(
            callback_url=req.callback_url,
            intent_id=req.intent_id,
            status=callback_status,
            info=callback_info
        )
        
        # If dispatch was not successful, raise exception for proper error response
        if not success:
            error_detail = upstream_reply.get("error", upstream_reply.get("raw", f"Testbed responded with HTTP {status_code}"))
            raise HTTPException(status_code=502, detail=error_detail)
            
    except DispatchError as e:
        logger.error(e)
        
        # Send failure callback to RTR
        testbed_name = req.testbed.value.upper() if req.testbed else "unknown"
        await send_status_update(
            callback_url=req.callback_url,
            intent_id=req.intent_id,
            status="failed",
            info=f"Action failed in {testbed_name} testbed: {str(e)}"
        )
        
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(e)
        
        # Send failure callback to RTR
        testbed_name = req.testbed.value.upper() if req.testbed else "unknown"
        await send_status_update(
            callback_url=req.callback_url,
            intent_id=req.intent_id,
            status="failed",
            info=f"Action failed in {testbed_name} testbed: {str(e)}"
        )
        
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