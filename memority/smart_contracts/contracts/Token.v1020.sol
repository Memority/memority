pragma solidity 0.4.24;

contract Client {
    address public owner;
    //function getOfflineVoters(bytes32 _hash, address _address) view public returns (address[]){}
    function getFileSize(bytes32 _hash) view public returns (uint256){}
    function getFileDeveloper(bytes32 _hash) view public returns (address){}
}

contract MemoDB {
    address tokenAddress;
    mapping (address => address) public clientContract;
    modifier onlyToken {require(msg.sender == tokenAddress);_;}
    function logTransaction(address _from, address _to, bytes32 _file, uint256 _value) external {}
    function updateHost(bytes32 ip) public {}
}

contract owned {
    address public owner;
    function owned() public {owner = msg.sender;}
    modifier onlyOwner { require(msg.sender == owner); _;}
    function transferOwnership(address newOwner) onlyOwner public {owner = newOwner;}
}

//interface tokenRecipient { function receiveApproval(address _from, uint256 _value, address _token, bytes _extraData) public; }

contract UtilsAPI {
    /*
     *  Abstract contract for interfacing with the DateTime contract.
     *
     */
    function isLeapYear(uint16 year) constant returns (bool);
    function getYear(uint timestamp) constant returns (uint16);
    function getMonth(uint timestamp) constant returns (uint8);
    function getDay(uint timestamp) constant returns (uint8);
    function getHour(uint timestamp) constant returns (uint8);
    function getMinute(uint timestamp) constant returns (uint8);
    function getSecond(uint timestamp) constant returns (uint8);
    function getWeekday(uint timestamp) constant returns (uint8);
    function toTimestamp(uint16 year, uint8 month, uint8 day) constant returns (uint timestamp);
    function toTimestamp(uint16 year, uint8 month, uint8 day, uint8 hour) constant returns (uint timestamp);
    function toTimestamp(uint16 year, uint8 month, uint8 day, uint8 hour, uint8 minute) constant returns (uint timestamp);
    function toTimestamp(uint16 year, uint8 month, uint8 day, uint8 hour, uint8 minute, uint8 second) constant returns (uint timestamp);
}

contract TokenERC20 {
    string public name;
    string public symbol;
    uint8 public decimals = 18;
    uint256 public totalSupply;
    uint256 public tokenForSale;
    uint256 public tokenPrice;
    address public utilsAddress = 0xdDd5Af3278e8954159614b683e0B46d27B47e77e;

    mapping (address => bool) public holdersMap;
    mapping (address => uint256) public balanceOf;
    address[] public holdersList;

    event Transfer(address indexed from, address indexed to, uint256 value);
    //event Burn(address indexed from, uint256 value);

    /**
     * Constrctor function
     * Initializes contract with initial supply tokens to the creator of the contract
     */
    function TokenERC20(
        uint256 initialSupply,
        uint256 _tokenPrice,
        string tokenName,
        string tokenSymbol
    ) public {
        tokenPrice = _tokenPrice / 10 ** uint256(decimals);
        totalSupply = initialSupply * 10 ** uint256(decimals);
        tokenForSale = totalSupply;
        name = tokenName;
        symbol = tokenSymbol;
    }

    /**
     * Internal transfer, only can be called by this contract
     */

    function _transfer(address _from, address _to, uint _value) internal {
        // Prevent transfer to 0x0 address. Use burn() instead
        require(_to != 0x0);
        require(balanceOf[_from] >= _value);
        require(balanceOf[_to] + _value > balanceOf[_to]);
        uint previousBalances = balanceOf[_from] + balanceOf[_to];
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        addToHolderList(_to);
        Transfer(_from, _to, _value);
        // Asserts are used to use static analysis to find bugs in your code. They should never fail
        assert(balanceOf[_from] + balanceOf[_to] == previousBalances);
    }

    /**
     * Transfer tokens
     * Send `_value` tokens to `_to` from your account
     * @param _to The address of the recipient
     * @param _value the amount to send
     */
    function transfer(address _to, uint256 _value) public {
        _transfer(msg.sender, _to, _value);
    }

    function addToHolderList(address _address) internal {
        if( ! holdersMap[_address] ){
            holdersMap[_address] = true;
            holdersList.push(_address);
        }
    }
}


