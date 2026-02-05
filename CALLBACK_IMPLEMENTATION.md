# Callback Feature Implementation Summary

## Overview
This document summarizes the implementation of the callback feature that enables DOC to send status updates back to the RTR API after mitigation actions are enforced.

## Changes Made

### 1. Model Updates
**File:** `src/model/MitigationActionRequest.py`
- Added `callback_url` field (optional) to store the RTR endpoint URL
- Updated example payload to demonstrate callback_url usage
- Maintains backward compatibility - callback_url is optional

### 2. Callback Utility
**File:** `src/utils/callback.py` (NEW)
- Created `send_status_update()` async function
- Handles HTTP POST to RTR's `/update_action_status` endpoint
- Includes error handling and logging
- Implements 10-second timeout for callback requests
- Returns boolean success/failure status

### 3. Dispatch Function Updates
**File:** `src/dispatch/http.py`
- Modified `dispatch()` to return tuple: `(response_data, status_code, success_flag)`
- Updated CNIT passthrough to return status information
- Changed error handling to return status data instead of raising exceptions immediately
- Maintains backward compatibility for existing code

### 4. Main API Updates
**File:** `src/main.py`
- Added import for `send_status_update` from callback utility
- **Single-domain flow:**
  - Unpacks dispatch response tuple
  - Sends callback with testbed-specific success/failure info
  - Handles exceptions with appropriate callback notifications
- **Multi-domain flow:**
  - Collects results from all domains
  - Sends aggregated callback with detailed per-domain status
  - Includes success count and domain-specific messages
- **Forwarding flow:**
  - callback_url is automatically passed to remote DOC instances
  - Remote DOC handles the callback (no changes needed)

### 5. Documentation
**File:** `README.md`
- Added "Status Callback Feature" section with:
  - How the feature works
  - Request format examples
  - Callback payload format
  - Status values explanation
  - Implementation notes
  - Example RTR endpoint integration code

### 6. Test Examples
**File:** `tests/example_callbacks.py` (NEW)
- Example payloads with callback_url
- Expected callback responses for various scenarios:
  - Single-domain success
  - Single-domain failure
  - Multi-domain success
  - Multi-domain partial success
  - Multi-domain complete failure
- Example without callback (backward compatibility)

## How It Works

### Flow Diagram
```
RTR API → DOC → Infrastructure (testbed)
                    ↓
                 (result)
                    ↓
            callback sent
                    ↓
RTR API ← status update
```

### Request Example
```json
{
  "intent_id": "dns-limit-001",
  "target_domain": "upc",
  "callback_url": "http://rtr-api:8000/update_action_status",
  "action": {
    "name": "dns_rate_limiting",
    "intent_id": "dns-limit-action-001",
    "fields": {
      "rate": "100",
      "duration": "300",
      "source_ip_filter": ["192.168.1.100"]
    }
  }
}
```

### Callback Payload
```json
{
  "intent_id": "dns-limit-001",
  "status": "completed",
  "info": "Action successfully enforced in UPC testbed"
}
```

## Status Values

| Status | Description |
|--------|-------------|
| `completed` | Action successfully enforced in all target testbeds |
| `failed` | Action failed in all target testbeds |
| `partial` | Some testbeds succeeded, others failed (multi-domain only) |

## Key Features

1. **Optional Field**: `callback_url` is optional - maintains backward compatibility
2. **Asynchronous**: Callbacks don't block the main response
3. **Detailed Info**: Includes testbed name and specific error messages
4. **Multi-domain Support**: Aggregates results from multiple domains
5. **Error Resilient**: Logs callback failures but doesn't affect mitigation
6. **Fire-and-Forget**: Callback failures don't impact the mitigation action
7. **Timeout Protection**: 10-second timeout prevents hanging

## Testing Recommendations

1. Test single-domain success scenario
2. Test single-domain failure scenario (unreachable testbed)
3. Test multi-domain with all successes
4. Test multi-domain with partial failures
5. Test multi-domain with all failures
6. Test without callback_url (backward compatibility)
7. Test with unreachable callback endpoint
8. Test callback timeout scenario

## Backward Compatibility

- All changes are additive
- Existing payloads without `callback_url` work unchanged
- Dispatch function changes don't break existing exception handling
- No breaking changes to existing APIs or contracts

## Future Enhancements

Potential improvements for future versions:
- Configurable callback timeout
- Retry mechanism for failed callbacks
- Callback authentication/authorization
- Webhook signature verification
- Callback queuing for high-volume scenarios
- Callback status tracking and monitoring
