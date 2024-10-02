from collections import deque
import copy

class TransactionPool:
    def __init__(self):
        self.__mem_pool = deque()

    def getTxsList(self, n):
        if len(self.__mem_pool) < n:
            return False, None
        txs_list = []
        while self.__mem_pool and len(txs_list) < n:
            txs_list.append(self.__mem_pool.popleft())
        return True, txs_list
    
    def addTxs(self, txs):
        self.__mem_pool.append(txs)

    def getAllTxs(self):
        return deque(copy.deepcopy(tx) for tx in self.__mem_pool) # clone