def build_cnit_passthrough(req):
    """
    CNIT passthrough builder - acknowledges the action without actual dispatch.
    Returns a simple success message indicating the domain was handled.
    """
    response = {
        "status": "acknowledged",
        "message": "Domain already handled or not within reachable domains",
        "intent_id": req.action.intent_id,
        "action": req.action.name
    }
    
    import json
    return json.dumps(response).encode("utf-8"), {"Content-Type": "application/json"}
