# User

## Get user address
**Request:**

`POST /user/address/`
```json
{}
```
**Response:**
```json
{
   "result" : "<str>address",
   "status" : "success"
}
```

## Get user role
**Request:**

`POST /user/role/`
```json
{}
```
**Response:**
```json
{
   "result" : [
      "host",  // if in host list
      "renter",  // if client contract created
      "miner"  // if in miner list
   ],
   "status" : "success"
}

```

## Get user transactions
**Request:**

`POST /user/transactions/`
```json
{}
```
**Response:**
```json
{
  "status": "success",
  "result": [
    {
      "comment": "file hash or 'developer_reward' or 'miner_reward'",
      "date": "YYYY-MM-DD HH:MM:SS",
      "to": "null or address",
      "from": "null or address",
      "value": "<float> MMR"
    }
  ]
}
```

## Get user balance
**Request:**

`POST /user/balance/`
```json
{}
```
**Response:**
```json
{
   "status" : "success",
   "result" : "<float> MMR"
}

```
