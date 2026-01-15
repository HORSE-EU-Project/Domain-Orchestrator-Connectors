# 🧩 Domain-Orchestrator-Connector

**Domain-Orchestrator-Connector** is a **modular**, **containerized** FastAPI-based system designed to translate and forward mitigation actions to multiple 5G/6G security testbeds, such as **UMU** and **UPC**. It acts as a middleware that unifies the communication format and logic across heterogeneous orchestrator APIs.

---

## ⚙️ Architecture

This system adopts a clean **modular architecture** with the following components:

- **API Layer (FastAPI)**: Receives high-level mitigation commands in JSON format.
- **Testbed Translators**: Convert commands to testbed-specific formats (e.g., XML or JSON).
- **Execution Handlers**: Send the translated actions to the appropriate testbed interfaces.
- **Persistence Layer (MongoDB)**: Logs each action and tracks intent IDs.
- **Dockerized Deployment**: Managed using `docker-compose` for reproducibility and scalability.

---

## 🌐 Multi-Domain Support

The Domain-Orchestrator-Connector (DOC) supports **multi-domain deployments**, enabling mitigation actions to be enforced across distributed 5G/6G network domains. This is achieved by deploying separate DOC instances in each domain, with each instance aware of its domain identity and the locations of other DOC instances.

### How It Works

When a mitigation action arrives at a DOC instance:

1. **Domain Check**: The DOC examines whether the action is targeted for its own domain or a different domain
2. **Local Enforcement**: If the action targets the current domain, the DOC translates the action using the communication protocol configured for the local infrastructure and enforces the mitigation/prevention action directly
3. **Cross-Domain Forwarding**: If the action targets another domain, the DOC propagates the mitigation/prevention action to the DOC instance deployed in that target domain, which then handles enforcement using its local infrastructure protocol

### Configuration Prerequisite

For multi-domain functionality to work correctly, **you must configure the domain identity** in the configuration file:

**File:** `./config/config.yaml`

```yaml
domain_routing:
  current_domain: upc  # Options: upc, umu, cnit
  doc_instances:
    upc: "http://10.19.2.19:8001"  # URL of DOC deployed in UPC domain
    umu: "http://10.208.11.70:8001"  # URL of DOC deployed in UMU domain
    cnit: "http://192.168.130.62:8001"  # URL of DOC deployed in CNIT domain
```

- Set `current_domain` to match the domain where this DOC instance is deployed
- Ensure all DOC instances have the correct URLs configured for cross-domain communication
- Each domain can use different communication protocols (XML, JSON, etc.) as defined in the testbed configurations

This architecture enables seamless orchestration of security mitigations across federated network infrastructures while respecting the autonomy and protocols of each domain.

---

## 🚀 Quick Start

To run the system locally:

```bash
docker-compose up --build
```

The API documentation will be available at: http://localhost:8000/docs

---

## 🛠️ API Endpoints

The Domain-Orchestrator-Connector provides three main endpoints:

### 1. **POST `/api/mitigate`** - Core Mitigation Endpoint
This is the main business logic endpoint for processing mitigation actions across different testbeds.

**Functionality:**
- Accepts mitigation action requests in a unified JSON format
- Persists requests to MongoDB for auditing and traceability
- Translates and forwards requests to the appropriate testbed (UMU or UPC)
- Returns structured responses with upstream testbed replies
- Handles errors gracefully with appropriate HTTP status codes

**Error Handling:**
- Returns HTTP 502 (Bad Gateway) for testbed communication errors
- Returns HTTP 500 (Internal Server Error) for general application errors
- Returns HTTP 422 (Unprocessable Entity) for validation errors with detailed messages

### 2. **GET `/ping`** - Health Check
Simple health check endpoint to verify service availability.

**Response:**
```json
{
  "status": "ok"
}
```

**Use Cases:**
- Service health monitoring
- Load balancer health checks
- Container orchestration health probes

### 3. **GET `/reload_config`** - Configuration Management
Dynamically reloads the YAML configuration file without service restart.

**Functionality:**
- Refreshes testbed configurations
- Updates action schemas and mappings
- Allows runtime configuration changes

**Use Cases:**
- Adding new testbed configurations
- Updating action definitions
- Modifying system settings without downtime

---

## 📥 API Input
All mitigation actions are sent to the unified endpoint /api/mitigate in the following format:

```bash
{
  "testbed": "umu",
  "action": "rate_limit",
  "intent_id": "limit-dns-42",
  "fields": {
    "ip": "192.168.1.100",
    "rate": "10req/s"
  }
}

```


| Field       | Type   | Description                              |
| ----------- | ------ | ---------------------------------------- |
| `testbed`   | string | Target testbed (`"umu"` or `"upc"`)      |
| `action`    | string | Name of the mitigation action            |
| `intent_id` | string | Unique ID for traceability and debugging |
| `fields`    | object | Action-specific parameters               |


## 📤 API Output

### Successful Response
Standard response structure for successful mitigation actions:
```json
{
  "status": "success",
  "testbed": "umu",
  "intent_id": "limit-dns-42",
  "message": "Action forwarded for processing.",
  "upstream": {
    // Testbed-specific response data
  }
}
```

### Error Responses

#### Validation Errors (HTTP 422)
For missing or invalid request fields:
```json
{
  "status": "error",
  "intent_id": "limit-dns-42",
  "message": "Missing field 'ip' for action 'rate_limit'."
}
```

#### Testbed Communication Errors (HTTP 502)
When the upstream testbed is unreachable or returns an error:
```json
{
  "status": "error",
  "intent_id": "limit-dns-42", 
  "message": "Failed to communicate with testbed"
}
```

#### Internal Server Errors (HTTP 500)
For unexpected application errors:
```json
{
  "status": "error",
  "intent_id": "limit-dns-42",
  "message": "Internal server error occurred"
}
```

### Health Check Response
```json
{
  "status": "ok"
}
```


## 🧪 Supported Testbeds
### UMU Testbed
Accepts XML (MSPL) payloads via HTTP POST/DELETE

Stateless interface; requires unique policy IDs

Demonstrates use of system model, policy interpreter, and device drivers

### UPC Testbed
Accepts JSON payloads via HTTP POST

Exposes one endpoint per mitigation action

JWT authentication planned but not currently enforced

### 📁 Additional Resources
More information, including message formats, endpoint mappings, and sample payloads, can be found in the following folders:

sample_mitigation_actions/ – JSON and XML examples

UMU_testbed/ – XML schema and communication logic

UPC_testbed/ – JSON API endpoint definitions and usage

### 🧱 Extending the Project
Add support for new testbeds by implementing translation and communication logic in a new module.

Define new actions by registering them in the existing action map.

Integrate easily into larger workflows (e.g., threat detection platforms, SOC dashboards).