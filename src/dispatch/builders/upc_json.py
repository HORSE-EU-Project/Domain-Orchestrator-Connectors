import json


def build_upc_json(req) -> tuple[bytes, dict]:
    """
    UPC now wants only:
      {"fields": {...}}
    """
    # support both new (req.action.fields) and older (req.fields) shapes:
    if hasattr(req, "action") and hasattr(req.action, "fields"):
        fields = req.action.fields
    else:
        fields = req.fields  # fallback if model differs in tests

    body = {"fields": fields}
    return json.dumps(body).encode("utf-8"), {"Content-Type": "application/json"}
