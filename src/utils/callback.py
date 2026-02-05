import httpx
import logging
from typing import Optional

logger = logging.getLogger("uvicorn.error")


async def send_status_update(
    callback_url: str,
    intent_id: str,
    status: str,
    info: str,
    timeout: int = 10
) -> bool:
    """
    Send status update to RTR API endpoint.
    
    Args:
        callback_url: The RTR endpoint URL (e.g., http://rtr-api:8000/update_action_status)
        intent_id: The intent ID of the mitigation action
        status: Status of the action - "completed" or "failed"
        info: Information about the action result and testbed(s)
        timeout: Request timeout in seconds
        
    Returns:
        bool: True if callback was successful, False otherwise
    """
    if not callback_url:
        logger.warning(f"No callback URL provided for intent_id {intent_id}")
        return False
    
    payload = {
        "intent_id": intent_id,
        "status": status,
        "info": info
    }
    
    try:
        logger.info(f"Sending status update to RTR: {callback_url}")
        logger.debug(f"Callback payload: {payload}")
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                callback_url,
                json=payload,
                timeout=timeout
            )
        
        if resp.is_success:
            logger.info(f"Successfully sent status update to RTR for intent_id {intent_id}: {status}")
            return True
        else:
            logger.error(
                f"RTR callback failed with status {resp.status_code} for intent_id {intent_id}: {resp.text}"
            )
            return False
            
    except httpx.TimeoutException:
        logger.error(f"Timeout sending callback to {callback_url} for intent_id {intent_id}")
        return False
    except httpx.RequestError as e:
        logger.error(f"Error sending callback to {callback_url} for intent_id {intent_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending callback for intent_id {intent_id}: {e}")
        return False
