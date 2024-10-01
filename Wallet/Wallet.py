from Wallet.SignatureScheme import EdDSA
from Blockchain.Transaction import Transaction

class Wallet(EdDSA):
    def createTxs(self, to_addr, data):
        txs = Transaction()
        txs.create(self._getPublicKey(), to_addr, data)
        txs.setSignature(self._sign(txs.getTxs()))
        return txs
    
    def verifyTxs(self, txs):
        return self.verify(txs.getTxs(), txs.getSignature())
    
    def createBlock(self):
        pass

    def verifyBlock(self):
        pass