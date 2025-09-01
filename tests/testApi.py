import json
from lxml import etree

import pytest
from fastapi.testclient import TestClient

from src.main import app
from tests.incomingMessages import *

UPC = 'upc'
UMU = 'umu'

@pytest.fixture
def client():
    return TestClient(app)

def test_upc_execute_test_1(client, httpx_mock, patch_mongo):
    payload = VALID_PAYLOAD_EXECUTE_TEST_1
    payload["testbed"] = UPC

    httpx_mock.add_response(
        method="POST",
        url="http://10.19.2.1/execute_test",
        status_code=200,
        json={
            "message": "Test 1 executed successfully with modules: Pre-processing, DEME, DTE, IBI, CKB, RTR, ePEM, CAS"},
    )

    resp = client.post("/api/mitigate", json=payload)
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    body = resp.json()
    assert body["upstream"] == {
        "message": "Test 1 executed successfully with modules: Pre-processing, DEME, DTE, IBI, CKB, RTR, ePEM, CAS"}
    patch_mongo.assert_called_once()
    assert len(httpx_mock.get_requests()) == 1
    req = httpx_mock.get_requests()[0]
    assert req.headers["Content-Type"].startswith("application/json")
    assert req.url == "http://10.19.2.1/execute_test"
    assert req.method == "POST"
    sent_json = json.loads(req.content)
    assert sent_json == { "fields": { "test_id": "1", "modules": ["Pre-processing", "DEME", "DTE", "IBI", "CKB", "RTR", "ePEM", "CAS"] }}

def test_upc_execute_test_2(client, httpx_mock, patch_mongo):
    payload = VALID_PAYLOAD_EXECUTE_TEST_2
    payload["testbed"] = UPC

    httpx_mock.add_response(
        method="POST",
        url="http://10.19.2.1/execute_test",
        status_code=200,
        json={
            "message": "Test 2 executed successfully with modules: Pre-processing, EM, P&P DT, DTE, IBI, CKB, IA DT, RTR, ePEM, CAS"},
    )

    resp = client.post("/api/mitigate", json=payload)
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    body = resp.json()
    assert body["upstream"] == {
        "message": "Test 2 executed successfully with modules: Pre-processing, EM, P&P DT, DTE, IBI, CKB, IA DT, RTR, ePEM, CAS"}
    patch_mongo.assert_called_once()
    assert len(httpx_mock.get_requests()) == 1
    req = httpx_mock.get_requests()[0]
    assert req.headers["Content-Type"].startswith("application/json")
    assert req.url == "http://10.19.2.1/execute_test"
    assert req.method == "POST"
    sent_json = json.loads(req.content)
    assert sent_json == { "fields": { "test_id": "2", "modules": ["Pre-processing", "EM", "P&P DT", "DTE", "IBI", "CKB", "IA DT", "RTR", "ePEM", "CAS"] }}


