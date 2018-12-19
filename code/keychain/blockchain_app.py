from blockchain import Blockchain, Transaction, TransactionEncoder
import time
import datetime
import json
import random
import argparse
import sys
import operator
from hashlib import sha256
from flask import Flask, request
from requests import get, post, exceptions

def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--miner", type=bool, default=False, nargs='?',
                        const=True, help="Starts the mining procedure.")
    parser.add_argument("--bootstrap", type=str, default=None,
                        help="Sets the address of the bootstrap node.")
    parser.add_argument("--difficulty", type=int, default=5,
                        help="Sets the difficulty of Proof of Work, only has "
                             "an effect with the `--miner` flag has been set.")
    parser.add_argument("--port", type=int, default=5000)
    arguments, _ = parser.parse_known_args()

    return arguments

app = Flask(__name__)

node = Blockchain(2, parse_arguments().port)


@app.route("/bootstrap")
def boostrap():
    address = request.args.get("bootstrap")
    node.bootstrap(address)
    return json.dumps({"result":True})

@app.route("/blockchain")
def get_chain():
    chain_data = []
    for block in node.get_blocks():
        chain_data.append(json.dumps(block.__dict__, sort_keys=True, cls=TransactionEncoder))
    return json.dumps({"length": len(chain_data), "chain": chain_data})

@app.route("/mine")
def mine():
    node.mine()

@app.route("/addNode")
def add_node():
    address = request.get_json()["address"]
    node.add_node(address)
    
@app.route("/message")
def message_handler():
    message_type = request.args.get('type')
    message = request.args.get('message')
    if(message_type == "addNode"):
        node.add_node(message)
        return json.dumps(node.get_last_hash())
    elif():
        pass
    else:
        pass

@app.route("/put")
def put():
    key = request.get_json()["key"]
    value = request.get_json()["value"]
    origin = request.get_json()["origin"]
    node.put(key, value, origin)

@app.route("/peers")
def get_peers():
    peers = []
    for peer in node.get_peers():
        peers.append(peer.get_address())
    return json.dumps({"peers": peers})






if __name__ == "__main__":
    arguments = parse_arguments()
    app.run(debug=True, port=arguments.port)