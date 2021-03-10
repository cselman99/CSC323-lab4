from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP

class User:
    def __init__(self, pw):
        self.pw = pw
        key = RSA.generate(2048)
        self.sk = key
        #self.skHash = key.export_key(passphrase=pw, pkcs=8, protection="scryptAndAES128-CBC")
        #self.pk = key.publickey().export_key()
        self.pk = key.publickey()
        self.keyHash = key.publickey().export_key()
        self.wallet = []




UTP = []
VTP = {}

printOrder = 0

publicKeyDatabase = {}
userbase = {} # meant to be inaccessable to the public 
compressedUB = {}

