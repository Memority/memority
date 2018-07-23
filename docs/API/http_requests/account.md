# Account

## Generate address
**Request:**

`POST /account/generate_address/`
```json
{
  "password": "<str>"
}
```
**Response:**
```json
{
  "status": "success",
  "result": "<str>address"
}
```

## Create renter account
**Request:**

`POST /account/create/`
```json
{}
```
**Response:**
```json
{
  "status": "success",
  "result": "<str>client_contract.address"
}
```

## Import from file
**Request:**

`POST /account/import/`
```json
{
  "filename": "/path/to/account/file.bin",
  "password": "password to account being imported"
}
```
**Response:**
```json
{
  "status": "success",
  "result": "ok"
}
```

## Export to file
**Request:**

`POST /account/export/`
```json
{
  "filename": "/path/where/to/import/account/file.bin"
}
```
**Response:**
```json
{
  "status": "success",
  "result": "ok"
}
```

## Request MMR tokens for testing
**Request:**

`POST /account/request_mmr/`
```json
{
  "key": "alpha tester key"
}
```
**Response:**
```json
{
  "status": "success",
  "result": 50.0  //balance, int
}
```
