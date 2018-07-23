# Host

## Get host IP with port
**Request:**

`POST /host/ip/`
```json
{}
```
**Response:**
```json
{
  "result" : "ip:port",  // null if not a hoster
  "status" : "success"
}
```

## Get storage info
**Request:**

`POST /host/storage/`
```json
{}
```
**Response:**
```json
{
  "status" : "success",
  "result" : {
    "used" : "<int>, bytes",
    "total" : "<int>, bytes"
  }
}
```

## Get sum of rewards for hosting
**Request:**

`POST /host/rewards/`
```json
{}
```
**Response:**
```json
{
  "result" : "<int>, MMR",
  "status" : "success"
}
```

## Become a hoster
You must have a white IP address and open port `9378`.

**Request:**

`POST /host/start/`
```json
{}
```
**Response:**
```json
{
  "result" : "ip:port",
  "status" : "success"
}
```

## Set storage size
**Request:**

`POST /host/storage/resize/`
```json
{
  "disk_space": "<int>"  // GB
}
```
**Response:**
```json
{
  "result" : "ok",
  "status" : "success"
}
```

## Set storage path
**Request:**

`POST /host/storage/set_path/`
```json
{
  "path": "/path/to/storage/dir/"
}
```
**Response:**
```json
{
  "result" : "ok",
  "status" : "success"
}
```
