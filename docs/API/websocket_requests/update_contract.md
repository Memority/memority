# Update client contract

**Request:**

`Send websocket message to /ws/`
```json
{
  "command": "update_client_contract"
}
```

During the updating process, status messages will be sent back to websocket:
```json
{
  "status": "info",
  "message": "log message"
}
```

**Response:**

```json
{
  "status": "success",
  "details": "client_contract_updated"
}
```
