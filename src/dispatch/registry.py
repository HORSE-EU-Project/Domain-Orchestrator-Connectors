from src.dispatch.builders.umu_xml import build_umu_xml
from src.dispatch.builders.upc_json import build_upc_json
from src.dispatch.builders.cnit_passthrough import build_cnit_passthrough

BUILDER_REGISTRY = {
    "umu_xml": build_umu_xml,
    "upc_json": build_upc_json,
    "cnit_passthrough": build_cnit_passthrough,
}
