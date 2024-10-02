from Wallet.SignatureScheme import EdDSA
from Blockchain.Transaction import Transaction
from Blockchain.Block import Block

class Wallet(EdDSA):
    def createTxs(self, to_addr, data):
        txs = Transaction()
        txs.create(self.getPublicKey(), to_addr, data)
        txs.setSignature(self._sign(txs.getTxs()))
        return txs
    
    def verifyTxs(self, txs):
        return self._verify(txs.getTxs(), txs.getSignature())
    
    def createBlock(self, preHash, txs_list, nOnce):
        block = Block()
        block.create(txs_list, preHash, nOnce, self.getPublicKey())
        block.setSignature(self._sign(block.getBlock()))
        return block
    
    def verifyBlock(self):
        pass