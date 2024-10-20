from collections import deque
import copy
import threading

class TransactionPool:
    def __init__(self, lock):
        self.__mem_pool = deque()
        self.__lock = lock

    def getTxsList(self, n):
        mem_pool = self.getAllTxs()
        if len(mem_pool) < n:
            return False, None
        txs_list = []
        while mem_pool and len(txs_list) < n:
            txs_list.append(mem_pool.popleft())
        return True, txs_list
    
    def addTxs(self, txs):
        with self.__lock:
            self.__mem_pool.append(txs)

    def removeTxs(self, txs):
        with self.__lock:
            self.__mem_pool.remove(txs)

    def _findTxs(self, txs):
        if txs in self.__mem_pool:
            return True
        return False

    def getAllTxs(self):
        with self.__lock:
            return deque(copy.deepcopy(tx) for tx in self.__mem_pool) # clone