def test_upc_block_ip_addresses(client, httpx_mock, patch_mongo):
    payload = VALID_PAYLOAD_BLOCK_IP_ADDRESSES
    payload["testbed"] = UPC

    httpx_mock.add_response(
        method="POST",
        url="http://10.19.2.1/block_ip_addresses",
        status_code=200,
        json={"message": "Blocked IP addresses: 192.168.1.100, 192.168.1.101, 192.168.1.102"},
    )

    resp = client.post("/api/mitigate", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["upstream"] == {"message": "Blocked IP addresses: 192.168.1.100, 192.168.1.101, 192.168.1.102"}
    patch_mongo.assert_called_once()
    assert len(httpx_mock.get_requests()) == 1
    req = httpx_mock.get_requests()[0]
    assert req.headers["Content-Type"].startswith("application/json")
    assert req.url == "http://10.19.2.1/block_ip_addresses"
    assert req.method == "POST"
    sent_json = json.loads(req.content)
    assert sent_json == {
        "fields": {
            "blocked_ips": [
                "192.168.1.100",
                "192.168.1.101",
                "192.168.1.102",
            ]
        }
    }


def test_upc_block_ues_multidomain(client, httpx_mock, patch_mongo):
    payload = VALID_PAYLOAD_BLOCK_UES_MULTIDOMAIN
    payload["testbed"] = UPC

    httpx_mock.add_response(
        method="POST",
        url="http://10.19.2.1/block_ues_multidomain",
        status_code=200,
        json={"message": "Block UEs rate limit 50/s on port 53 applied"},
    )

    resp = client.post("/api/mitigate", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["upstream"] == {"message": "Block UEs rate limit 50/s on port 53 applied"}
    patch_mongo.assert_called_once()
    assert len(httpx_mock.get_requests()) == 1
    req = httpx_mock.get_requests()[0]
    assert req.headers["Content-Type"].startswith("application/json")
    assert req.url == "http://10.19.2.1/block_ues_multidomain"
    assert req.method == "POST"
    sent_json = json.loads(req.content)
    assert sent_json == {
        "fields": {
            "blocked_ips": [
                "192.168.1.100",
                "192.168.1.101",
                "192.168.1.102",
            ]
        }
    }


def test_upc_dns_rate_limiting(client, httpx_mock, patch_mongo):
    payload = VALID_PAYLOAD_DNS_RATE_LIMITING
    payload["testbed"] = UPC

    httpx_mock.add_response(
        method="POST",
        url="http://10.19.2.1/dns_rate_limiting",
        status_code=200,
        json={
            "message": "Rate limiting applied on dnsserver for 20 requests per second for 60 seconds on the IPs: 172.21.1.121."},
    )

    resp = client.post("/api/mitigate", json=payload)
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    body = resp.json()
    assert body["upstream"] == {
        "message": "Rate limiting applied on dnsserver for 20 requests per second for 60 seconds on the IPs: 172.21.1.121."}
    patch_mongo.assert_called_once()
    assert len(httpx_mock.get_requests()) == 1
    req = httpx_mock.get_requests()[0]
    assert req.headers["Content-Type"].startswith("application/json")
    assert req.url == "http://10.19.2.1/dns_rate_limiting"
    assert req.method == "POST"
    sent_json = json.loads(req.content)
    assert sent_json == { "fields": { "rate": "20", "duration": "60", "source_ip_filter": ["malicious_ips"] } }
#
# def test_upc_router_rate_limiting(client, httpx_mock, patch_mongo):
#     payload = VALID_PAYLOAD_ROUTER_RATE_LIMIT
#     payload["testbed"] = UPC
#
#     httpx_mock.add_response(
#         method="POST",
#         url="http://10.19.2.1/router_rate_limiting",
#         status_code=200,
#         json={"message": "Rate limiting applied on routerDNS for 100 requests per second for 120 seconds."},
#     )
#
#     resp = client.post("/api/mitigate", json=VALID_PAYLOAD_UPC)
#     print(resp.status_code, resp.json())
#     assert resp.status_code == 200
#     body = resp.json()
#     assert body["upstream"] == {
#         "message": "Rate limiting applied on routerDNS for 100 requests per second for 120 seconds."}
#     patch_mongo.assert_called_once()
#     assert len(httpx_mock.get_requests()) == 1
#     req = httpx_mock.get_requests()[0]
#     assert req.headers["Content-Type"].startswith("application/json")
#     assert req.url == "http://10.19.2.1/router_rate_limiting"
#     assert req.method == "POST"
#     sent_json = json.loads(req.content)
#     assert sent_json ==	{"fields": { "device": "Device", "rate": "100", "duration": "120" } }
#
#


#### UMU ####

UMU_URL = "http://10.208.11.70:8002/meservice"

def assert_no_placeholders(xml_str: str):
    assert "{{" not in xml_str and "}}" not in xml_str

def assert_xml_has(xml, xpath):
    ns = {"x": "http://modeliosoft/xsddesigner/a22bd60b-ee3d-425c-8618-beb6a854051a/ITResource.xsd"}
    assert xml.xpath(xpath, namespaces=ns)

def test_umu_dns_rate_limit_success(client, httpx_mock, patch_mongo):
    payload = VALID_PAYLOAD_DNS_RATE_LIMITING
    payload["testbed"] = UMU

    httpx_mock.add_response(
        method="POST",
        url=UMU_URL,
        status_code=200,
        text="The security policy has been enforced successfully"
    )

    resp = client.post("/api/mitigate", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["upstream"] == {
        "raw": "The security policy has been enforced successfully"
    }

    patch_mongo.assert_called_once()
    reqs = httpx_mock.get_requests()
    assert len(reqs) == 1
    req = reqs[0]
    assert req.method == "POST"
    assert str(req.url) == UMU_URL
    assert req.headers["Content-Type"] == "application/xml"
    xml_str = req.content.decode()
    assert_no_placeholders(xml_str)

    xml = etree.fromstring(xml_str.encode())
    assert_xml_has(xml, ".//x:configurationRuleAction/x:qosActionType[.='LIMIT']")
    assert_xml_has(xml, ".//x:throughput[.='20']")



#### OLD ####

def test_qos_template_renders():
    from src.dispatch.builders.umu_xml import env
    tpl = env.get_template("qos.xml.j2")
    out = tpl.render(
        id="30001",
        device="dns-s",
        interface="eth0",
        throughput=20,
        unit="rps",
        description="limit DNS to 20 rps",
    )
    assert "<throughput>20</throughput>" in out



def test_mitigate_sad_path(client):
    PAYLOAD = {
        "testbed": "umus",
        "action": "firewall_pfcp_requests",
        "intent_id": "limit-dns-42",
        "fields": {
            "ip": "192.168.1.100",
            "rate": "10req/s"
        }
    }
    response = client.post("/api/mitigate", json=PAYLOAD)
    assert response.status_code == 422


def test_mitigate_sad_path_2(client):
    PAYLOAD = {
        "testbed": "umus",
        "action": "firewall_pfcp_requests",
        "intent_id": "limit-dns-42",
        "fields": {
            "ip": "192.168.1.100",
            "rate": "10req/s"
        }
    }
    response = client.post("/api/mitigate", json=PAYLOAD)
    print(response.json())
    assert response.status_code == 422


def test_mitigate_sad_path_3(client):
    PAYLOAD = {
        "testbed": "umu",
        "action": "firewall_pfcsp_requests",
        "intent_id": "limit-dns-42",
        "fields": {
            "ip": "192.168.1.100",
            "rate": "10req/s"
        }
    }
    response = client.post("/api/mitigate", json=PAYLOAD)
    assert response.status_code == 422


def test_mitigate_sad_path_4(client):
    PAYLOAD = {
        "testbed": "umu",
        "action": "firewall_pfcsp_requests",
        "intent_id": "limit-dns-42",
        "fields": {}
    }
    response = client.post("/api/mitigate", json=PAYLOAD)
    assert response.status_code == 422


def test_mitigate_sad_path_5(client):
    PAYLOAD = {
        "testbed": "umu",
        "action": "firewall_pfcsp_requests",
        "intent_id": "",
        "fields": {
            "ip": "192.168.1.100",
            "rate": "10req/s"
        }
    }
    response = client.post("/api/mitigate", json=PAYLOAD)
    assert response.status_code == 422


def test_missing_ip_returns_custom_error(client):
    bad_payload = {
        "testbed": "umu",
        "action": "dns_rate_limiting",
        "intent_id": "limit-dns-42",
        "fields": {"duration": 10,
                   "rate": 120}  # 'source_ip_filter' missing
    }

    r = client.post("/api/mitigate", json=bad_payload)
    assert r.status_code == 422
    body = r.json()
    print(f"BODY: {body}")
    assert body == {
        "status": "error",
        "intent_id": "limit-dns-42",
        "message": "Missing or empty field(s) ['source_ip_filter'] for action 'dns_rate_limiting'"
    }


def test_upc_block_ip_addresses_missing_fields(client, httpx_mock, patch_mongo):
    VALID_PAYLOAD_UPC = {
        "testbed": "upc",
        "action": "block_ip_addresses",
        "intent_id": "block-ip-42",
        "fields": {
        }
    }

    resp = client.post("/api/mitigate", json=VALID_PAYLOAD_UPC)
    print(resp.status_code, resp.json())
    assert resp.status_code == 422
    body = resp.json()
    assert body == {'status': 'error', 'intent_id': 'block-ip-42',
                    'message': "Missing or empty field(s) ['blocked_ips'] for action 'block_ip_addresses'"}





def test_upc_define_dns_servers(client, httpx_mock, patch_mongo):
    VALID_PAYLOAD_UPC = {
        "testbed": "upc",
        "action": "define_dns_servers",
        "intent_id": "define_dns_servers-1",
        "fields": {"dns_servers": ["server_list"]}
    }

    httpx_mock.add_response(
        method="POST",
        url="http://10.19.2.1/define_dns_servers",
        status_code=200,
        json={"dns_servers": {"name": "dnsserver", "ip": "172.21.5.5"}},
    )

    resp = client.post("/api/mitigate", json=VALID_PAYLOAD_UPC)
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    body = resp.json()
    assert body["upstream"] == {"dns_servers": {"name": "dnsserver", "ip": "172.21.5.5"}}
    patch_mongo.assert_called_once()
    assert len(httpx_mock.get_requests()) == 1
    req = httpx_mock.get_requests()[0]
    assert req.url == "http://10.19.2.1/define_dns_servers"
    assert req.method == "POST"


def test_upc_firewall_pfcp_requests(client, httpx_mock, patch_mongo):
    VALID_PAYLOAD_UPC = {
        "testbed": "upc",
        "action": "firewall_pfcp_requests",
        "intent_id": "firewall_pfcp_requests-1",
        "fields": {"drop_percentage": "X", "request_types": ["Deletion", "Establishment", "Modification"]}
    }

    httpx_mock.add_response(
        method="POST",
        url="http://10.19.2.1/firewall_pfcp_requests",
        status_code=200,
        json={"message": f"Firewall PFCP requests drop X% on port 8805 applied"},
    )

    resp = client.post("/api/mitigate", json=VALID_PAYLOAD_UPC)
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    body = resp.json()
    assert body["upstream"] == {"message": f"Firewall PFCP requests drop X% on port 8805 applied"}
    patch_mongo.assert_called_once()
    assert len(httpx_mock.get_requests()) == 1
    req = httpx_mock.get_requests()[0]
    assert req.url == "http://10.19.2.1/firewall_pfcp_requests"
    assert req.method == "POST"


def test_upc_validate_smf_integrity(client, httpx_mock, patch_mongo):
    VALID_PAYLOAD_UPC = {
        "testbed": "upc",
        "action": "validate_smf_integrity",
        "intent_id": "validate_smf_integrity-1",
        "fields": {"check": "if compromised", "action": "restart"}
    }

    httpx_mock.add_response(
        method="POST",
        url="http://10.19.2.1/validate_smf_integrity",
        status_code=200,
        json={"message": "The SMF container is compromised and will be restarted."},
    )

    resp = client.post("/api/mitigate", json=VALID_PAYLOAD_UPC)
    print(resp.status_code, resp.json())
    assert resp.status_code == 200
    body = resp.json()
    assert body["upstream"] == {"message": "The SMF container is compromised and will be restarted."}
    patch_mongo.assert_called_once()
    assert len(httpx_mock.get_requests()) == 1
    req = httpx_mock.get_requests()[0]
    assert req.url == "http://10.19.2.1/validate_smf_integrity"
    assert req.method == "POST"
