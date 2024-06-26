const SimpleStorage = artifacts.require("BoardGameShop");

module.exports = function(deployer) {
  deployer.deploy(SimpleStorage);
};