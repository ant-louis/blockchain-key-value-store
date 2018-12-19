"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import time
import datetime
import json
import random
import argparse
import sys
import operator
import threading
import copy 
from hashlib import sha256
from flask import Flask, request
from requests import get, post, exceptions
from broadcast import Broadcast, Peer


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

    def proof(self, difficulty):
        """Return the proof of the current block."""
        return self.compute_hash().startswith('0' * difficulty)

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

    def _change_nonce(self, random = False):
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
    #Overwriting
    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

class Blockchain:

    def __init__(self, difficulty, port):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        address, download the peerlist, and start the bootstrapping procedure.
        """
        # Initialize the properties.
        self._blocks = []
        # self.broadcast = Broadcast([])
        self._pending_transactions = []
        self._difficulty = difficulty

        #Block confirmation request
        self._confirm_block = False #Block request flag
        self._blocks_to_confirm = []
        self._blocks_to_confirm_hash = []

        self._add_genesis_block()

        #self.ip = get('https://api.ipify.org').text
        self.ip = "127.0.0.1:{}".format(port)

        #Creating mining thread
        print("Create mining thread")
        mining_thread = threading.Thread(target = self.mine)
        mining_thread.start()


    def _add_genesis_block(self):
        """Adds the genesis block to your blockchain."""
        self._blocks.append(Block(0, [], time.time(), "0"))

    def bootstrap(self, address):
        if(address == self.ip):
            # Initialize the chain with the Genesis block.
            self._add_genesis_block()
            return
        url = "http://{}/peers".format(address)
        result = get(url)

        if result.status_code != 200:
            print("Unable to connect the bootstrap server")
            return
        peers = result.json()["peers"]
        for peer in peers:
            self.add_node(peer)
        self.add_node(address)

        if(self.ip in peers):
            peers.remove(self.ip)

        results = self.broadcast.send("addNode",self.ip)
        address = get_address_best_hash(results)
        url = "http://{}/blockchain".format(address)
        result = get(url)
        if result.status_code != 200:
            print("Unable to connect the load blockchain")
            return
        chain = result.json()["chain"]

        for block in chain:
            block = json.loads(block)
            transactions = []

            for t in block["_transactions"]:
                transactions.append(Transaction(t["key"], t["value"], t["origin"]))
                
        self._blocks.append(Block(block["_index"], 
                                    transactions, 
                                    block["_timestamp"], 
                                    block["_previous_hash"]))  
        for block in self._blocks:
            print(block.get_transactions())

    def add_node(self, peer):
        self.broadcast.add_peer(peer)

    def get_ip(self):
        return self.ip

    def put(self, key, value, origin):
        """Puts the specified key and value on the Blockchain.
        """
        transaction = Transaction(key, value, origin)
        self.add_transaction(transaction)

    def get_blocks(self):
        """ Return all blocks from the chain"""
        return self._blocks

    def get_last_hash(self):
        """Return the hash of the last block"""
        return self._blocks[-1].compute_hash()

    def get_peers(self):
        return self.broadcast.get_peers()

    def difficulty(self):
        """Returns the difficulty level."""
        return self._difficulty

    def add_transaction(self, transaction):
        """Adds a transaction to your current list of transactions,
        and broadcasts it to your Blockchain network.
        
        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """

        print("Added transaction" ,transaction.__dict__)
        self._pending_transactions.append(transaction)


        #TODO: Broadcast transaction to network
        
        return

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
            new_block._change_nonce()
            computed_hash = new_block.compute_hash()

            #If process gets a block confirmation request during mining procedure
            #TODO: One node accepts block while the others are mining
            if (self._confirm_block and
                self._blocks_to_confirm_hash and
                self._blocks_to_confirm):

                print("Confirming an incoming block...")
                if not self._check_block(self._blocks_to_confirm[-1], self._blocks_to_confirm_hash[-1]):
                    #Block is valid, we add it to the chain, stop mining
                    print("Adding block")
                    self._add_block(self._blocks_to_confirm[-1], self._blocks_to_confirm_hash[-1])
                    
                    return None

                else:
                    print("Resume mining...")
                    #Block is not valid, we continue mining
                    self._blocks_to_confirm.pop()
                    self._blocks_to_confirm_hash.pop()
                    if self._blocks_to_confirm:
                        self._confirm_block = False

        return computed_hash

    def confirm_block(self, block, block_hash):
        """
        Confirm a block from another Node

        Parameters:
        ----------
        block: Block object
        block_hash: sha256 hash of the Block object
        """
        self._confirm_block = True
        self._blocks_to_confirm.append(block)
        self._blocks_to_confirm_hash.append(block_hash)

    def mine(self):
        """Implements the mining procedure
        """

        while(True):
            if(not self._pending_transactions):
                time.sleep(1) #Wait before checking new transactions
            else:
                last_block = self._blocks[-1]
                
                input_tr = copy.deepcopy(self._pending_transactions)
                nb_transactions = len(input_tr)
                new_block = Block(index=last_block._index + 1,
                                transactions=input_tr,
                                timestamp=time.time(),
                                previous_hash=last_block.compute_hash())

                #Remove the transactions that were inserted into the block
                del self._pending_transactions[:nb_transactions]
                print("Processed {} transaction(s) in this block, {} pending".format(nb_transactions, len(self._pending_transactions)))

                print("Mining....")
                proof = self._proof_of_work(new_block)
                if proof is None:
                    print("Block confirmed by other node")

                    foreign_block = self._blocks_to_confirm.pop()
                    self._blocks_to_confirm_hash.pop()
                    local_block_tr = new_block.get_transactions()

                    for tr in [json.loads(t) for t in foreign_block._transactions]:
                        tr_obj = Transaction(tr["key"], tr["value"], tr["origin"]) 
                        
                        # Remove the incoming block's transaction from the pool
                        if tr_obj in self._pending_transactions:
                            self._pending_transactions.remove(tr_obj)
                            
                        #Remove the incoming block's transaction from the locally mined block
                        if tr_obj in local_block_tr:
                            local_block_tr.remove(tr_obj)
                    
                    #The transactions that were not added to the chain get put back in the pool
                    self._pending_transactions.extend(local_block_tr)
                    
                    #Reset block confirmation fields
                    if self._blocks_to_confirm:
                        self._confirm_block = False
                        

                elif self._check_block(new_block, proof):
                    #Add block to chain
                    self._add_block(new_block, proof)
                else:
                    #Computed proof is not correct, add the transactions back in the pool
                    self._pending_transactions.extend(input_tr)

    def _add_block(self,block, computed_hash):
        """
        Add a block to the blockchain
        """
        self._blocks.append(block)
        print("Block ID {} hash {} added to the chain".format(block._index, computed_hash))

    def _check_block(self, block, computed_hash):
        """
        Check the validity of the block before adding it
        to the blockchain
        """
        
        #Get last block from blockchain
        last_block = self._blocks[-1]
        previous_hash = last_block.compute_hash()

        # print("Previous hash",block.get_previous_hash())
        # print("Previous hash computed",previous_hash)
        # print("Hash",block.compute_hash())
        # print("Computed hash",computed_hash)
        return (previous_hash == block.get_previous_hash() and 
                computed_hash.startswith('0' * self._difficulty) and 
                computed_hash == block.compute_hash())

    def is_valid(self):
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        """
        previous_hash = self._blocks[-1].get_previous_hash()
        it = -1
        while previous_hash != "0":
            #Check if proof is valid and if previous hashes match
            if(previous_hash != self._blocks[it-1].compute_hash() or
                not self._blocks[it].proof( self._difficulty)):
                
                return False
            it = it - 1
            previous_hash = self._blocks[it].get_previous_hash()
        
        return True


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
