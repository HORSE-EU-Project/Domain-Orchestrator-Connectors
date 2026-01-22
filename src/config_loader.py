import enum
import os
import pathlib
from typing import Any, Dict

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
_DEFAULT_YAML = ROOT / "config" / "config.yaml"


def _load_yaml(path: pathlib.Path = _DEFAULT_YAML) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text())


def reload_yaml(path: pathlib.Path = _DEFAULT_YAML):
    global _SPEC, _TESTBED_SPEC, _ACTION_SPEC, ACTION_SCHEMAS, TESTBED_CFG, DOMAIN_ROUTING
    _SPEC = _load_yaml(path)
    _TESTBED_SPEC = _SPEC["testbeds"]
    _ACTION_SPEC = _SPEC["actions"]
    ACTION_SCHEMAS = {n: d["required_fields"] for n, d in _ACTION_SPEC.items()}
    DOMAIN_ROUTING = _SPEC.get("domain_routing", {})
    
    # Override current_domain from environment variable if set
    if "CURRENT_TESTBED" in os.environ:
        DOMAIN_ROUTING["current_domain"] = os.environ["CURRENT_TESTBED"].lower()


_SPEC = _load_yaml()
DEFAULTS = _SPEC.get("defaults", {})
DOMAIN_ROUTING = _SPEC.get("domain_routing", {})

# Override current_domain from environment variable if set
if "CURRENT_TESTBED" in os.environ:
    DOMAIN_ROUTING["current_domain"] = os.environ["CURRENT_TESTBED"].lower()

_TESTBED_SPEC = _SPEC['testbeds']
_ACTION_SPEC = _SPEC['actions']

TestBedEnum = enum.Enum('TestBedEnum', {n.upper(): n for n in _TESTBED_SPEC}, type=str)
ActionEnum = enum.Enum('ActionEnum', {n.upper(): n for n in _ACTION_SPEC}, type=str)

ACTION_SCHEMAS = {name: data['fields'] for name, data in _ACTION_SPEC.items()}
TESTBED_CFG = _SPEC['testbeds']
