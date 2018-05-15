pragma solidity ^0.4.16; //We have to specify what version of the compiler this code will use

contract Token {
    address public dbAddress;
    function preparePayouts(address[] _addresses, bytes32 _hash) public returns (bool success){}
    function preparePayout(address _addresses, bytes32 _hash) public returns (bool success){}
    function replacePayout(address _address_from, address _address_to, bytes32 _hash, address[] voters) public returns (bool){}
    function depositForFile(uint256 _value, bytes32 _hash) public returns (bool success) {}
}

contract MemoDB {
    address tokenAddress;
    modifier onlyToken {require(msg.sender == tokenAddress);_;}
    function logTransaction(address _from, address _to, bytes32 _file, uint256 _value) external onlyToken {}
    function updateHost(bytes32 ip) public {}
    function newClient(address owner) public {}
}

contract owned {
    address public owner;
    function owned() public {owner = msg.sender;}
    modifier onlyOwner { require(msg.sender == owner); _;}
    function transferOwnership(address newOwner) onlyOwner public {owner = newOwner;}
}

contract Client is owned {

    struct file {
        string name;
        bytes32 hash;
        address[] hosts;
        uint size;
        uint timestamp;
        address developer;
    }

    mapping (bytes32 => file) public fileList;
    mapping (bytes32 => mapping (address => address[])) public offlineHosts;
    mapping (bytes32 => mapping (address => uint[])) public offlineVoteTime;

    address public token_address;
    bytes32[] public files;
    uint file_copies = 10;
    address public dbAddress;

    function Client(address _token_address) public {
        token_address = _token_address;

        Token token = Token(_token_address);
        dbAddress = token.dbAddress();

        MemoDB db = MemoDB(dbAddress);
        db.newClient(msg.sender);
    }

    function changeTokenAddress(address _address) external onlyOwner {
        token_address = _address;
    }

    function makeDeposit(uint256 _value, bytes32 _hash) external onlyOwner returns (bool success) {
        Token token = Token(token_address);
        bool status = token.depositForFile(_value, _hash);
        return status;
    }

    function newFile(bytes32 hash, string name, uint size, address developer, address[] hosts) external onlyOwner {
        if(fileList[hash].size == 0){
            files.push(hash);
        }

        fileList[hash].hash = hash;
        fileList[hash].name = name;
        fileList[hash].size = size;
        fileList[hash].hosts = hosts;
        fileList[hash].timestamp = now;
        fileList[hash].developer = developer;

        Token token = Token(token_address);
        token.preparePayouts(hosts, hash);
    }

    function inFileList(bytes32 _hash, address _address) internal returns (bool) {
        for (uint i = 0; i < fileList[_hash].hosts.length; i++) {
            if(fileList[_hash].hosts[i] == _address){
                return true;
            }
        }
        return false;
    }

    function inOfflineList(bytes32 _hash, address _address) internal returns (bool) {
        return offlineHosts[_hash][_address].length > 0;
    }

    function addHostToFile(bytes32 _hash) external {
        require(fileList[_hash].size > 0);                      // file exists
        require(fileList[_hash].hosts.length < file_copies);    // file need copy
        require( ! inFileList(_hash, msg.sender));              // prevent host duplicate
        require( ! inOfflineList(_hash, msg.sender));           // not in offline list

        fileList[_hash].hosts.push(msg.sender);

        Token token = Token(token_address);
        token.preparePayout(msg.sender, _hash);
    }

    function replaceHost(bytes32 _hash, address _oldHost) external {
        require( fileList[_hash].size > 0 );     // file exists
        require( offlineHosts[_hash][_oldHost].length > fileList[_hash].hosts.length / 2 );  // >50% votes on host offline

        bool oldExists = false;
        bool newExists = false;

        for (uint i = 0; i < fileList[_hash].hosts.length; i++) {
            if(fileList[_hash].hosts[i] == msg.sender){
                newExists = true;
                break;
            }

            if(fileList[_hash].hosts[i] == _oldHost){
                oldExists = true;
                fileList[_hash].hosts[i] = msg.sender;
            }
        }

        require(oldExists && !newExists);

        Token token = Token(token_address);
        bool status = token.replacePayout(_oldHost, msg.sender, _hash, offlineHosts[_hash][_oldHost]);
        if(status){
            delete offlineHosts[_hash][_oldHost];
        }
    }

    function getFiles() view public returns (bytes32[]) {
        return files;
    }

    function getFileName(bytes32 _hash) view public returns (string) {
        require( fileList[_hash].size > 0 );
        return fileList[_hash].name;
    }

    function getFileSize(bytes32 _hash) view public returns (uint256) {
        require( fileList[_hash].size > 0 );
        return fileList[_hash].size;
    }

    function getFileDeveloper(bytes32 _hash) view public returns (address) {
        require( fileList[_hash].size > 0 );
        return fileList[_hash].developer;
    }

    function getFileHosts(bytes32 _hash) view public returns (address[]) {
        require( fileList[_hash].size > 0 );
        return fileList[_hash].hosts;
    }

    function voteOffline(address _address, bytes32 _hash) public returns (bool success) {
        // check if host and voter addresses exists in file hosts
        bool voterExists = false;
        bool hostExists = false;
        for (uint x = 0; x < fileList[_hash].hosts.length; x++) {
            if(fileList[_hash].hosts[x] == _address){
                hostExists = true;
            }
            if(fileList[_hash].hosts[x] == msg.sender){
                voterExists = true;
            }
            if(hostExists && voterExists){
                break;
            }
        }

        require(hostExists && voterExists);

        // check for vote from this host
        bool voted = false;
        for (uint i = 0; i < offlineHosts[_hash][_address].length; i++) {
            if(offlineHosts[_hash][_address][i] == msg.sender){
                voted = true;
                break;
            }
        }
        require( ! voted );

        offlineHosts[_hash][_address].push(msg.sender);
        offlineVoteTime[_hash][_address].push(now);

        return true;
    }

//    function getOfflineVoters(bytes32 _hash, address _address) view public returns (address[]) {
//        return offlineHosts[_hash][_address];
//    }

    function needCopy(bytes32 _hash) view public returns (bool) {
        return fileList[_hash].hosts.length < file_copies;
    }

    function needReplace(address _address, bytes32 _hash) view public returns (bool) {
        uint activeHosts = fileList[_hash].hosts.length;
        uint actualVotes = 0;
        uint from = now - 60 * 60 * 24;
        for (uint i = 0; i < offlineVoteTime[_hash][_address].length; i++) {
            if(offlineVoteTime[_hash][_address][i] >= from){
                actualVotes++;
            }
        }

        return actualVotes > activeHosts / 2;
    }


}