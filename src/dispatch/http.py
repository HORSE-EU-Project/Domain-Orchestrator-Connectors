import httpx
import logging

from src.config_loader import TESTBED_CFG
from src.dispatch.registry import BUILDER_REGISTRY

logger = logging.getLogger("uvicorn.error")

class DispatchError(Exception):
    """I use this to wrap any network / 4xx / 5xx errors we want to bubble up."""
    pass

def resolve_endpoint(testbed: str, action: str) -> str:
    cfg = TESTBED_CFG[testbed]
    # per-action mapping (UPC style)
    if "endpoints" in cfg:
        # Convert action to lowercase for case-insensitive lookup
        action_lower = action.lower()
        try:
            return cfg["endpoints"][action_lower]
        except KeyError:
            raise ValueError(
                f"Action '{action}' not allowed on test-bed '{testbed}'. "
                f"Allowed: {list(cfg['endpoints'])}"
            )

    # single-URL test-bed (UMU style)
    return cfg["base_url"]

async def dispatch(req_model):
    """
    1. Build payload via the registry
    2. POST to the correct endpoint
    3. Return tuple: (response_data, http_status_code, success_flag)
    4. Raise DispatchError on non-2xx
    
    Special case: CNIT passthrough returns immediately without HTTP call
    
    Returns:
        tuple: (response_dict, status_code, success_bool)
    """
    builder = BUILDER_REGISTRY[req_model.message_type]
    body_bytes, headers = builder(req_model)
    
    # Log the mitigation message before sending
    logger.info(f"Dispatching mitigation action: testbed={req_model.testbed.value}, action={req_model.action.name}, intent_id={req_model.intent_id}")
    logger.debug(f"Payload: {body_bytes.decode('utf-8')}")
    logger.debug(f"Headers: {headers}")
    
    # CNIT passthrough - return the built response directly without HTTP call
    if req_model.message_type == "cnit_passthrough":
        import json
        response_data = json.loads(body_bytes.decode("utf-8"))
        return response_data, 200, True
    
    url = resolve_endpoint(req_model.testbed.value, req_model.action.name)
    logger.info(f"Sending mitigation request to: {url}")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, content=body_bytes, headers=headers, timeout=15)
    except httpx.ConnectTimeout:
        logger.error(f"Timeout connecting to {url}")
        raise DispatchError(f"Timeout connecting to {url}")
    except httpx.ConnectError as e:
        logger.error(f"Connection error while reaching {url}: {e}")
        raise DispatchError(f"Failed to connect to {url} — likely unreachable.")
    except httpx.RequestError as e:
        logger.error(f"Unexpected request error during dispatch to {url}: {repr(e)}")
        raise DispatchError(f"Error dispatching to {url}: {e.__class__.__name__}")



    if not resp.is_success:
        logger.warning(f"Dispatch to {url} returned {resp.status_code}: {resp.text}")
        # Return response data with failure status
        try:
            response_data = resp.json()
        except ValueError:
            response_data = {"raw": resp.text, "error": f"HTTP {resp.status_code}"}
        return response_data, resp.status_code, False

    # Most UPC endpoints answer JSON; fall back to text
    try:
        response_data = resp.json()
    except ValueError:
        response_data = {"raw": resp.text}
    
    return response_data, resp.status_code, True