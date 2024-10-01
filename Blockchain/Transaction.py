import json
import time

class Transaction:
    def __init__(self):
        self.__from = ""
        self.__to = ""
        self.__data = ""
        self.__signature = ""
        self.__timestamp = time.time()

    def create(self, from_addr, to_addr, data): # hex str, hex str, str
        self.__from = from_addr
        self.__to = to_addr
        self.__data = data

    def getTxs(self):
        return json.dumps({
            "from": self.__from,
            "to": self.__to,
            "data": self.__data,
            "time": self.__timestamp
        })

    def setSignature(self, sig):
        self.__signature = sig

    def getSignature(self):
        return self.__signature