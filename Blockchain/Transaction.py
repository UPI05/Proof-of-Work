import json

class Transaction:
    def __init__(self):
        self.__msg_type = "txs"
        self.__from = ""
        self.__to = ""
        self.__data = ""
        self.__signature = ""
        self.__timestamp = 0

    def create(self, from_addr, to_addr, data, timestamp): # hex str, hex str, str
        self.__from = from_addr
        self.__to = to_addr
        self.__data = data
        self.__timestamp = timestamp

    def createFromStr(self, str):
        txs = json.loads(str)
        self.__from = txs['from']
        self.__to = txs['to']
        self.__data = txs['data']
        self.__timestamp = txs['time']

    def getTxs(self):
        return json.dumps({
            "msg_type": self.__msg_type, 
            "from": self.__from,
            "to": self.__to,
            "data": self.__data,
            "time": self.__timestamp
        })
    
    def getProducer(self):
        return self.__from

    def setSignature(self, sig):
        self.__signature = sig

    def getSignature(self):
        return self.__signature
    
    # Kiểm tra format của txs. Khác với verify bên wallet (kiểm tra mật mã).
    def validateTxs():
        # is spent?
        pass