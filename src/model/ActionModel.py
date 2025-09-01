from pydantic import BaseModel, Field
from typing import Dict, Any

class ActionObject(BaseModel):
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "dns_rate_limiting",
                "intent_id": "dns-limit-action-001",
                "fields": {
                    "rate": "100",
                    "duration": "300",
                    "source_ip_filter": ["192.168.1.100", "10.0.0.5"]
                }
            }
        }
    }
    
    name: str = Field(..., description="Action key, e.g. dns_rate_limiting")
    intent_id: str = Field(..., description="Per-action ID")
    fields: Dict[str, Any] = Field(..., description="Action-specific k/v pairs")