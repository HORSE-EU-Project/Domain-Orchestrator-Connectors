from src.dispatch.builders.umu_xml import build_umu_xml
from src.dispatch.builders.upc_json import build_upc_json

BUILDER_REGISTRY = {
    "umu_xml": build_umu_xml,
    "upc_json": build_upc_json,
}
