import pathlib

from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.config_loader import DEFAULTS, ACTION_SCHEMAS

TEMPLATE_DIR = pathlib.Path(__file__).parent.parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(enabled_extensions=("xml",))
    # autoescape makes sure &, <, > in placeholders are properly escaped
)

def build_umu_xml(req):
    name = req.action.name
    flds = req.action.fields

    if name == "dns_rate_limiting":
        tpl = "qos.xml.j2"
        ctx = {
            "id": req.action.intent_id,
            "device": DEFAULTS["dns_device"],
            "interface": DEFAULTS["dns_iface"],
            "throughput": flds["rate"],
            "unit": DEFAULTS["qos_units"]["rps"],
            "description": f"limit DNS to {flds['rate']} rps",
        }

    elif name == "rate_limiting":
        tpl = "qos.xml.j2"
        rate_num, rate_unit = flds["rate"][:-4], flds["rate"][-4:]
        ctx = {
            "id": req.action.intent_id,
            "device": flds["device"],
            "interface": flds["interface"],
            "throughput": rate_num,
            "unit": rate_unit or DEFAULTS["qos_units"]["bw"],
            "description": f"limit {flds['device']} {flds['interface']} to {flds['rate']}",
        }

    elif name == "block_pod_address":
        tpl = "filtering.xml.j2"
        ctx = {
            "id": req.action.intent_id,
            "device": flds["device"],
            "output_interface": flds["interface"],
            "target": flds["blocked_pod"],
            "description": f"Block pod {flds['blocked_pod']} at {flds['device']}",
        }

    else:
        raise ValueError(f"UMU does not support action: '{name}'")

    xml = env.get_template(tpl).render(**ctx)
    if "{{" in xml:
        raise ValueError("Unresolved placeholders in generated XML")
    return xml.encode(), {"Content-Type": "application/xml"}