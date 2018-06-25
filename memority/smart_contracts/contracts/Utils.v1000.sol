pragma solidity 0.4.24;

contract owned {
    address public owner;
    function owned() public {owner = msg.sender;}
    modifier onlyOwner { require(msg.sender == owner); _;}
    function transferOwnership(address newOwner) onlyOwner public {owner = newOwner;}
}

contract Utils is owned{

    uint256 version = 1000;


    function Utils() public {

    }

    function constVerify(bytes32 r, bytes32 s, uint8 v, bytes32 hash) constant returns(address) {
        return ecrecover(hash, v, r, s);
    }

    function verify(bytes32 r, bytes32 s, uint8 v, bytes32 hash) returns(address) {
        bytes memory prefix = "\x19Ethereum Signed Message:\n32";
        bytes32 prefixedHash = keccak256(prefix, hash);

        return ecrecover(prefixedHash, v, r, s);
    }

    function verifyTest() returns(address) {
        bytes32 r = 0xf01ae6cac8a11cbfa58a641b585f22ae57d4e0705785d2b099dece6564d5dcee;
        bytes32 s = 0x54f502f510d29aaf07ba788e5bdcb58e56974a8b6a95d44a9ea04c32e907add3;
        uint8 v = 27;
        bytes32 hash = 0x9c22ff5f21f0b81b113e63f7db6da94fedef11b2119b4088b89664fb9a3cb658;
        return ecrecover(hash, v, r, s);
    }

    function keccak(bytes32 hash) returns(bytes32) {
        bytes memory prefix = "\x19Ethereum Signed Message:\n32";
        bytes32 prefixedHash = keccak256(prefix, hash);

        return prefixedHash;
    }

    function hash(bytes32 hash) returns(bytes32) {
        return hash;
    }

    function prefix() returns(bytes) {
        bytes memory prefix = "\x19Ethereum Signed Message:\n32";
        return prefix;
    }
}
