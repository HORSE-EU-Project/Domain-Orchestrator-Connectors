"""
Example payloads demonstrating the callback feature for status updates.

These examples show how to include a callback_url in mitigation requests
so that DOC can send status updates back to the RTR API after enforcement.
"""

# Example 1: Single-domain action with callback
CALLBACK_DNS_RATE_LIMITING = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "dns-limit-callback-001",
    "target_domain": "upc",
    "callback_url": "http://rtr-api:8000/update_action_status",
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
    "info": "awaiting enforcement"
}

# Example 2: Multi-domain action with callback
CALLBACK_MULTI_DOMAIN = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "multi-domain-callback-001",
    "target_domain": ["upc", "umu"],
    "callback_url": "http://rtr-api:8000/update_action_status",
    "action": {
        "name": "router_rate_limiting",
        "intent_id": "router-limit-001",
        "fields": {
            "device": "router-1",
            "rate": "100mbps",
            "duration": "600"
        }
    },
    "status": "pending",
    "info": "awaiting enforcement"
}

# Example 3: Block IP addresses with callback
CALLBACK_BLOCK_IPS = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "block-ips-callback-001",
    "target_domain": "upc",
    "callback_url": "http://rtr-api:8000/update_action_status",
    "action": {
        "name": "block_ip_addresses",
        "intent_id": "block-ips-action-001",
        "fields": {
            "blocked_ips": ["192.168.1.100", "192.168.1.101", "10.0.0.50"]
        }
    },
    "status": "pending",
    "info": "awaiting enforcement"
}

# Example 4: UMU testbed specific action with callback
CALLBACK_UMU_RATE_LIMITING = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "umu-rate-limit-callback-001",
    "target_domain": "umu",
    "callback_url": "http://rtr-api:8000/update_action_status",
    "action": {
        "name": "rate_limiting",
        "intent_id": "rate-limit-action-001",
        "fields": {
            "device": "firewall-1",
            "interface": "eth0",
            "rate": "50mbps"
        }
    },
    "status": "pending",
    "info": "awaiting enforcement"
}

# Example 5: Action without callback (backward compatible)
NO_CALLBACK_DNS_LIMIT = {
    "command": "add",
    "intent_type": "mitigation",
    "intent_id": "dns-limit-no-callback-001",
    "target_domain": "upc",
    # callback_url is optional - omitting it means no callback will be sent
    "action": {
        "name": "dns_rate_limiting",
        "intent_id": "dns-limit-action-002",
        "fields": {
            "rate": "200",
            "duration": "300",
            "source_ip_filter": ["192.168.2.100"]
        }
    },
    "status": "pending",
    "info": "awaiting enforcement"
}


"""
Expected callback payloads that DOC will send to the RTR API:
"""

# Callback for successful single-domain action
EXPECTED_CALLBACK_SUCCESS = {
    "intent_id": "dns-limit-callback-001",
    "status": "completed",
    "info": "Action successfully enforced in UPC testbed"
}

# Callback for failed single-domain action
EXPECTED_CALLBACK_FAILURE = {
    "intent_id": "dns-limit-callback-001",
    "status": "failed",
    "info": "Action failed in UPC testbed: Connection timeout"
}

# Callback for successful multi-domain action
EXPECTED_CALLBACK_MULTI_SUCCESS = {
    "intent_id": "multi-domain-callback-001",
    "status": "completed",
    "info": "Multi-domain execution: 2/2 successful | ✓ Action enforced in UPC testbed | ✓ Action enforced in UMU testbed"
}

# Callback for partial multi-domain action
EXPECTED_CALLBACK_MULTI_PARTIAL = {
    "intent_id": "multi-domain-callback-001",
    "status": "partial",
    "info": "Multi-domain execution: 1/2 successful | ✓ Action enforced in UPC testbed | ✗ Action failed in UMU testbed: Testbed unreachable"
}

# Callback for completely failed multi-domain action
EXPECTED_CALLBACK_MULTI_FAILED = {
    "intent_id": "multi-domain-callback-001",
    "status": "failed",
    "info": "Multi-domain execution: 0/2 successful | ✗ Action failed in UPC testbed: Connection refused | ✗ Action failed in UMU testbed: Timeout"
}
