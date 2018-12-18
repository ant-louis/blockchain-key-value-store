"""
KeyChain key-value store (stub).
"""

from keychain import Blockchain
from keychain import Transaction
from requests import get
import blockchain
import json


class Callback:
    def __init__(self, transaction, chain):
        self._transaction = transaction
        self._chain = chain

    def wait(self):
        """Wait until the transaction appears in the blockchain."""
        raise NotImplementedError

    def completed(self):
        """Polls the blockchain to check if the data is available."""
        raise NotImplementedError


class Storage:

    port = 5000
    
    def __init__(self, bootstrap, miner):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        if miner:
            self._ip = bootstrap + ":" + str(Storage.port)

            # Bootstrap
            result = get("http://{}/bootstrap".format(self.get_ip()))
            if result.status_code != 200:
                print("Unable to connect the bootstrap server")
                return
            
            # Mine
            result = get("http://{}:5000/mine".format(self.get_ip()))
            if result.status_code != 200:
                print("Unable to connect the bootstrap server")
                return
        else:
            Storage.port += 1
            self._ip = get('https://api.ipify.org').text + ":" + str(Storage.port)
    
    def get_ip(self):
        """
        Get the ip adress of the user.
        """
        return self._ip
        
    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.
        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        url = "http://{}/put".format(self.get_ip())
        result = get(url, data=json.dumps({"key": key, "value": value, "origin": self.get_ip()}))
        if result.status_code != 200:
            print("Unable to connect the bootstrap server")
            return
        
        # callback = Callback()
        # if block:
        #     callback.wait()

        # return callback

    def retrieve(self, key):
        """Searches the most recent value of the specified key.

        -> Search the list of blocks in reverse order for the specified key,
        or implement some indexing schemes if you would like to do something
        more efficient.
        """
       # Get the blockchain
        url = "http://{}/blockchain".format(self.get_ip())
        result = get(url)
        if result.status_code != 200:
            print("Unable to connect the load blockchain")
            return
        chain = result.json()["chain"]

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
        url = "http://{}/blockchain".format(self.get_ip())
        result = get(url)
        if result.status_code != 200:
            print("Unable to connect the load blockchain")
            return
        chain = result.json()["chain"]

        values = []
        for block in reversed(chain):
            block = json.loads(block)
            for t in reversed(block["_transactions"]):
                if t["key"] == key:
                    values.append(t["value"])
        return values
