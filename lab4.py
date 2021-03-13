import ledger
import hashlib
import random
import binascii
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
import GlobalDB
import Output
from Crypto.Hash import SHA256
from threading import Lock
import sys


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
data_lock = Lock()

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
    while(ZCBlock not in GlobalDB.VTP):
        nonce = random.randrange(0, pow(2,256)-1)
        if nonce in nonceTracker:
            continue
        nonceTracker.add(nonce)
        ZCBlock.nonce = nonce

        zcbHash = (str(ZCBlock.transactionID) + ZCBlock.transactionType + str(ZCBlock.users) + str(ZCBlock.signature) + str(ZCBlock.nonce)).encode('utf-8')
        m = SHA256.new()
        m.update(zcbHash)
        # curHash = m.hexdigest()
        # print("Hash"+curHash)
        curHash = int(m.hexdigest(), 16)

        # if curHash <= 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
        if curHash <=0x000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
            #print(curHash)
            # print("returning zcblock")
            # return ZCBlock
            return nonce, curHash
    # print("returning None")
    return None, None

def verify_transaction(zcblock):
    # print('verifying transaction')
    output_list = []
    #print("VTP: "+VTP)
    if zcblock.transactionType != "GENESIS":
        for output in zcblock.output_IDs[:-1]:
            # print("output IDS:")
            # print([hex(c) for c in zcblock.output_IDs])
            # #['0x65fd319d552e9fd4', '0x49d7077a6192557a', '0x4211654c954883c8', '0x0']
            # print("------------")
        # for output in zcblock.output_IDs:
            output_list.append(GlobalDB.VTP[output].outputBlock)
        output_list = [o for o in output_list if o is not None]
        # print("Output:", output_list)
        # print("transaction:", hex(zcblock.transactionID))
        #Output: [Private RSA key at 0x1C2FC8637C0:7.85, Private RSA key at 0x1C2FC9062E0:2.15, Private RSA key at 0x1C2FC9062E0:0.1499999999999999, Private RSA key at 0x1C2FC9062E0:3.0, Private RSA key at 0x1C2FC906520:-4.0, Private RSA key at 0x1C2FC906520:10.0]
        # transaction: 0x382cb270c1763a97
        #[Private RSA key at 0x1844F25A790:7.85, Private RSA key at 0x1844F263FA0:2.15, Private RSA key at 0x1844F263FA0:0.1499999999999999, Private RSA key at 0x1844F263FA0:3.0, None]

    if zcblock.transactionType == "GENESIS":
        #print("verified")
        # zcblock.outputBlock = Output(zcblock.amounts, [compressedUB[zcblock.users[0]]])
        pass
    elif zcblock.transactionType == "TRANSFER":
        #print('a')
        ledger.verify_transfer(GlobalDB.compressedUB[zcblock.users[0]], zcblock.amounts[0], output_list[0])
        #print('b')
    elif zcblock.transactionType == "MERGE":
        #print('a')
        ledger.verify_merge(GlobalDB.compressedUB[zcblock.users[0]], zcblock.amounts[-1], output_list)
        #print('b')
    elif zcblock.transactionType == "JOIN":
        givers = []
        #print('d')
        for i in range(len(zcblock.users)-1):
            givers.append(GlobalDB.compressedUB[zcblock.users[i]])
        #print('e')
        #print()
        ledger.verify_join(givers, zcblock.amounts[:-1], zcblock.amounts[-1], output_list)
        #print('f')
    else:
        raise Exception("Invalid transaction type: "+zcblock.transactionType)


def run(name, threadID):
    print(name + ' running...')
    #print("VTP: " + str(GlobalDB.VTP))
    #print("UTP:", GlobalDB.UTP)
    #print("VTP:", GlobalDB.VTP)
    oldVTPlen = len(GlobalDB.VTP)
    transactionChain = []
    while(len(GlobalDB.VTP) < 10 and len(GlobalDB.UTP) > 0):
        #print(GlobalDB.UTP)
        choice = random.randrange(0,len(GlobalDB.UTP))
        if len(GlobalDB.VTP) > oldVTPlen:
            transactionChain.append(list(GlobalDB.VTP.keys())[-1])
            oldVTPlen = len(GlobalDB.VTP)
        try:
            #if len(GlobalDB.UTP) == 10: print('10')
            #print("UTP"+str(len(GlobalDB.UTP)))
            #sys.stdout.flush()
            choice = random.randrange(0, len(GlobalDB.UTP))
            block = GlobalDB.UTP[choice]
            verify_transaction(block)
            #verifiedBlock = verifyNode(UTP[choice])
            newnonce, curHash = verifyNode(block)
            
            if (newnonce is not None) and (curHash is not None):
                with data_lock:
                    try:
                        #print(VTP)
                        # print("Thread: "+str(self.threadID))
                        print(block.transactionType)
                        GlobalDB.UTP.remove(GlobalDB.UTP[choice])
                        
                        try:
                            process_transaction(block)
                        except:
                            #print("damn it")
                            pass
                        # print('processed...')
                        # print("key length: "+str(len(block.outputBlock.keys)))
                        block.PW = curHash
                        block.nonce = newnonce
                        
                        v = {block.transactionID: block}
                        GlobalDB.VTP.update(v)
                        # print("transaction processed")
                        tmp = [str(hex(k)) for k in GlobalDB.VTP.keys()]
                        #print(tmp)
                        # VTP[verifiedBlock.transactionID] = verifiedBlock
                        # print("VTP updated")
                        # print(VTP[verifiedBlock.transactionID])
                        #print('---')
                        #print("VTP: "+str(len(VTP)))
                        #print(hex(list(VTP.keys())[0]))
                        #print("---")
                        #print(VTP)
                        #print("---")
                    except Exception as e:
                        tb = sys.exc_info()[2]
                        print("EXCEPTION THROWN:\/")
                        print(e.with_traceback(tb))
        except Exception as e:
            # tb = sys.exc_info()[2]
            # print("EXCEPTION THROWN:\/")
            # print(e.with_traceback(tb))
            pass
        
    while True:
        #print('time to print!!!')
        if GlobalDB.printOrder == threadID:
            printChain(name, transactionChain)
            GlobalDB.printOrder += 1
            break


# TODO: Task II: Create Verifying Nodes
def process_transaction(zcblock: ledger.ZCBLOCK):
    #print('processing -----'+zcblock.transactionType)
    output_list = []
    if zcblock.transactionType != "GENESIS":
        for output in zcblock.output_IDs[:-1]:
            #print("PROCESS")
            #print(type(output))
            output_list.append(GlobalDB.VTP[output].outputBlock)
        output_list = [o for o in output_list if o is not None]
        if len(output_list) == 0:
            raise Exception("Number of incoming transactions must be greater than 0.")

            #print('here2')
    #print('processing: '+str(zcblock.transactionType))
    if zcblock.transactionType == "GENESIS":
        genOutput = Output.Output(zcblock.amounts, [GlobalDB.compressedUB[zcblock.users[0]].sk])
        zcblock.outputBlock = genOutput
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
        print("excpetion raise time >:(")
        raise Exception("Invalid transaction type: "+zcblock.transactionType)
    
    
def printChain(name, transactionChain):
    print('\n\n'+name + "'s Transaction Chain:")
    temp = transactionChain
    for i in temp:
        print(hex(i))
    # while temp != None:
    #     print(temp)
    #     temp = temp.prevs
    print('---------------------------')

