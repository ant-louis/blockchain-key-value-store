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
from broadcast import Broadcast, send_to_one 

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

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """

        #Don't hash successors in blocks
        to_hash = copy.deepcopy(self.__dict__)
        block_string = json.dumps(to_hash, sort_keys=True, cls=TransactionEncoder)
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
    #Overwriting equality function
    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

class Blockchain:

    def __init__(self, difficulty, port, miner = True):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        address, download the peerlist, and start the bootstrapping procedure.
        """
        # Initialize the properties.
        self._master_chain = []
        self._branch_list = []
        self._last_hash = None
        self._pending_transactions = []
        self._difficulty = difficulty

        #Block confirmation request
        self._confirm_block = False #Block request flag
        self._blocks_to_confirm = []
        self._blocks_to_confirm_hash = []

        #self.ip = get('https://api.ipify.org').text
        self._ip = "127.0.0.1:{}".format(port)
        
        self._add_genesis_block()
        self._last_hash = self._master_chain[-1].compute_hash()
        print("Last hash", self._last_hash)

        # self.broadcast = Broadcast([], self._ip)

        #Creating mining thread
        if miner:
            print("Create mining thread")
            mining_thread = threading.Thread(target = self.mine)
            mining_thread.start()

    def _add_genesis_block(self):
        """Adds the genesis block to your blockchain."""
        self._master_chain.append(Block(0, [], time.time(), "0"))

    def bootstrap(self, address):
        if(address == self._get_ip()):
            # Initialize the chain with the Genesis block.
            self._add_genesis_block()
            return
        # Get the list of peer from bootstrap node
        try:
            result = send_to_one(address, "peers")
        except exceptions.RequestException:
            print("Unable to bootstrap (connection faild to bootstrap node)")
            return
        peers = result.json()["peers"]
        for peer in peers:
            self.add_node(peer)
        self.add_node(address)
        if(self._get_ip() in peers):
            peers.remove(self._get_ip())


        # Get all the blocks from a non-corrupted node
        hashes = {}
        for peer in self.get_peers():
            hashes[peer] = send_to_one(peer, "addNode", {"address" : self._get_ip()})
        if hashes:
            address = get_address_best_hash(hashes)
        result = send_to_one(address, "blockchain")
        chain = result.json()["chain"]

        # Reconstruct the chain
        for block in chain:
            block = json.loads(block)
            transaction = []

            for t in block["_transactions"]:
                transaction.append(Transaction(t["key"], t["value"], t["origin"]))

            self._add_block(Block(block["_index"], 
                                    transaction, 
                                    block["_timestamp"], 
                                    block["_previous_hash"]))  

        return

        
    def add_node(self, peer):
        self.broadcast.add_peer(peer)   

    def _get_ip(self):
        return self._ip

    def _add_block(self,new_block, computed_hash):
        """
        Add a block to the blockchain if it is valid
        Apply longest chain rule
        Constraint: Discard block if the parent is more than 1 generation away
        from the master chain
        """
        #TODO : Check where to add the block

        #Check block validity
        if (not new_block.proof(self._difficulty) or
            not computed_hash == new_block.compute_hash()):
            return False

        #Direct successors of last block from master node
        #Discard block if the parent is more than 1 generation away
        if new_block._previous_hash == self._master_chain[-1].compute_hash():
            self._branch_list.append([new_block])
            print("Block ID {} hash {} added to BRANCH".format(new_block._index, computed_hash[:4]))
            return True

        createBranch = False
        for branch in self._branch_list:

            if createBranch:
                break
            #If parent of new_block is last block of the branch,
            #add it to the branch

            if branch[-1].compute_hash() == new_block._previous_hash:
                branch.append(new_block)
                createBranch = True
                break
            #Else, copy the branch and add the new block to the copy
            for k, block in enumerate(branch):
                if new_block._previous_hash == block.compute_hash():
                    new_branch = copy.deepcopy(branch[:k]).append(new_block)
                    self._branch_list.append(new_branch)
                    createBranch = True
                    break

        max_len_branch = sorted(self._branch_list, key=len)[-1]
        max_len = len(sorted(self._branch_list, key=len)[-1])
        

        #Longest chain rule : branch longer than 2 blocks get added
        if max_len > 2:
            #Add all but one element to the master chain

            self._last_hash = max_len_branch[-1].compute_hash()
            self._master_chain.extend(max_len_branch[:-1])
            #Remove all  but one element from the list of branches
            self._branch_list = [[max_len_branch[-1]]]
            [print("Block ID {} hash {} added to MASTER"
                    .format(block._index, block.compute_hash()[:4]))
                    for block in max_len_branch[:-1]]
            return True
        
        return createBranch
    

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

            #TODO: Confirm when not mining
            if (self._confirm_block and
                self._blocks_to_confirm_hash and
                self._blocks_to_confirm):

                print("Confirming an incoming block...")
                if not self._add_block(self._blocks_to_confirm[-1], self._blocks_to_confirm_hash[-1]):
                    print("Resume mining...")
                    #Block is not valid, we continue mining
                    self._blocks_to_confirm.pop()
                    self._blocks_to_confirm_hash.pop()
                    if self._blocks_to_confirm:
                        self._confirm_block = False

        self._last_hash = computed_hash
        return computed_hash


    def get_blocks(self):
        """ Return all blocks from the chain"""
        # TODO: Return the true blockchain
        return self._master_chain

    def get_last_hash(self):
        """Return the hash of the last block"""
        return self._master_chain[-1].compute_hash()

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

        # print("Added transaction" ,transaction.__dict__)
        self._pending_transactions.append(transaction)

        #TODO: Broadcast transaction to network
        
        return

    def confirm_block(self, block, block_hash):
        """
        Pass a block to be confirmed by the blockchain

        Parameters:
        ----------
        block: Block object
        block_hash: sha256 hash of the Block object
        """
        self._confirm_block = True
        self._blocks_to_confirm.append(block)
        self._blocks_to_confirm_hash.append(block_hash)

    def mine(self):
        """Implements the mining procedure"""

        while(True):
            if not self._pending_transactions:
                time.sleep(1) #Wait before checking new transactions
            else:
                
                input_tr = copy.deepcopy(self._pending_transactions)
                nb_transactions = len(input_tr)
                new_block = Block(index="rand",
                                transactions=input_tr,
                                timestamp=time.time(),
                                previous_hash=self._last_hash)

                #Remove the transactions that were inserted into the block
                del self._pending_transactions[:nb_transactions]
                # print("Processed {} transaction(s) in this block, {} pending".format(nb_transactions, len(self._pending_transactions)))

                # print("Mining....")

                proof = self._proof_of_work(new_block)
                print("Proof" ,proof[:4])
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
                        

                #Current node mined block     
                elif self._add_block(new_block, proof):
                    continue
                else:
                    #Computed proof is not correct, add the transactions back in the pool
                    print("Proof not correct, transactions go back in pool")
                    self._pending_transactions.extend(input_tr)

    def is_valid(self):
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        """
        previous_hash = self.get_last_hash()
        it = -1
        while previous_hash != "0":
            #Check if proof is valid and if previous hashes match
            if(previous_hash != self._master_chain[it-1].compute_hash() or
                not self._master_chain[it].proof(self._difficulty)):
                
                return False
            it = it - 1
            previous_hash = self._master_chain[it]._previous_hash
        
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


if __name__ == '__main__':
    i = 0
    node = Blockchain(2,5000,True)
    while(True):
        transaction1 = Transaction("Team", i,666)
        node.add_transaction(transaction1)
        transaction2 = Transaction("Turing", i,666)
        node.add_transaction(transaction2)
        time.sleep(2)
        print(node.get_blocks())
        i += 10