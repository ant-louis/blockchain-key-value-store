"""
KeyChain key-value store (stub).
"""
from threading import Thread
from time import sleep
from blockchain import Blockchain, Transaction
from requests import get
from blockchain_app import app
import blockchain_app
import json
import argparse


class Callback:
    def __init__(self, storage, key, value):
        self._storage = storage
        self._key = key 
        self._value = value

    def wait(self):
        """Wait until the transaction appears in the blockchain."""
        timeout = 30
        while(self.completed() != self._value):
            sleep(1)
            timeout -= 1
            if(timeout < 0):
                print("Time out reached in the wait...")
                break

    def completed(self):
        """Polls the blockchain to check if the data is available."""
        return self._storage.retrieve(self._key)
       


class Storage():

    port = 5000
    
    def __init__(self, bootstrap, miner):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        if miner:
            # Set ip address
            Storage.port += 1
            self._address = get('https://api.ipify.org').text + ":" + str(Storage.port)

            # Run the app in a thread
            Thread(target=app.run(debug=True,host=self._address)).start()

            # Bootstrap
            url = "http://{}/bootstrap".format(self._address)
            result = get(url, data=json.dumps({"bootstrap": bootstrap}))
            if result.status_code != 200:
                print("Unable to connect the bootstrap server")
                return
            
            # Mine
            result = get("http://{}/mine".format(self._address))
            if result.status_code != 200:
                print("Unable to mine")
                return
        else:
            # Connect to bootstrap address if simple user
            self._address = bootstrap


    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.
        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        url = "http://{}/put".format(self._address)
        result = get(url, data=json.dumps({"key": key, "value": value, "origin": self._address}))
        if result.status_code != 200:
            print("Unable to put transaction on the blockchain")
            return
        
        callback = Callback(self, key, value)
        if block:
            callback.wait()

        return callback


    def retrieve(self, key):
        """Searches the most recent value of the specified key.

        -> Search the list of blocks in reverse order for the specified key,
        or implement some indexing schemes if you would like to do something
        more efficient.
        """
       # Get the blockchain
        url = "http://{}/blockchain".format(self._address)
        result = get(url)
        if result.status_code != 200:
            print("Unable to reetrieve value from the blockchain")
            return
        chain = result.json()["chain"]

        # Get the value of the most recent transaction corresponding to key
        value = None
        for block in reversed(chain):
            block = json.loads(block)
            for t in reversed(block["_transactions"]):
                if t["key"] == key:
                    value = t["value"]
        return value


    def retrieve_all(self, key):
        """Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        # Get the blockchain
        url = "http://{}/blockchain".format(self._address)
        result = get(url)
        if result.status_code != 200:
            print("Unable to retrieve values from the blockchain")
            return
        chain = result.json()["chain"]
        
        # Get the values of the transactions corresponding to key
        values = []
        for block in reversed(chain):
            block = json.loads(block)
            for t in reversed(block["_transactions"]):
                if t["key"] == key:
                    values.append(t["value"])
        return values
