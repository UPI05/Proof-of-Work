from collections import deque

class TransactionPool:
    def __init__(self):
        self.__mem_pool = deque()

    def getTxsList(self, n):
        txs_list = []
        while self.__mem_pool and len(txs_list) < n:
            txs_list.append(self.__mem_pool.popleft())
        return txs_list
    
    def addTxs(self, txs):
        self.__mem_pool.append(txs)

    def getAll(self):
        return self.__mem_pool