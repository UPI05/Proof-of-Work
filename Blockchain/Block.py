import time
import json
import hashlib

class Block():
    def __init__(self):
        self.__txs_list = []
        self.__preHash = ""
        self.__nOnce = 0
        self.__producer = ""
        self.__signature = ""
        self.__timestamp = 0
    
    def create(self, txs_list, preHash, nOnce, producer, timestamp):
        self.__txs_list = txs_list
        self.__preHash = preHash
        self.__producer = producer
        self.__nOnce = nOnce
        self.__timestamp = timestamp

    def genesis(self):
        self.create(['0x0123'], '0x4567', '0x89ab', '0xcdef', '0x0000')

    def getBlock(self):
        return json.dumps({
            "timestamp": self.__timestamp,
            "preHash": self.__preHash,
            "txs_list": self.__txs_list,
            "producer": self.__producer,
            "nOnce": self.__nOnce
        })
    
    def getHash(self):
        blockStr = self.getBlock()
        hash = hashlib.sha256(blockStr.encode())
        return hash.hexdigest()
    
    def setSignature(self, sig):
        self.__signature = sig

    def getSignature(self):
        return self.__signature
    
    # Kiểm tra format của block. Khác với verify bên wallet (kiểm tra mật mã).
    def validateBlock():
        pass