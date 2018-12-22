"""
KeyChain key-value store (stub).
"""
from threading import Thread
from time import sleep
import json
import argparse
import subprocess
from requests import get


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
    
    def __init__(self, bootstrap, miner, port = 5000):
        """
        Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        self.blockchain_app = subprocess.Popen(["python" ,"blockchain_app.py", "--miner", str(miner), "--bootstrap", str(bootstrap), "--port", str(port)])
        ip = "127.0.0.1"
        self._address = "{}:{}".format(ip,port)
        sleep(5)

    def put(self, key, value, block=True):
        """
        Puts the specified key and value on the Blockchain.
        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        url = "http://{}/put".format(self._address)
        result = get(url, data=json.dumps({"key": key, "value": value, "origin": self._address}),timeout = 10)
        
        if result.status_code != 200:
            print("Unable to put transaction on the blockchain")
            return
        
        callback = Callback(self, key, value)
        if block:
            callback.wait()
        return callback


    def retrieve(self, key):
        """
        Searches the most recent value of the specified key.

        -> Search the list of blocks in reverse order for the specified key,
        or implement some indexing schemes if you would like to do something
        more efficient.
        """
       # Get the value of the most recent transaction corresponding to key
        url = "http://{}/retrieve".format(self._address)
        result = get(url, data=json.dumps({"key": key}))
        if result.status_code != 200:
            print(result)
            print("Unable to retrieve value from the blockchain")
            return
        return result.json()["value"]


    def retrieve_all(self, key):
        """
        Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        # Get the values of the transactions corresponding to key
        url = "http://{}/retrieve_all".format(self._address)
        result = get(url, data=json.dumps({"key": key}))
        if result.status_code != 200:
            print("Unable to retrieve all values from the blockchain")
            return
        return result.json()["values"]
    
    
    def __del__(self):
        """
        Kill the flask application when the Storage is deleted.
        """
        self.blockchain_app.kill()
