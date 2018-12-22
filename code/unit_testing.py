import unittest
import time

from blockchain import Blockchain, Block, Transaction

class UnitTestBlockchain(unittest.TestCase):

    def test_bootstrap_blockchain(self):
        blockchain = Blockchain(bootstrap = "127.0.0.1", unitTests=True)
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(len(blockchain.get_blocks()) == 1)

    def test_add_blocks_blockchain(self):
        blockchain = Blockchain(bootstrap = "127.0.0.1", unitTests=True)
        for i in range(20):
            blockchain.add_transaction(Transaction("K"+str(i), "V"+str(i), "P"+str(i)))

        #Mining thread starts by itself
        time.sleep(8)

        #First block get put in branches lsit
        for i in range(21,30):
            blockchain.add_transaction(Transaction("K"+str(i), "V"+str(i), "P"+str(i)))


        time.sleep(8)

        #We mine 2 blocks, but only the last first one gets added to the master branch
        #The other stays in the branches list
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(len(blockchain.get_blocks()) == 2)



if __name__ == '__main__':
    unittest.main()
