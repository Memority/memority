pragma solidity 0.4.24;

contract owned {
    address public owner;
    function owned() public {owner = msg.sender;}
    modifier onlyOwner { require(msg.sender == owner); _;}
    function transferOwnership(address newOwner) onlyOwner public {owner = newOwner;}
}

contract Utils is owned{

    uint256 version = 1000;


    function Utils(address _tokenAddress) public {

    }

    function newClient(address owner) public {

    }
}
