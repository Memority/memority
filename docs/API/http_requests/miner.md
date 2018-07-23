# Miner

## Get miner ip
**Request:**

`POST /miner/ip/`
```json
{}
```
**Response:**
```json
{
   "status" : "success",
   "result" : "ip:port"
}
```

## Get sum of rewards for mining
**Request:**

`POST /miner/rewards/`
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

## Send request for adding you to miners
You must have a white IP address and open port `30320` and minimum 10000 MMR on your balance.

**Request:**

`POST /miner/request/`
```json
{}
```
**Response:**
```json
{
  "result" : "<str> request status",
  "status" : "success"
}
```
