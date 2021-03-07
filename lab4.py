import ledger
import hashlib
import random
import threading
import binascii
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

# Questions
# 1. Are identities different from nodes? Should an identity be able to complete a transaction from any node?
# 2. Are the ledgers stored with the nodes? How to all nodes receive updated ledger?
# 3. Why are there 10 nodes? Are all the nodes verifying transactions?
# 5. How should we go about adding new transactions to the UTP? If two transactions are related to one another, the later transaction should
# not have the opportunity to be verified before its parent.

# *  -------------------------------- * #
# *  Lab 4: Minimum Viable Blockchain * #
# *  -------------------------------- * #

# TODO: Task I: Define a Transaction

publicKeyDatabase = {}
privateKeyDatabase = {} # meant to be inaccessable to the public 
VTP = []

class User:
    def __init__(self, pw):
        self.pw = pw
        key = RSA.generate(2048)
        self.sk = key.export_key(passphrase=pw, pkcs=8, protection="scryptAndAES128-CBC")
        self.pk = key.publickey().export_key()
        self.wallet = []


def createUsers():
    for i in range(10):
        u = User(str(i))
        publicKeyDatabase[i] = u.pk
        privateKeyDatabase[i] = u.sk



def verifySignature(msg, sig, pk):
    decryptor = PKCS1_OAEP.new(pk)
    decrypted = decryptor.decrypt(sig)
    print('Decrypted:', decrypted)
    return msg == decrypted


def verifyNode(ZCBlock):
    nonce = 0

    while(ZCBlock not in VP):
        ZCBlock.nonce = nonce
        curHash = hex(hash(ZCBlock))
        print(curHash)
        
        try:
            if curHash <= 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
                ZCBlock.PW = curHash
                return ZCBlock
        except:
            pass

        nonce += 1

    return None


# TODO: Task II: Create Verifying Nodes
class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.transactionChain = None

    def run(self):
        print(self.name + ' running...')
        while(len(UTP) > 0):
            choice = random.randrange(0,len(UTP))
            try:
                verifiedBlock = verifyNode(UTP[choice])
                if verifiedBlock is not None:
                    UTP.remove(UTP[choice])
                    VTP.append(verifiedBlock)
            except:
                pass

        self.printChain()
    

    def printChain(self):
        print(self.name + ' Transaction Chain:')
        print(self.transactionChain)
        print('---------------------------')




# ! RUN PROGRAM ! #
# Create the userbase
createUsers()

# Create the Unverified Transfer Pool
UTP = generateUTP('transfers.txt')

# Verify values in pool using 10 nodes
for i in range(10):
    c = myThread(i, "Thread " + i)
    c.start()


