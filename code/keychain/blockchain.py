"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import time
import datetime
import json
from hashlib import sha256

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        """Describe the properties of a block."""

        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0

    def proof(self):
        """Return the proof of the current block."""
        raise NotImplementedError

    def get_transactions(self):
        """Returns the list of transactions associated with this block."""
        return self.transactions

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


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


class Blockchain:
    def __init__(self, bootstrap, difficulty):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        address, download the peerlist, and start the bootstrapping procedure.
        """
        raise NotImplementedError

        # Initialize the properties.
        self._blocks = []
        self._peers = []
        self.pending_transactions = []
        self._difficulty = difficulty

        # Initialize the chain with the Genesis block.
        self._add_genesis_block()

        # Bootstrap the chain with the specified bootstrap address.
        self._bootstrap(bootstrap)

    def _add_genesis_block(self):
        """Adds the genesis block to your blockchain."""
        self._blocks.append(Block(0, [], time.time(), "0"))

    def _bootstrap(self, address):
        """Implements the bootstrapping procedure."""
        peer = Peer(address)
        raise NotImplementedError

    def difficulty(self):
        """Returns the difficulty level."""
        return self._difficulty

    def add_transaction(self, transaction):
        """Adds a transaction to your current list of transactions,
        and broadcasts it to your Blockchain network.
        
        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """
        self.pending_transactions.append(transaction)
        raise NotImplementedError

    def mine(self):
        """Implements the mining procedure."""
        raise NotImplementedError

    def is_valid(self):
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        """
        raise NotImplementedError
