# Checks
Before communicating with Memority Core, you must perform some checks.

## Blockchain synchronization status

**Request:**

`POST /checks/sync_status/`
```json
{}
```
**Response:**
```json
{
  "status": "success",
  "result": {
    "syncing": "<bool> {true|false}",
    "percent": "<int>"  // -1 if sync hasn't started yet
  }
}
```

## App update availability

**Request:**

`POST /checks/app_updates/`
```json
{}
```
**Response:**
```json
{
  "status": "success",
  "result": {
    "update_available": "<bool>{true|false}",
    "download_url": "<str>: url for latest app version for current platform"
  }
}
```

## Smart contract update availability

**Request:**

`POST /checks/contract_updates/`
```json
{}
```
**Response:**
```json
{
  "status": "success",
  "result": "<bool>{true|false}"
}
```
If result is `true`, you must update contract by calling `update_contract` 
(more details [here](../websocket_requests/update_contract.md))
