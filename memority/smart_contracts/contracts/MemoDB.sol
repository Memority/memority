pragma solidity ^0.4.16;

contract owned {
    address public owner;
    function owned() public {owner = msg.sender;}
    modifier onlyOwner { require(msg.sender == owner); _;}
    function transferOwnership(address newOwner) onlyOwner public {owner = newOwner;}
}

contract MemoDB is owned{

    struct host {
        address hostAddress;
        bytes32 ip;
        uint power;
        bool active;
    }

    struct transaction {
        address from;
        address to;
        bytes32 file;
        uint256 date;
        uint256 value;
    }

    mapping (address => bytes32[]) public transactionsId;
    mapping (bytes32 => transaction) public transactions;
    mapping (address => host) public hostInfo;
    mapping (address => address) public clientContract;
    address tokenAddress;
    address[] public hostList;

    event HostAdded(address from);

    function MemoDB(address _tokenAddress) public {
        tokenAddress = _tokenAddress;
    }

    modifier onlyToken {
        require(msg.sender == tokenAddress);
        _;
    }

    function changeToken(address _token) onlyOwner public {
        tokenAddress = _token;
    }

    function logTransaction(address _from, address _to, bytes32 _file, uint256 _value) external {

        bytes32 unique = keccak256(now, _from, _to);

        transactionsId[_to].push(unique);

        transactions[unique].from = _from;
        transactions[unique].to = _to;
        transactions[unique].file = _file;
        transactions[unique].date = now;
        transactions[unique].value = _value;

        if(_from != address(0)){
            transactionsId[_from].push(unique);
        }
    }

    function transactionsCount(address _address) public returns (uint256) {
        return transactionsId[_address].length;
    }

    function updateHost(bytes32 ip) public {

        require(! hostInfo[msg.sender].active || hostInfo[msg.sender].ip != ip);
        //require(balanceOf[msg.sender] >= minTokenForHost);

        if( ! hostInfo[msg.sender].active){
            hostList.push(msg.sender);

            hostInfo[msg.sender].active = true;
            hostInfo[msg.sender].hostAddress = msg.sender;
            hostInfo[msg.sender].power = 1;
        }

        hostInfo[msg.sender].ip = ip;

        HostAdded(msg.sender);
    }

    function getHosts() view public returns (address[]) {
        return hostList;
    }

    function getHostIp(address hostAddress) view public returns (bytes32) {
        require( hostInfo[hostAddress].active );
        return hostInfo[hostAddress].ip;
    }

    function newClient(address owner) public {
        //Client client = Client(msg.sender);
        //address owner = client.owner();

        if(clientContract[owner] != address(0)){
            // todo: merge data from old client contract?
        }

        clientContract[owner] = msg.sender;
    }
}
