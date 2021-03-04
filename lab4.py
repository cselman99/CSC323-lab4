import hashlib
import threading
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

# Questions
# 1. Are identities different from nodes? Should an identity be able to complete a transaction from any node?
# 2. Are the ledgers stored with the nodes? How to all nodes receive updated ledger?
# 3. Why are there 10 nodes? Are all the nodes verifying transactions?
# 4. How do we hash the message with key? Concatination?

# *  -------------------------------- * #
# *  Lab 4: Minimum Viable Blockchain * #
# *  -------------------------------- * #

# TODO: Task I: Define a Transaction

counter = 0

class ZCBLOCK:
    def __init__(self, transactionID = None, _input = None, _output = None, signatures = None, prevs = None, nonce, PW = None):
        self.transactionID = transactionID
        self._input = _input
        self._output = _output
        self.signatures = signatures
        self.prevs = prevs
        self.nonce = counter
        counter += 1
        self.PW = PW


class User:
    def __init__(self, pw):
        self.pw = pw
        key = RSA.generate(2048)
        self.sk = key.export_key(passphrase=pw, pkcs=8, protection="scryptAndAES128-CBC")
        self.pk = key.publickey().export_key()


def verify(message, signature, pk):
    pass


def transfer():
    pass


def merge():
    pass


def join():
    pass


def generateTransactionNumber(input, output, signature):
    pass

# TODO: Task II: Create Verifying Nodes




