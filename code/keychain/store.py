from keychain import Blockchain
from keychain import Transaction
import node.py


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

        

        if miner:
            # Bootstrap
            
            
        else:

        

    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.

        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        
    
        
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
        

        

    def retrieve_all(self, key):
        """Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        



    # def retrieve(self, key):
    #     """Searches the most recent value of the specified key.

    #     -> Search the list of blocks in reverse order for the specified key,
    #     or implement some indexing schemes if you would like to do something
    #     more efficient.
    #     """
    #     value = None

    #     for block in reversed(_blockchain):
    #         for transaction in reversed(_blockchain.get_transactions()):
    #             if transaction.key == key:
    #                 value = transaction.value

    #     return value

    # def retrieve_all(self, key):
    #     """Retrieves all values associated with the specified key on the
    #     complete blockchain.
    #     """
    #     values = []

    #     for block in reversed(_blockchain):
    #         for transaction in reversed(_blockchain.get_transactions()):
    #             if transaction.key == key:
    #                 values.append(transaction.value)

    #     return values
