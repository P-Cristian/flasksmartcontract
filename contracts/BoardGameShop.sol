// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BoardGameShop {
    struct Game {
        string title;
        string description;
        uint price;
        address owner;
        bool isForSale;
    }

    Game[] public games;
    mapping(uint => address) public gameToOwner;
    mapping(address => uint) ownerGameCount;

    function addGame(string memory _title, string memory _description, uint _price) public {
        games.push(Game(_title, _description, _price, msg.sender, true));
        uint gameId = games.length - 1;
        gameToOwner[gameId] = msg.sender;
        ownerGameCount[msg.sender]++;
    }

    function getGame(uint _gameId) public view returns (string memory, string memory, uint, address, bool) {
        Game storage game = games[_gameId];
        return (game.title, game.description, game.price, game.owner, game.isForSale);
    }

    function buyGame(uint _gameId) public payable {
        Game storage game = games[_gameId];
        require(game.isForSale, "Game is not for sale");
        require(msg.value == game.price, "Incorrect value");

        address seller = game.owner;
        game.owner = msg.sender;
        game.isForSale = false;
        ownerGameCount[seller]--;
        ownerGameCount[msg.sender]++;
        gameToOwner[_gameId] = msg.sender;

        payable(seller).transfer(msg.value);
    }

    function updateGame(uint _gameId, string memory _title, string memory _description, uint _price, bool _isForSale) public {
        Game storage game = games[_gameId];
        require(msg.sender == game.owner, "Only the owner can update the game");

        game.title = _title;
        game.description = _description;
        game.price = _price;
        game.isForSale = _isForSale;
    }

    function totalGames() public view returns (uint) {
    return games.length;
}
}