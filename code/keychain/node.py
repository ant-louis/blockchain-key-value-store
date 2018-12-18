from flask import Flask, request
from blockchain import Blockchain
import json
import requests

class Node:

    def __init__(self, difficulty=3):
        self.blockchain = Blockchain(difficulty)
        self.peers = []

    def get_chain(self):
        return self.blockchain
    
    def broadcast_bootstrap(self, peers):
        pass

    def broadcast(self, peers, message):
        pass
    

        

app = Flask(__name__)

node = Node()

@app.route("/blockchain")
def get_chain():
    blockchain = node.get_chain()
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


@app.route("/bootstrap", methods=['POST'])
def boostrap():
    boostrap_adress = request.get_json()["bootstrap"]
    url = "http://{}/peers".format(boostrap_adress)
    result = request.get(url)
    if result.status_code != 200:
        print("unable to connect the bootstrap server")
        return
    peers = result.json()["peers"]
    


    

app.run(debug=True, port=5000)

