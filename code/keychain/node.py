from flask import Flask, request
from blockchain import Blockchain
import json
import operator
from requests import get

class Node:

    def __init__(self, difficulty=3):
        self.blockchain = Blockchain(difficulty)
        self.peers = []
        self.ip = get('https://api.ipify.org').text

    def get_chain(self):
        return self.blockchain
    
    def bootstrap(self, boostrap_address):

        url = "http://{}/peers".format(boostrap_address)
        result = get(url)
        if result.status_code != 200:
            print("unable to connect the bootstrap server")
            return
        peers = result.json()["peers"]
        for peer in peers:
            self.add_node(peer)
        
        results = self.broadcast(self.peers, self.ip, "addNode")
        address = get_address_best_hash(results)
        
        
    def put(self, key, value, origin):
        transaction = Transaction(key, value, origin)
        self._blockchain.add_transaction(self, transaction)

        
        


    def get_last_hash(self):
        return self.blockchain.get_last_hash()

    def broadcast(self, peers, message, message_type):
        """ 
        Best effort broadcast
        """
        results = {}
        for peer in peers:
            url = "http://{}/message".format(peer.get_address())
            results[peer.get_address()] = get(url, data=json.dumps({"type": message_type, "message": message})).json()
        
        return results
    
    def add_node(self, peer):
        new_peer = Peer(peer)
        self.peers.append(new_peer)

    def get_ip(self):
        return self.ip

class Peer:
    def __init__(self, address):
        """Address of the peer.

        Can be extended if desired.
        """
        self._address = address
    def get_address(self):
        return self._address


def get_address_best_hash(hashes):
    results = {}
    for hash in hashes.values():
        if(hash in results):
            results[hash] += 1
        else:
            results[hash] = 1
    
    best_hash = max(results.items(), key=operator.itemgetter(1))[0]
    for address,hash in hashes.items():
        if(best_hash == hash):
            return address
    return None
        

app = Flask(__name__)

node = Node()

@app.route("/blockchain")
def get_chain():
    blockchain = node.get_chain()
    chain_data = []
    for block in blockchain.get_chain():
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


@app.route("/bootstrap", methods=['POST'])
def boostrap():
    boostrap_address = request.get_json()["bootstrap"]
    node.bootstrap(boostrap_address)


@app.route("/addNode", methods=['POST'])
def add_node():
    address = request.get_json()["address"]
    node.add_node(address)
    return json.dumps({"last_hash": node.get_last_hash()})


@app.route("/message", methods=['POST'])
def message_hanler():
    message_type = request.get_json()["message_type"]
    message = request.get_json()["message"]

    if(message_type == "addNode"):
        node.add_node(message)
    elif():
        pass
    else:
        pass


@app.route("/put", methods=['POST'])
def put():
    key = request.get_json()["key"]
    value = request.get_json()["value"]
    origin = request.get_json()["origin"]
    node.put(key, value, origin)

app.run(debug=True, port=5000)

