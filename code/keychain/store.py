"""
KeyChain key-value store (stub).
"""

from keychain import Blockchain
from keychain import Transaction
from requests import get
import blockchain
import json


# class Callback:
#     def __init__(self, transaction, chain):
#         self._transaction = transaction
#         self._chain = chain

#     def wait(self):
#         """Wait until the transaction appears in the blockchain."""
#         raise NotImplementedError

#     def completed(self):
#         """Polls the blockchain to check if the data is available."""
#         raise NotImplementedError


class Storage:
    
    def __init__(self, bootstrap, miner):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        if miner:
            self.ip = bootstrap
            url = "http://{}:5000/bootstrap".format(self.ip)
            result = get(url)
            if result.status_code != 200:
                print("Unable to connect the bootstrap server")
                return
        else:
            self.ip = get('https://api.ipify.org').text
        

    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.
        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        url = "http://{}:5000/put".format(self.ip)
        result = get(url, data=json.dumps({"key": key, "value": value, "origin": self.ip})).json()
        if result.status_code != 200:
            print("Unable to connect the bootstrap server")
            return
        
        # callback = Callback(transaction, self._blockchain)
        # if block:
        #     callback.wait()

        # return callback

    def retrieve(self, key):
        """Searches the most recent value of the specified key.

        -> Search the list of blocks in reverse order for the specified key,
        or implement some indexing schemes if you would like to do something
        more efficient.
        """
        url = "http://{}:5000/retrieve".format(self.ip)
        result = get(url, data=json.dumps({"key": key})).json()
        if result.status_code != 200:
            print("Unable to connect the bootstrap server")
            return

    def retrieve_all(self, key):
        """Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        url = "http://{}:5000/retrieve_all".format(self.ip)
        result = get(url, data=json.dumps({"key": key})).json()
        if result.status_code != 200:
            print("Unable to connect the bootstrap server")
            return
