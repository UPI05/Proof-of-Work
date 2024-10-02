from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
from Crypto.Util.number import bytes_to_long, long_to_bytes

class EdDSA:
    ### Focus on hex strings ###
    def __init__(self):
        self.__key = ""
        self.__default_passphrase = "@Hieu Vo"
        self.__curve = "ed25519"
        self.__sig_scheme = "rfc8032"

    def genKey(self):
        self.__key = ECC.generate(curve=self.__curve)

    def saveKey(self, path="privatekey.pem", pwd=None):
        if pwd is None:
            pwd = self.__default_passphrase

        with open(path, "wt") as f:
            data = self.__key.export_key(
                format='PEM',
                passphrase=pwd.encode(),
                protection='PBKDF2WithHMAC-SHA512AndAES256-CBC',
                prot_params={'iteration_count':131072})
            f.write(data)
            f.close()

    def loadKey(self, path="privatekey.pem", pwd=None):
        if pwd is None:
            pwd = self.__default_passphrase
            
        f = open(path, "rt")
        pemKey = ''.join(f.readlines())
        f.close()
        self.__key = ECC.import_key(pemKey, pwd)

    def getPublicKey(self):
        return hex(bytes_to_long(self.__key.public_key().export_key(format='raw')))
    
    def setPublicKey(self, pkey):
        self.__key = eddsa.import_public_key(long_to_bytes(int(pkey, 16)))

    def _sign(self, message):
        signer = eddsa.new(self.__key, self.__sig_scheme)
        return hex(bytes_to_long(signer.sign(message.encode())))

    def _verify(self, message, signature):
        verifier = eddsa.new(self.__key, self.__sig_scheme)
        try:
            signature = long_to_bytes(int(signature, 16))
            verifier.verify(message.encode(), signature)
            return True
        except ValueError:
            return False