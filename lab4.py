import ledger
import hashlib
import random
import threading
import binascii
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
import GlobalDB
import Output
import sys
from Crypto.Hash import SHA256

# Questions
# 1. Are identities different from nodes? Should an identity be able to complete a transaction from any node?
# 2. Are the ledgers stored with the nodes? How to all nodes receive updated ledger?
# 3. Why are there 10 nodes? Are all the nodes verifying transactions?
# 5. How should we go about adding new transactions to the UTP? If two transactions are related to one another, the later transaction should
# not have the opportunity to be verified before its parent.
# 6. what is the "value" in the output and why should a public key be associated with it?

# *  -------------------------------- * #
# *  Lab 4: Minimum Viable Blockchain * #
# *  -------------------------------- * #

'''
TODO:
- there needs to be a place that runs run merge join 
'''

# TODO: Task I: Define a Transaction


# VTP = []
VTP = GlobalDB.VTP
UTP = GlobalDB.UTP

def createUsers():
    for i in range(10):
        u = GlobalDB.User(str(i))
        GlobalDB.publicKeyDatabase[i] = u.pk
        GlobalDB.userbase[u.keyHash] = u
        GlobalDB.compressedUB[i] = u



def verifySignature(msg, sig, pk):
    decryptor = PKCS1_OAEP.new(pk)
    decrypted = decryptor.decrypt(sig)
    print('Decrypted:', decrypted)
    return msg == decrypted


def verifyNode(ZCBlock):
    nonceTracker = set()
    print(ZCBlock)

    while(ZCBlock not in VTP):
        nonce = random.randrange(0, pow(2,256)-1)
        if nonce in nonceTracker:
            continue
        nonceTracker.add(nonce)

        ZCBlock.nonce = nonce
        zcbHash = (str(ZCBlock.transactionID) + ZCBlock.transactionType + str(ZCBlock.users) + str(ZCBlock.signature) + str(ZCBlock.nonce)).encode('utf-8')
        m = SHA256.new()
        m.update(zcbHash)
        curHash = int(m.hexdigest(), 16)
        
        if curHash <= 0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
            print(hex(curHash))
            #0x002a5c6c7ecaadcc9f58600618786c25cb461d990e74327aa1be64d4a98bbc0d
            #0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            ZCBlock.PW = curHash
            return ZCBlock
    return None

def verify_transaction(zcblock):
    output_list = []
    if zcblock.transactionType != "GENESIS":
        #print('not GENESIS')
        for output in zcblock.output_IDs:
            output_list.append(VTP[output].outputBlock)
    if zcblock.transactionType == "GENESIS":
        #print('GENESIS')
        pass
    elif zcblock.transactionType == "TRANSFER":
        #print('TRANSFER')
        ledger.verify_transfer(GlobalDB.compressedUB[zcblock.users[0]], zcblock.amounts[0], output_list[0])
    elif zcblock.transactionType == "MERGE":
        #print('MERGE')
        ledger.verify_merge(GlobalDB.compressedUB[zcblock.users[0]], zcblock.amounts[-1], output_list)
    elif zcblock.transactionType == "JOIN":
        givers = []
        #print('JOIN')
        for i in range(len(zcblock.users)-1):
            givers.append(GlobalDB.compressedUB[zcblock.users[i]])
        ledger.verify_join(givers, zcblock.amounts[:-1], zcblock.amounts[-1], output_list)
    else:
        raise Exception("Invalid transaction type: "+zcblock.transactionType)


# TODO: Task II: Create Verifying Nodes
class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.transactionChain = None

    def run(self):
        print(self.name + ' running...')
        while(len(VTP) < 10):
            try:
                choice = random.randrange(0,len(UTP))
                verify_transaction(UTP[choice])
                verifiedBlock = verifyNode(UTP[choice])
                if verifiedBlock is not None:
                    UTP.remove(UTP[choice])
                    self.process_transaction(verifiedBlock)
                    VTP[verifiedBlock.transactionID] = verifiedBlock
            except Exception as e:
                pass
        
        while(True):
            if GlobalDB.printOrder == self.threadID:
                self.printChain()
                GlobalDB.printOrder += 1
                break
    
    def process_transaction(self, zcblock: ledger.ZCBLOCK):
        output_list = []
        if zcblock.transactionType != "GENESIS":
            for output in zcblock.output_IDs:
                output_list.append(VTP[output].outputBlock)
        if zcblock.transactionType == "GENESIS":
            zcblock.outputBlock = Output.Output(zcblock.amounts, [GlobalDB.compressedUB[zcblock.users[0]]])
        elif zcblock.transactionType == "TRANSFER":
            zcblock.outputBlock = ledger.run_transfer(GlobalDB.compressedUB[zcblock.users[0]], GlobalDB.compressedUB[zcblock.users[1]], zcblock.amounts[0], output_list[0])
        elif zcblock.transactionType == "MERGE":
            zcblock.outputBlock = ledger.run_merge(GlobalDB.compressedUB[zcblock.users[0]], GlobalDB.compressedUB[zcblock.users[1]], zcblock.amounts[-1], output_list)
        elif zcblock.transactionType == "JOIN":
            givers = []
            for i in range(len(zcblock.users)-1):
                givers.append(GlobalDB.compressedUB[zcblock.users[i]])
            zcblock.outputBlock = ledger.run_join(givers, GlobalDB.compressedUB[zcblock.users[-1]], zcblock.amounts[:-1], zcblock.amounts[-1], output_list)
        else:
            raise Exception("Invalid transaction type: "+zcblock.transactionType)
    
    
    def printChain(self):
        print(self.name + "'s Transaction Chain:")
        temp = self.transactionChain
        while temp != None:
            print(temp)
            temp = temp.prevs
        print('---------------------------')

