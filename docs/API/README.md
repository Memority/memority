# API reference
By default, Memority listen on: 
- port `9379` on `127.0.0.1` for communicating with GUI, CLI and third-party developer apps.
- port `9378` on `0.0.0.0` for communicating with renters and other hosts
- port `30320` for `geth` node

Most operations are performed through HTTP requests.
Long-running operations - 
[uploading](websocket_requests/upload_file.md) /
[downloading](websocket_requests/download_file.md) a file, 
[upgrading client contract](websocket_requests/update_contract.md) - are performed via websockets 
because of ability to send status messages in the process.

## Standard HTTP response format:
```json
{
  "status": "{success|error|info}",
  "result": "{...}",  // if success
  "message": "str"  // error message or info message, according to status
}
```
## [Checks](http_requests/checks.md)
Before communicating with Memority Core, you must perform some checks.

## [Account](http_requests/account.md)

## [File](http_requests/files.md)

## [Host](http_requests/host.md)

## [Miner](http_requests/miner.md)

## [User](http_requests/user.md)
