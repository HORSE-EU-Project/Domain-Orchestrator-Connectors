VALID_PAYLOAD_EXECUTE_TEST_1 = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "execute_test_1",
    "testbed": None,
    "threat": "api_vul",
    "action": {
        "name": "execute_test_1",
        "intent_id": "execute-test-1",
        "fields": {"test_id": "1", "modules": ["Pre-processing", "DEME", "DTE", "IBI", "CKB", "RTR", "ePEM", "CAS"]}
    },
    "status": "pending",
    "info" : "awaiting reinforcement"
}

VALID_PAYLOAD_EXECUTE_TEST_2 = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "execute_test_2",
    "testbed": None,
    "threat": "api_vul",
    "action": {
        "name": "execute_test_2",
        "intent_id": "execute-test-2",
        "fields": {"test_id": "2",
                   "modules": ["Pre-processing", "EM", "P&P DT", "DTE", "IBI", "CKB", "IA DT", "RTR", "ePEM", "CAS"]}
    },
    "status": "pending",
    "info" : "awaiting reinforcement"
}

VALID_PAYLOAD_BLOCK_IP_ADDRESSES = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "block-ip-42",
    "testbed": None,
    "threat": "api_vul",
    "action": {
        "name": "block_ip_addresses",
        "intent_id": "block-ip-42-01",
        "fields": {"blocked_ips": ["192.168.1.100", "192.168.1.101", "192.168.1.102"]}
    },
    "status": "pending",
    "info" : "awaiting reinforcement"
}

VALID_PAYLOAD_BLOCK_UES_MULTIDOMAIN = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "block_ues_multidomain-42",
    "testbed": None,
    "threat": "api_vul",
    "action": {
        "name": "block_ues_multidomain",
        "intent_id": "block_ues_multidomain-42",
        "fields": {"rate_limiting": "generic"}
    },
    "status": "pending",
    "info" : "awaiting reinforcement"
}

VALID_PAYLOAD_DNS_RATE_LIMITING = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "dns_rate_limiting-42",
    "testbed": None,
    "threat": "api_vul",
    "action": {
        "name": "dns_rate_limiting",
        "intent_id": "dns_rate_limiting-42",
        "fields": {"rate": "20", "duration": "60", "source_ip_filter": ["malicious_ips"]}
    },
    "status": "pending",
    "info" : "awaiting reinforcement"
}


VALID_PAYLOAD_ROUTER_RATE_LIMIT = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "router_rate_limiting-42",
    "testbed": None,
    "threat": "api_vul",
    "action": {
        "name": "router_rate_limiting",
        "intent_id": "router_rate_limiting-42",
        "fields": 	{"fields": { "device": "Device", "rate": "100", "duration": "120" } }
    },
    "status": "pending",
    "info" : "awaiting reinforcement"
}

# Multi-domain payloads
VALID_PAYLOAD_MULTI_DOMAIN_DNS_RATE_LIMITING = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "multi-dns-limit-001",
    "target_domain": ["upc", "umu"],
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

VALID_PAYLOAD_MULTI_DOMAIN_BLOCK_IP = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "multi-block-ip-001",
    "target_domain": ["upc"],
    "threat": "ip_attack",
    "action": {
        "name": "block_ip_addresses",
        "intent_id": "block-ip-action-001",
        "fields": {
            "blocked_ips": ["192.168.1.100", "192.168.1.101"]
        }
    },
    "status": "pending",
    "info": "awaiting reinforcement"
}

# Multi-domain with CNIT
VALID_PAYLOAD_MULTI_DOMAIN_WITH_CNIT = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "multi-with-cnit-001",
    "target_domain": ["upc", "cnit"],
    "threat": "attack",
    "action": {
        "name": "block_ip_addresses",
        "intent_id": "block-ip-cnit-001",
        "fields": {
            "blocked_ips": ["192.168.1.100"]
        }
    },
    "status": "pending",
    "info": "awaiting reinforcement"
}

# Single-element list that should be normalized
VALID_PAYLOAD_SINGLE_ELEMENT_LIST_CNIT = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "single-list-cnit-001",
    "target_domain": ["cnit"],  # Single-element list
    "threat": "attack",
    "action": {
        "name": "block_ip_addresses",
        "intent_id": "block-ip-single-001",
        "fields": {
            "blocked_ips": ["192.168.1.100"]
        }
    },
    "status": "pending",
    "info": "awaiting reinforcement"
}

# Single string CNIT
VALID_PAYLOAD_SINGLE_STRING_CNIT = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "single-string-cnit-001",
    "target_domain": "cnit",  # Single string
    "threat": "attack",
    "action": {
        "name": "block_ip_addresses",
        "intent_id": "block-ip-string-001",
        "fields": {
            "blocked_ips": ["192.168.1.100"]
        }
    },
    "status": "pending",
    "info": "awaiting reinforcement"
}