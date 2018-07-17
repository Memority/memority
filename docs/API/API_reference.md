# API reference
By default, Memority listen on: 
- port `9379` on `127.0.0.1` for communicating with GUI, CLI and third-party developer apps.
- port `9378` on `0.0.0.0` for communicating with renters and other hosts
- port `30320` for `geth` node

## Standard response format:
```
{
  "status": "{success|error|info}",
  "data": {...},  // if success
  "message": "str"  // error message or info message, according to status
}
```

## Checks
Before communicating with Memority Core, you must perform some checks.

### Blockchain synchronization status

#### Request:
`GET /checks/sync_status/`
#### Response:
```
{
  "status": "success",
  "data": {
    "result": {
      "syncing": {true|false},
      "percent": int  // -1 if sync hasn't started yet
    }
  }
}
```

### App update availability

#### Request:
`GET /checks/app_updates/`
#### Response:
```
{
  "status": "success",
  "data": {
    "result": {
      "update_available": {true|false},
      "download_url": "str: url for latest app version for current platform"
    }
  }
}
```

### Smart contract update availability

#### Request:
`GET /checks/contract_updates/`
#### Response:
```
{
  "status": "success",
  "data": {
    "result": {true|false}
  }
}
```

## Account

### Create
### Import

#### Request:
`POST /account/import/`
#### POST data:
```
{
  "filename": "path to a file with account to import",
  "password": "password to account being imported"
}
```
#### Response:
```
{
  "status": "{success|error}",
  "data": {  // if success
    "result": "ok"
  },
  "message": "str"  // if error
}
```

### Export

#### Request:
`POST /account/export/`
#### POST data:
```
{
  "filename": "path where to save exported account",
}
```
#### Response:
```
{
  "status": "{success|error}",
  "data": {  // if success
    "result": "ok"
  },
  "message": "str"  // if error
}
```

### Update smart contract to new version
