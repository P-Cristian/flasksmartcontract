from flask import Flask, render_template, request, jsonify, send_file
from web3 import Web3
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)


w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))


with open('build/contracts/BoardGameShop.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

    network_id = list(contract_json['networks'].keys())[-1]
    contract_address = contract_json['networks'][network_id]['address']


contract = w3.eth.contract(address=contract_address, abi=contract_abi)


UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



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

    game_id = len(read_from_file('games_in_shop.txt')) + 1
    save_to_file('games_in_shop.txt', {'game_id': game_id, 'title': title, 'description': description, 'price': price, 'isForSale': True})

    return jsonify({'status': 'success', 'message': 'Game added successfully'})

@app.route('/update_game', methods=['POST'])
def update_game():
    data = request.json
    game_id = int(data['game_id'])
    title = data['title']
    description = data['description']
    price = int(data['price'])
    isForSale = data['isForSale']

    games = read_from_file('games_in_shop.txt')
    for game in games:
        if game['game_id'] == game_id:
            game['title'] = title
            game['description'] = description
            game['price'] = price
            game['isForSale'] = isForSale
            break
    else:
        return jsonify({'status': 'error', 'message': 'Game not found'})

 
    with open('games_in_shop.txt', 'w') as f:
        for game in games:
            f.write(json.dumps(game) + '\n')

    return jsonify({'status': 'success', 'message': 'Game updated successfully'})

@app.route('/buy_game', methods=['POST'])
def buy_game():
    data = request.json
    game_id = int(data['game_id'])

   
    games = read_from_file('games_in_shop.txt')
    for game in games:
        if game['game_id'] == game_id:
            if not game['isForSale']:
                return jsonify({'status': 'error', 'message': 'Game is not for sale'})
            save_to_file('games_bought.txt', {'game_id': game_id, 'buyer': data['buyer']})
            game['isForSale'] = False
            break
    else:
        return jsonify({'status': 'error', 'message': 'Game not found'})

 
    with open('games_in_shop.txt', 'w') as f:
        for game in games:
            f.write(json.dumps(game) + '\n')

    return jsonify({'status': 'success', 'message': 'Game purchased successfully'})


@app.route('/remove_game', methods=['POST'])
def remove_game():
    data = request.json
    game_id = int(data['game_id'])

    games = read_from_file('games_in_shop.txt')
    games = [game for game in games if game['game_id'] != game_id]


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
    try:
        with open('bought_games.txt', 'r') as f:
            titles = f.read().splitlines()
        return jsonify(titles), 200
    except Exception as e:
        print(f"Error reading from file: {str(e)}")
        return jsonify({'error': 'Failed to read game titles from file'}), 500


@app.route('/write_game', methods=['POST'])
def write_game():
    data = request.json
    game_title = data.get('gameTitle')
    
    if not game_title:
        return jsonify({'error': 'No game title provided'}), 400
    
    try:
        with open('bought_games.txt', 'a') as f:
            f.write(game_title + '\n')
        return jsonify({'message': 'Game title written successfully'}), 200
    except Exception as e:
        print(f"Error writing to file: {str(e)}")
        return jsonify({'error': 'Failed to write game title to file'}), 500

if __name__ == '__main__':
    app.run(debug=True)