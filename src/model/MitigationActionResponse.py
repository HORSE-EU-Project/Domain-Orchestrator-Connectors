from pydantic import BaseModel
from typing import Dict, Any


class MitigationActionResponse(BaseModel):
    status: str
    testbed: str
    intent_id: str
    message: str
    upstream: Dict[str, Any] | None = None
