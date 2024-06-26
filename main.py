from flask import Flask, render_template, request, jsonify, send_file
from web3 import Web3
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Load the contract ABI and address
with open('build/contracts/BoardGameShop.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

    network_id = list(contract_json['networks'].keys())[-1]
    contract_address = contract_json['networks'][network_id]['address']

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# File storage functions
def save_to_file(filename, data):
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')


def read_from_file(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return [json.loads(line) for line in f]


@app.route('/')
def index():
    return render_template('index.html', contract_address=contract_address, contract_abi=contract_abi)


@app.route('/add_game', methods=['POST'])
def add_game():
    data = request.json
    title = data['title']
    description = data['description']
    price = int(data['price'])

    # Save game info to file with an ID
    game_id = len(read_from_file('games_in_shop.txt')) + 1
    save_to_file('games_in_shop.txt', {'game_id': game_id, 'title': title, 'description': description, 'price': price})

    return jsonify({'status': 'success', 'message': 'Game added successfully'})


@app.route('/update_game', methods=['POST'])
def update_game():
    data = request.json
    game_id = int(data['game_id'])
    title = data['title']
    description = data['description']
    price = int(data['price'])

    games = read_from_file('games_in_shop.txt')
    for game in games:
        if game['game_id'] == game_id:
            game['title'] = title
            game['description'] = description
            game['price'] = price
            break
    else:
        return jsonify({'status': 'error', 'message': 'Game not found'})

    # Overwrite file with updated game list
    with open('games_in_shop.txt', 'w') as f:
        for game in games:
            f.write(json.dumps(game) + '\n')

    return jsonify({'status': 'success', 'message': 'Game updated successfully'})


@app.route('/buy_game', methods=['POST'])
def buy_game():
    data = request.json
    game_id = int(data['game_id'])

    # Check if the game exists
    games = read_from_file('games_in_shop.txt')
    for game in games:
        if game['game_id'] == game_id:
            save_to_file('games_bought.txt', {'game_id': game_id, 'buyer': data['buyer']})
            return jsonify({'status': 'success', 'message': 'Game purchased successfully'})

    return jsonify({'status': 'error', 'message': 'Game not found'})


@app.route('/remove_game', methods=['POST'])
def remove_game():
    data = request.json
    game_id = int(data['game_id'])

    games = read_from_file('games_in_shop.txt')
    games = [game for game in games if game['game_id'] != game_id]

    # Overwrite file with updated game list
    with open('games_in_shop.txt', 'w') as f:
        for game in games:
            f.write(json.dumps(game) + '\n')

    return jsonify({'status': 'success', 'message': 'Game removed successfully'})


@app.route('/get_games', methods=['GET'])
def get_games():
    games = read_from_file('games_in_shop.txt')
    return jsonify(games)


@app.route('/get_bought_games', methods=['GET'])
def get_bought_games():
    games = read_from_file('games_bought.txt')
    return jsonify(games)


if __name__ == '__main__':
    app.run(debug=True)