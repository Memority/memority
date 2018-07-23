# Files

## Get file list
**Request:**

`POST /files/list/`
```json
{}
```
**Response:**
```json
{
  "status": "success",
  "result": [
    {
      "deposit_ends_on": "YYYY-MM-DD HH:MM UTC",
      "hash": "<str>",
      "id": "1",
      "name": "<str> filename",
      "price_per_hour": "<float> The cost of one hour of file storage",
      "size": "<int>",
      "status": "uploaded",
      "timestamp": "YYYY-MM-DD HH:MM UTC"
    }
  ]
}
```

## Get file info
**Request:**

`POST /files/info/`
```json
{
  "file_hash": "<str>"
}
```
**Response:**
```json
{
  "result": {
    "deposit_ends_on": "YYYY-MM-DD HH:MM UTC",
    "hash": "<str>",
    "id": "1",
    "name": "<str> filename",
    "price_per_hour": "<float> The cost of one hour of file storage",
    "size": "<int>",
    "status": "uploaded",
    "timestamp": "YYYY-MM-DD HH:MM UTC"
  },
  "status": "success"
}

```

## Prolong deposit for a file
Takes some time because of waiting for transaction to complete.

**Request:**

`POST /files/prolong_deposit/`
```json
{
  "file_hash": "<str>", 
  "value": "<float>: in MMR"
}
```
**Response:**
```json
{
  "status": "success",
  "result": "ok"
}
```
