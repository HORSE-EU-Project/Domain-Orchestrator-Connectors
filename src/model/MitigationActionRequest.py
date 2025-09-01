from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic import constr
from typing_extensions import Annotated

from src.config_loader import TestBedEnum, ACTION_SCHEMAS, TESTBED_CFG
from src.model.ActionModel import ActionObject


class FieldPairs(BaseModel):
    key: constr(min_length=2)
    value: Any


class MitigationActionRequest(BaseModel):
    model_config = {
        "json_schema_extra": {
            "example": {
                "command": "add",
                "intent_type": "mitigation",
                "intent_id": "dns-limit-001",
                "testbed": "upc",
                "threat": "dns_attack",
                "action": {
                    "name": "dns_rate_limiting",
                    "intent_id": "dns-limit-action-001",
                    "fields": {
                        "rate": "100",
                        "duration": "300",
                        "source_ip_filter": ["192.168.1.100", "10.0.0.5"]
                    }
                },
                "status": "pending",
                "info": "awaiting reinforcement"
            }
        }
    }
    
    command: str
    intent_type: str
    intent_id: str
    target_domain: str | None = ""
    testbed: Annotated[
        TestBedEnum,
        Field(description="Destination test-bed (umu / upc)")
    ]
    action: ActionObject
    attacked_host: str | None = "0.0.0.0"
    mitigation_host: str | None = "0.0.0.0"
    duration: int | None = 0
    message_type: str | None = None

    # Required by MongoDB validator but optional in non-persist contexts
    threat: Optional[str] = Field(default="vul")
    status: Optional[str] = Field(default="pending")
    info: Optional[str] = Field(default="Awaiting enforcement")

    def model_post_init(self, __context):
        self.message_type = TESTBED_CFG[self.testbed.value]["message_type"]

    def validate_action_fields(cls, action: ActionObject) -> ActionObject:
        required_spec = ACTION_SCHEMAS[action.name]  # <-- use .name
        fields = action.fields

        missing = [
            k for k in required_spec
            if k not in fields or cls._is_empty(fields[k])
        ]
        if missing:
            raise ValueError(
                f"Missing or empty field(s) {missing} for action '{action.name}'"
            )
        return action

    @field_validator("intent_id", mode="before")
    @classmethod
    def _strip_spaces(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Missing or empty field 'intent_id'")
        return v.strip()

    def _is_empty(v: Any) -> bool:
        if v is None:
            return True
        if isinstance(v, (str, bytes)) and v.strip() == "":
            return True
        if isinstance(v, list) and len(v) == 0:
            return True
        return False
