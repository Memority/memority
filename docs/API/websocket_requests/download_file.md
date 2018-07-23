# Download file

**Request:**

`Send websocket message to /ws/`
```json
{
  "command": "download",
  "kwargs": {
    "file_hash": "hash of a file",
    "destination": "/path/to/destination/dir"
  }
}
```

During the download process, status messages will be sent back to websocket:
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
  "details": "downloaded",
  "result": {
    "file": {
      "name": "/path/to/downloaded/file"
    }
  }
}
```
