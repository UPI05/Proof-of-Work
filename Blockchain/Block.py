import time
import json
import hashlib

class Block():
    def __init__(self):
        self.__msg_type = "block"
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

    def createFromStr(self, str):
        block = json.loads(str)
        self.__txs_list = block['txs_list']
        self.__preHash = block['preHash']
        self.__producer = block['producer']
        self.__nOnce = block['nOnce']
        self.__timestamp = block['timestamp']

    def genesis(self, shard_id=0):
        self.create(['0x0000'], str(shard_id), '0x0000', '0x0000', '0x0000')

    def getBlock(self):
        return json.dumps({
            "msg_type": self.__msg_type,
            "timestamp": self.__timestamp,
            "preHash": self.__preHash,
            "txs_list": self.__txs_list,
            "producer": self.__producer,
            "nOnce": self.__nOnce
        })
    
    def getTxsList(self):
        return self.__txs_list
    
    def getHash(self):
        blockStr = self.getBlock()
        hash = hashlib.sha256(blockStr.encode())
        return hash.hexdigest()
    
    def getProducer(self):
        return self.__producer
    
    def setSignature(self, sig):
        self.__signature = sig

    def getSignature(self):
        return self.__signature
    
    # Kiểm tra format của block. Khác với verify bên wallet (kiểm tra mật mã).
    def validateBlock():
        pass