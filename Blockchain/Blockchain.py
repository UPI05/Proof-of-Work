from Blockchain.Block import Block
import copy
import json

class Blockchain():
    def __init__(self, lock, shard_id=0):
        self.__lock = lock

        genesis_block = Block()
        genesis_block.genesis(shard_id) # Each shard holds a specific chain

        self.__chain = [genesis_block]

    def resetChain(self, shard_id):
        genesis_block = Block()
        genesis_block.genesis(shard_id)

        self.__chain = [genesis_block]

    def getLastBlockHash(self):
        return self.__chain[len(self.__chain) - 1].getHash()

    def getBlockChain(self):
        res = []
        for i in range(len(self.__chain)):
            res.append({
                f'block_{i}': self.__chain[i].getBlock(),
                f'block_{i}_hash': self.__chain[i].getHash(),
                'producer_sig': self.__chain[i].getSignature()
            })
        return res
    
    def compareChainAndUpdate(self, target_chain):
        # using longest-chain-rule to determine the right chain
        pass

    def addBlock(self, block_str):
        block_json = json.loads(json.loads(block_str).get('data'))
        
        block = Block()
        block.create(block_json.get('txs_list'), block_json.get('preHash'), block_json.get('nOnce'), block_json.get('producer'), block_json.get('timestamp'))
        block.setSignature(json.loads(block_str).get('sig'))

        if self.__chain[len(self.__chain) - 1].getHash() == block_json.get('preHash'):
            with self.__lock:
                self.__chain.append(block)
            return True
        else:
            return False
            
    # Kiểm tra format của Blockchain. Khác với verify bên wallet (kiểm tra mật mã).
    def __validateBlockchain(self):
        # Validate preHash
        for i in range(1, len(self.__chain)):
            if self.__chain[i].getHash() != self.__chain[i - 1].getHash():
                return False
        
        return True