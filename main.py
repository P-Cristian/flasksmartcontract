from flask import Flask, render_template, request, jsonify
from web3 import Web3
import json

app = Flask(__name__)

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Load the contract ABI and address
with open('build/contracts/SimpleStorage.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

    # Get the most recent deployment
    network_id = list(contract_json['networks'].keys())[-1]
    contract_address = contract_json['networks'][network_id]['address']

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=contract_abi)


@app.route('/')
def index():
    return render_template('index.html', contract_address=contract_address, contract_abi=contract_abi)


@app.route('/get', methods=['GET'])
def get_value():
    value = contract.functions.get().call()
    return jsonify({'value': value})


if __name__ == '__main__':
    app.run(debug=True)