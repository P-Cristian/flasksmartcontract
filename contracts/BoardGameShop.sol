contract BoardGameShop {
    struct BoardGame {
        string title;
        string description;
        uint256 price;
        address owner;
        bool isForSale;
    }

    mapping(uint256 => BoardGame) public boardGames;
    uint256 public gameCount;

    event GameAdded(uint256 gameId, string title, uint256 price);
    event GameUpdated(uint256 gameId, string title, uint256 price);
    event GameSold(uint256 gameId, address buyer);
    event GameRemoved(uint256 gameId);

    function addGame(string memory _title, string memory _description, uint256 _price) public {
        gameCount++;
        boardGames[gameCount] = BoardGame(_title, _description, _price, msg.sender, true);
        emit GameAdded(gameCount, _title, _price);
    }

    function updateGame(uint256 _gameId, string memory _title, string memory _description, uint256 _price) public {
        require(boardGames[_gameId].owner == msg.sender, "Only the owner can update the game");
        BoardGame storage game = boardGames[_gameId];
        game.title = _title;
        game.description = _description;
        game.price = _price;
        emit GameUpdated(_gameId, _title, _price);
    }

    function buyGame(uint256 _gameId) public payable {
        BoardGame storage game = boardGames[_gameId];
        require(game.isForSale, "Game is not for sale");
        require(msg.value >= game.price, "Insufficient funds");

        address payable seller = payable(game.owner);
        seller.transfer(msg.value);
        game.owner = msg.sender;
        game.isForSale = false;

        emit GameSold(_gameId, msg.sender);
    }

    function removeGame(uint256 _gameId) public {
        require(boardGames[_gameId].owner == msg.sender, "Only the owner can remove the game");
        delete boardGames[_gameId];
        emit GameRemoved(_gameId);
    }

    function getGame(uint256 _gameId) public view returns (string memory, string memory, uint256, address, bool) {
        BoardGame memory game = boardGames[_gameId];
        return (game.title, game.description, game.price, game.owner, game.isForSale);
    }
}