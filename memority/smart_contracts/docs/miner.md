# Miner Logic
### Became miner  

1. Submit request - POST https://api.memority.io/api/app/miner/request  
User must be registered and KYC completed.     

2. All active miners must sync "signers" list.  
2.1. GET "http://api.memority.io/api/app/miners"  
receive miners with true | false status. true - vote for; false - vote off   
2.2. get local active miners    
```web3.manager.request_blocking("clique_getSigners", [])  ```   
2.3. compare two lists and vote for or off.    
```web3.manager.request_blocking("clique_propose", ['0x234adsf...', true|false]) ```    

3. Before start mining, miner must check if his address in "clique_getSigners" (2.2.) if ok and when request status (1.) return "active" status:   
3.1. submit miner enode - POST https://api.memority.io/api/api/app/enode    
3.2. unlock account   
3.3. ```web3.miner.start()   ```   
can be done with run command: 
```geth ... --unlock $ADDRESS --password $NODE_DIR/password.txt --mine```   

### Miner updates  

1. All users and miners need to sync enode lists with static-nodes.json     
GET "http://api.memority.io/api/app/enodes"     

to add new node at runtime:  
```web3.admin.addPeer("enode://f4642fa65af50cfdea8fa741....6fbaf6416c0@33.4.2.1:30303")```   