contract Token is owned, TokenERC20 {

    //uint256 paymentInterval = 60 * 60 * 24 * 14;    // 2 week
    uint256 public paymentInterval = 60;    // 1 min
    uint256 public tokensPerByteHour = 50;    // 0.000 000 000 5 MMR per byte/hour
    uint256 public minTokenForHost = 1000000000000;    // 1 MMR
    bool public payoutsFrozen = false;
    uint256 public holdersToken;
    uint256 public minHoldersBalance = 100 * 10 ** 12;
    uint256 etherPerUser = 5000000000000000000;
    address public dbAddress;
    uint256 public version = 1020;

    mapping (address => mapping (bytes32 => uint256)) public deposits;
    mapping (bytes32 => mapping (uint256 => uint256)) public depositPrice;
    mapping (bytes32 => mapping (address => uint)) public payouts;
    mapping (uint16 => mapping (uint8 => mapping (uint8 => uint256))) public minersRewards;

    function Token(
        uint256 initialSupply,
        uint256 _tokenPrice,
        string tokenName,
        string tokenSymbol
    ) TokenERC20(initialSupply, _tokenPrice, tokenName, tokenSymbol) public {}

    function setPrices(uint256 _tokenPrice) onlyOwner public {
        tokenPrice = _tokenPrice;
    }

    function setDbAddress(address _address) onlyOwner public {
        dbAddress = _address;
    }

    function updateMinForHost(uint256 _value) onlyOwner public {
        minTokenForHost = _value;
    }

    function enroll(address _address, uint256 _value) onlyOwner public {
        require(tokenForSale >= _value);
        balanceOf[_address] += _value;
        tokenForSale -= _value;
        addToHolderList(_address);
        logTransaction(address(0), _address, 'enroll', _value);
        if(_address.balance < etherPerUser){
            _address.transfer(etherPerUser - _address.balance);
        }
        Transfer(address(0), _address, _value);
    }

    function() payable public{

    }

    function refill() public {
        require(msg.sender.balance < etherPerUser);
        msg.sender.transfer(etherPerUser - msg.sender.balance);
    }

    function freezePayouts(bool freeze) onlyOwner public {
        payoutsFrozen = freeze;
    }

    function updateHost(bytes32 ip) public {

        //require(! hostInfo[msg.sender].active || hostInfo[msg.sender].ip != ip);
        require(balanceOf[msg.sender] >= minTokenForHost);

        MemoDB db = MemoDB(dbAddress);
        db.updateHost(ip);
    }

    function depositForFile(uint256 _value, bytes32 _hash) public returns (bool success) {
        Client client = Client(msg.sender);
        address owner = client.owner();

        require(balanceOf[owner] >= _value);

        balanceOf[owner] -= _value;
        deposits[owner][_hash] += _value;
        // todo: diff deposits prices
        depositPrice[_hash][tokensPerByteHour] = _value;

        logTransaction(owner, address(0), _hash, _value);
        Transfer(owner, address(0), _value);

        return true;
    }


//    function deleteDeposit(bytes32 _hash) public returns (bool success) {
//        Client client = Client(msg.sender);
//        address owner = client.owner();
//
//        require(deposits[owner][_hash] > 0);
//
//        uint256 value = deposits[owner][_hash];
//        balanceOf[owner] += value;
//        deposits[owner][_hash] = 0;
//
//        logTransaction(address(0), owner, _hash, value);
//        Transfer(address(0), owner, value);
//
//        return true;
//    }

    function timeToPay(bytes32 _hash) view public returns (bool success) {
        address _address = msg.sender;
        if(payouts[_hash][_address] == 0){
            return false;
        }
        return now - payouts[_hash][_address] > paymentInterval;
    }

    function preparePayout(address _addresses, bytes32 _hash) public returns (bool success) {
        payouts[_hash][_addresses] = now;
        return true;
    }

    function preparePayouts(address[] _addresses, bytes32 _hash) public returns (bool success) {
        //todo: make deposit first?
        for (uint i = 0; i < _addresses.length; i++) {
            payouts[_hash][_addresses[i]] = now;
        }
        return true;
    }

    function setHoldersMinBalance(uint256 _tokens_wei) onlyOwner public {
        minHoldersBalance = _tokens_wei;
    }

    function setReward(uint256 _reward) onlyOwner public {
        tokensPerByteHour = _reward;
    }

    // total reward for file in mmr wei
    function calculateMmr(uint256 _secs, uint256 _size_bytes) internal returns (uint256) {
        return  ( _secs / 60 / 60 )  * _size_bytes * tokensPerByteHour;
    }

    function logTransaction(address _from, address _to, bytes32 _file, uint256 _value) internal {

        MemoDB db = MemoDB(dbAddress);
        db.logTransaction(_from, _to, _file, _value);
    }

    // called by Client contract
    function replacePayout(address _address_from, address _address_to, bytes32 _hash, address[] voters) public returns (bool) {
        //todo: sec check
        Client client = Client(msg.sender);
        address owner = client.owner();
        uint256 size = client.getFileSize(_hash);
        uint256 secs = now - payouts[_hash][_address_from];
        uint256 penalty = calculateMmr(secs, size);

        payouts[_hash][_address_to] = now;
        delete payouts[_hash][_address_from];

//        Client client = Client(msg.sender);
//        address[] voters = client.getOfflineVoters(_hash, _address_from);
        uint256 reward = penalty / voters.length;
        for (uint i = 0; i < voters.length; i++) {
            balanceOf[voters[i]] += reward;
            deposits[owner][_hash] -= reward;
        }

        return true;
    }

    function requestPayout(address owner, bytes32 _hash) public returns (uint256) {
        require( ! payoutsFrozen );
        require( timeToPay(_hash) );

        MemoDB db = MemoDB(dbAddress);
        address _address = db.clientContract(owner);

        Client client = Client(_address);
        //address owner = client.owner();
        uint256 size = client.getFileSize(_hash);
        uint256 secs = now - payouts[_hash][msg.sender];
        uint256 amount = calculateMmr(secs, size);

        if(deposits[owner][_hash] < amount){
            amount = deposits[owner][_hash];
            //todo: init 'out of funds'
        }

        require( amount > 0 );

        address developer = client.getFileDeveloper(_hash);
        uint256 userReward = amount / 20;
        uint256 hostReward = amount - userReward * 2;

        deposits[owner][_hash] -= amount;
        balanceOf[msg.sender] += hostReward;
        balanceOf[developer] += userReward;

        UtilsAPI utils = UtilsAPI(utilsAddress);
        minersRewards[utils.getYear(now)][utils.getMonth(now)][utils.getDay(now)] += userReward;

        addToHolderList(msg.sender);
        addToHolderList(developer);

        payouts[_hash][msg.sender] = now;

        logTransaction(address(0), msg.sender, 'host_reward', hostReward);
        logTransaction(address(0), developer, 'developer_reward', userReward);

        Transfer(address(0), msg.sender, hostReward);
        Transfer(address(0), developer, userReward);

        return amount;
    }

    function doMinerReward(uint16 _year, uint8 _month, uint8 _day, address _miner, uint256 _amount) public onlyOwner {
        require(minersRewards[_year][_month][_day] >= _amount);
        minersRewards[_year][_month][_day] -= _amount;
        balanceOf[_miner] += _amount;
        logTransaction(address(0), _miner, 'miner_reward', _amount);
        Transfer(address(0), _miner, _amount);
    }


//    function doHoldersReward() public onlyOwner {
//        require(holdersToken > 0);
//
//        uint256 totalHolderParts = 0;
//
//        for (uint x = 0; x < holdersList.length; x++) {
//            if(balanceOf[holdersList[x]] >= minHoldersBalance){
//                totalHolderParts += balanceOf[holdersList[x]] / minHoldersBalance;
//            }
//        }
//
//        uint256 rewardPerPart = holdersToken / totalHolderParts;
//
//        for (x = 0; x < holdersList.length; x++) {
//            if(balanceOf[holdersList[x]] >= minHoldersBalance){
//                uint256 reward = balanceOf[holdersList[x]] / minHoldersBalance * rewardPerPart;
//                balanceOf[holdersList[x]] += reward;
//                holdersToken -= reward;
//                logTransaction(address(0), holdersList[x], 'holder_reward', reward);
//            }
//        }
//    }

    function withdrawAll() onlyOwner public {
        owner.transfer(address(this).balance);
    }

    // Import section
    function importBalance(address _address, uint256 _value) public onlyOwner {
        balanceOf[_address] = _value;
        addToHolderList(_address);
    }

    function importTotal(uint256 _totalSupply, uint256 _tokenForSale, uint256 _holdersToken) public onlyOwner {
        totalSupply = _totalSupply;
        tokenForSale = _tokenForSale;
        holdersToken = _holdersToken;
    }

    function importDeposits(address _address, bytes32 _file, uint256 _value) public onlyOwner {
        deposits[_address][_file] = _value;
    }

    function importPayouts(bytes32 _file, address _address, uint256 _time) public onlyOwner {
        payouts[_file][_address] = _time;
    }

}

