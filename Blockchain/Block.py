from Blockchain.Transaction import Transaction
import time
import json

class Block():
    def __init__(self):
        self.__num_of_txs = 5
        self.__txs_list = []
        self.__preHash = ""
        self.__producer = ""
        self.__signature = ""
        self.__timestamp = time.time()
    
    def create(self, txs_list, preHash, producer):
        if len(txs_list) != self.__num_of_txs:
            print('Number of txs invalid!!!')
            return

        self.__txs_list = [txs_list]
        self.__preHash = preHash
        self.__producer = producer

    def getBlock(self):
        return json.dumps({
            "timestamp": self.__timestamp,
            "preHash": self.__preHash,
            "txs_list": self.__txs_list,
            "producer": self.__producer
        })
    
    def setSignature(self, sig):
        self.__signature = sig

    def getSignature(self):
        return self.__signature