"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import time
import datetime
import json
import random
import sys
import operator
from hashlib import sha256
from flask import Flask, request
from requests import get


class TransactionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Transaction):
            return vars(obj)
        return json.JSONEncoder.default(self, obj)

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce = 0):
        """Describe the properties of a block."""

        self._index = index
        self._transactions = transactions
        self._timestamp = timestamp
        self._previous_hash = previous_hash
        self._nonce = nonce

    def proof(self):
        """Return the proof of the current block."""
        raise NotImplementedError

    def get_transactions(self):
        """Returns the list of transactions associated with this block."""
        return self._transactions
    
    def get_previous_hash(self):
        return self._previous_hash

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True, cls=TransactionEncoder)
        return sha256(block_string.encode()).hexdigest()

    def change_nonce(self, random = False):
        if(random):
            self._nonce = random.randint(1, sys.maxsize)
        else:
            self._nonce += 1

class Transaction:
    def __init__(self, key, value, origin):
        """A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self.key = key
        self.value = value 
        self.origin = origin

class Peer:
    def __init__(self, address):
        """Address of the peer.

        Can be extended if desired.
        """
        self._address = address
    def get_address(self):
        return self._address

class Blockchain:
    def __init__(self, difficulty, bootstrap_address):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        address, download the peerlist, and start the bootstrapping procedure.
        """
        print("in init")
        # Initialize the properties.
        self._blocks = []
        self._peers = []
        self._pending_transactions = []
        self._difficulty = difficulty

        #Block confirmation request
        self._confirm_block = False #B lock request flag
        self._block_to_confirm = None
        self._block_hash = None

        self.ip = get('https://api.ipify.org').text


        # Initialize the chain with the Genesis block.
        self._add_genesis_block()

        # Bootstrap the chain with the specified bootstrap address.
        self._bootstrap(bootstrap_address)

    def _add_genesis_block(self):
        """Adds the genesis block to your blockchain."""
        self._blocks.append(Block(0, [], time.time(), "0"))

    def _bootstrap(self, address):

        if(address == self.ip):
            return
        print("In bootstrap")
        url = "http://{}:5000/peers".format(address)
        result = get(url)
        print("after first get")

        if result.status_code != 200:
            print("Unable to connect the bootstrap server")
            return
        peers = result.json()["peers"]
        print(peers)
        for peer in peers:
            self.add_node(peer)
        
        results = self.broadcast(self._peers, self.ip, "addNode")
        address = get_address_best_hash(results)
        
        url = "http://{}:5000/peers".format(address)
        result = get(url)
        if result.status_code != 200:
            print("Unable to connect the load blockchain")
            return
        
        chain = result.json()["chain"]
        print(chain)
        print(type(chain))

        for block in chain:
            self._blocks.append(Block(block.index, 
                                        block.transactions, 
                                        block.timestamp, 
                                        block.previous_hash))            


    def add_node(self, peer):
        new_peer = Peer(peer)
        self._peers.append(new_peer)

    def get_ip(self):
        return self.ip

    def put(self, key, value, origin):
        transaction = Transaction(key, value, origin)
        self.add_transaction(transaction)
        
    def broadcast(self, peers, message, message_type):
        """ 
        Best effort broadcast
        """
        results = {}
        for peer in peers:
            url = "http://{}:5000/message".format(peer.get_address())
            results[peer.get_address()] = get(url, data=json.dumps({"type": message_type, "message": message})).json()
        
        return results

    def get_blocks(self):
        """ Return all blocks from the chain"""
        return self._blocks

    def get_last_hash(self):
        """Return the hash of the last block"""
        return self._blocks[-1].compute_hash()

    def get_peers(self):
        return self._peers

    def difficulty(self):
        """Returns the difficulty level."""
        return self._difficulty

    def add_transaction(self, transaction):
        """Adds a transaction to your current list of transactions,
        and broadcasts it to your Blockchain network.
        
        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """
        self._pending_transactions.append(transaction)
        #TODO: Broadcast transaction to network

    def _proof_of_work(self, new_block):
        """
        Implement the proof of work algorithm
        Also check for block confirmation request from another Node
        """
        #Reset nonce
        new_block._nonce = 0

        #Get the real hash of the block
        computed_hash = new_block.compute_hash()

        #Find the nonce that computes the right block hash
        while not computed_hash.startswith('0' * self._difficulty):
            new_block.change_nonce()
            computed_hash = new_block.compute_hash()

            #If process gets a block confirmation request during mining procedure
            #TODO: One node accepts block while the others are minign
            if (self._confirm_block and
                self._block_hash and
                self._block_to_confirm):

                if self._check_block(self._block_to_confirm, self._block_hash):
                    #Block is valid, we add it to the chain, stop mining
                    self._add_block(self._block_to_confirm, self._block_hash)
                    self._confirm_block = False
                    self._block_hash = None
                    self._block_to_confirm = None
                    
                    return None

                else:
                    #Block is not valid, we continue mining
                    self._confirm_block = False
                    self._block_hash = None
                    self._block_to_confirm = None

        return computed_hash

    def confirm_block(self, block, block_hash):
        """
        Confirm a block from another Node
        """
        self._confirm_block = True
        self._block_to_confirm = block
        self._block_hash = block_hash

    
    def mine(self):
        """Implements the mining procedure."""

        #No pending transactions
        if not self._pending_transactions:
            return False

        last_block = self._blocks[-1]

        new_block = Block(index=last_block._index + 1,
                          transactions=self._pending_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.compute_hash())
        
        print("Mining")
        proof = self._proof_of_work(new_block)
        if proof is None:
            print("Block confirmed by other node")
            return False

        print("The hash of the block was :", proof)
        #Reset the transaction list
        self._pending_transactions = [] 

        return self._add_block(new_block, proof)

    def _add_block(self,block, computed_hash):
        """
        Add a block to the blockchain
        """
        #Check validity of block
        if not self._check_block(block, computed_hash):
            print("Block not valid")
            return False
        print("Block with ID {} added to the chain".format(block._index))
        self._blocks.append(block)
        return True


    def _check_block(self, block, computed_hash):
        """
        Check the validity of the block before adding it
        to the blockchain
        """
        
        #Get last block from blockchain
        last_block = self._blocks[-1]
        previous_hash = last_block.compute_hash()

        return (previous_hash == block.get_previous_hash() and 
                computed_hash.startswith('0' * self._difficulty) and 
                computed_hash == block.compute_hash())


    def is_valid(self):
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        """
        #TODO: Do the method
        raise NotImplementedError

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
print("after app run")

node = Blockchain(2,"127.0.0.0")
transaction = Transaction("Test", 123, 666)
node.add_transaction(transaction)
node.mine()
app.run(host = "0.0.0.0", debug=True, port=5000)



@app.route("/blockchain")
def get_chain():
    chain_data = []
    for block in node.get_blocks():
        chain_data.append(json.dumps(block.__dict__, sort_keys=True, cls=TransactionEncoder))
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


@app.route("/peers")
def get_peers():
    return json.dumps({"peers": node.get_peers()})
