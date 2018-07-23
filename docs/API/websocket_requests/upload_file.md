# Upload file

**Request:**

`Send websocket message to /ws/`
```json
{
    "command": "upload",
    "kwargs": {
        "path": "/path/to/a/file"
    }
}
```

During the upload process, status messages will be sent back to websocket:
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
  "details": "uploaded",
  "result": {
    "file": {
      "deposit_ends_on": "YYYY-MM-DD HH:MM UTC",
      "hash": "<str>",
      "id": "1",
      "name": "<str> filename",
      "price_per_hour": "<float> The cost of one hour of file storage",
      "size": "<int>",
      "status": "uploaded",
      "timestamp": "YYYY-MM-DD HH:MM UTC"
    }
  }
}
```
