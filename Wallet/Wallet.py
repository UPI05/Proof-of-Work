from Wallet.SignatureScheme import EdDSA
from Blockchain.Transaction import Transaction
from Blockchain.Block import Block
import time
import json

class Wallet(EdDSA):
    def createTxs(self, to_addr, data):
        txs = Transaction()
        txs.create(self.getPublicKey(), to_addr, data, time.time())
        txs.setSignature(self._sign(txs.getTxs()))
        return txs
    
    def verifyTxs(self, txs):
        return self._verify(txs.getTxs(), txs.getSignature())
    
    def createBlock(self, preHash, txs_list, nOnce):
        block = Block()
        block.create(txs_list, preHash, nOnce, self.getPublicKey(), time.time())
        block.setSignature(self._sign(block.getBlock()))
        return block
    
    def verifyBlock(self, block):
        tmp_wallet = Wallet()
        for txs_str in block.getTxsList():
            txs = Transaction()
            txs.createFromStr(json.loads(txs_str)['data'])
            txs.setSignature(json.loads(txs_str)['sig'])
            tmp_wallet.setPublicKey(txs.getProducer())
            if not tmp_wallet.verifyTxs(txs):
                return False

        return self._verify(block.getBlock(), block.getSignature())