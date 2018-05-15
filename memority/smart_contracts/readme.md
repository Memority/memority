# Enveiroment setup
```
apt-get install build-essential python   
npm install ganache-cli web3@0.20.2
npm install solc

# start dev nodes
node_modules/.bin/ganache-cli   
```
# web3 console  
```
node
> Web3 = require('web3')
> web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));

// node info
> web3.eth.accounts  

// Compile the cottract
> code = fs.readFileSync('Voting.sol').toString()
> solc = require('solc')
> compiledCode = solc.compile(code) 

// Deploy the contract 
> abiDefinition = JSON.parse(compiledCode.contracts[':Voting'].interface)
> VotingContract = web3.eth.contract(abiDefinition)
> byteCode = compiledCode.contracts[':Voting'].bytecode
> deployedContract = VotingContract.new(['Rama','Nick','Jose'],{data: byteCode, from: web3.eth.accounts[0], gas: 4700000})
> deployedContract.address

// Interact with the contract
> contractInstance = VotingContract.at(deployedContract.address)
> contractInstance.totalVotesFor.call('Rama')
> contractInstance.voteForCandidate('Rama', {from: web3.eth.accounts[0]})
> contractInstance.totalVotesFor.call('Rama').toLocaleString()

```

# Truffle
### install
npm install -g truffle   
npm install -g webpack   
truffle unbox webpack
```
truffle migrate
```  

# Token notes
```
Once you have created a token contract you should ask for it to be added to common sites such as Etherscan, MyEtherWallet and CoinMarketCap, although be sure to follow the instructions at the links provided for your best chance of the submission being accepted.
```

