import random
from lab4 import userbase
from Output import Output
import binascii
import hashlib
from Crypto.PublicKey import RSA
from lab4 import User
import time
from Crypto.Cipher import PKCS1_OAEP
import UTP
# TODO: Task III: Transaction File

# ! Object format:
# NUMBER: the hash of the input, output, and signature fields.
# TYPE: either TRANS, JOIN, or MERGE
# INPUT: a set of transaction numbers
# OUTPUT: a set of (value:public key) pairs
# SIGNATURE: a set of cryptographic signatures on the TYPE, INPUT, and OUTPUT fields

# UTP = None

class ZCBLOCK:
    def __init__(self, transactionID = None, transactionType = None, _input = None, _output = None, signatures = None, prevs = None, nonce = None, PW = None):
        self.transactionID = transactionID
        self.transactionType = transactionType
        self._input = _input # [[public_key1,output_id1,secretkey1],[...],...] last one is who receives the money
        self._output = _output # {value:ID}
        self.signature = signatures # [sig1, sig2, ..., sigN]
        self.prevs = prevs 
        self.nonce = None 
        self.PW = PW 

    def __repr__(self):
        final = "Transaction " + str(self.transactionID) + " with nonce " + self.nonce + "\n"
        for key in self._output:
            final += "\t" + str(key) + " gets " + self._output[key] + "\n"
        return final

def generateTransfers():
    types = ["GENESIS", "TRANSFER", "TRANSFER", "TRANSFER", "TRANSFER", \
        "MERGE", "JOIN", "TRANSFER", "JOIN", "MERGE"]

    inputs = ["", "pk:ID:sk", "pk:ID:sk", "pk:ID:sk", "pk:ID:sk", "pk:ID:sk pk:ID:sk", "pk:ID:sk", "pk:ID:sk", "pk:ID:sk", "pk:ID:sk"]

    outputs = ["25:ID_1", "15:ID_2 10:ID_1", "3:ID_3 12:ID_2", "1:ID_4 2:ID_3",\
        "2.15:ID_4 7.85:ID_1", "25:ID_1 25:ID_1", "25:ID_1 25:ID_1", "2:ID_4 10:ID_2", "2:ID_4 10:ID_2", "2:ID_4 10:ID_2", "0.85:ID_3 7:ID_1"]

    uk = [u for u in userbase.keys()]
    parties = [[], [uk[0]], [uk[1]], [uk[2]], [(uk[0])], [uk[0], uk[1]], [uk[2],uk[3]], [uk[1]], [uk[0], uk[2]], [uk[1], uk[3]], [uk[0]]]

    result = ""
    for i in range(len(types)):
        signatures = []
        for p in parties[i]:
            tmp = generateSignature(inputs[i], outputs[i], types[i], p)
            signatures.append(tmp)

        IDVals = str.encode(inputs[i]) + str.encode(outputs[i])
        
        for s in signatures:
            if s is not None:
                IDVals += s
        
        transactionID = str(hex(hash(IDVals)))
        result += transactionID + "\n" + types[i] + "\n" + inputs[i] + "\n"\
            + outputs[i] + "\n"
        
        for s in signatures:
            if s is not None:
                result += "temp" + " "

        result += "\n\n" 
        
    f = open('transfers.txt', 'w')
    f.write(result)
    f.close()

# generateTransfers()

'''
output_database = {}
entry: output_identifier:Output object

inputs: output_id1, output_id2, ..., outputidN
'''

def generateUTP(filename):
    f = open(filename, "r")
    flines = f.read().split('\n')
    f.close()
    UTP = []
    for i in range(0, len(flines), 6):
        newZCBlock = ZCBLOCK()
        
        # id and type
        newZCBlock.transactionID = int(flines[i].strip('\n'), 16)
        newZCBlock.transactionType = flines[i+1].strip('\n')

        # input user_public_key:output_id:secret_key
        inputString = flines[i+2]
        input_list = []
        for userinput in inputString.split(" "):
            input_list.append(userinput.split(":"))
        newZCBlock._input = input_list
        
        # output
        outputStrings = flines[i+3].strip('\n').split(' ')
        outputDict = {}
        for output in outputStrings:
            separated = output.split(':')
            outputDict[separated[0]] = separated[1]
        newZCBlock._output = outputDict
        
        # signatures
        signatures = flines[i+4].spit(' ')
        newZCBlock.signature = [int(sig, 16) for sig in signatures]

        # previous block
        if i != 0:
            newZCBlock.prevs = UTP[len(UTP)]

        # need to decide how inputs are defined before this is completed
        # call these functions after they have been verified???
        # if newZCBlock.transactionType == 'GENESIS':
        #     pass
        # elif newZCBlock.transactionType == 'TRANSFER':
        #     transfer()
        # elif newZCBlock.transactionType == 'MERGE':
        #     merge()
        # elif newZCBlock.transactionType == 'JOIN':
        #     join()
        # else:
        #     raise Exception("Invalid transaction type: "+newZCBlock.transactionType)



        UTP.append(newZCBlock)
        
        
        
        
    # lines = []
    # for line in f.read:
    #     lines.append(line)
    # f.close()
    # UTP = []
    # for i in range(round(len(lines) / 4) + 0.5):
    #     if lines[i * 4] == "TRANSFER\n":
    #         #giver = users[UTP[int(lines[i * 4 + 1][0])].
    #         u = userbase[]
    #         transfer()
    #     elif lines[i * 4] == "MERGE\n":
    #         merge()
    #     elif lines[i * 4] == "JOIN\n":
    #         join()
    #     elif i == 0 and lines[i * 4] == "GENESIS\n":
    #         genesis()
    #     randTime = random.random()
    #     time.sleep(randTime * 2)
    return UTP


def verify_transfer(giver: User, send_amount: float, prior_block: Output):
    total_amount = prior_block.check_value(giver.private_key)
    if total_amount == None:
        raise Exception("No funds for the user exist with this block.")
    if total_amount < send_amount:
        raise Exception("Insufficient funds")

def run_transfer(giver: User, reciever: User, send_amount: float, prior_block: Output):
    total_amount = prior_block.get_value(giver.private_key)
    giver_output_amount = total_amount - send_amount
    return Output([giver_output_amount, send_amount], [giver.private_key, reciever.private_key])

def verify_merge(giver: User, send_amount: float, prior_blocks: list):
    total_amount = 0
    for i in range(len(prior_blocks)):
        total_amount += prior_blocks[i].check_value(giver.private_key)
    if total_amount < send_amount:
        raise Exception("Insufficient funds")
    
def run_merge(giver: User, reciever: User, send_amount: float, prior_blocks: list):
    total_amount = 0
    for i in range(len(prior_blocks)):
        total_amount += prior_blocks[i].get_value(giver.private_key)
    giver_output_amount = total_amount - send_amount
    return Output([giver_output_amount, send_amount], [giver.private_key, reciever.private_key])

'''
givers: list of identities
reciever: the identity who the transaction is directed towards
send_amounts: the total amount that each giver will be contributing
prior_blocs: 2d list- each item is a list of prior_blocks that each user will be using
'''
def verify_join(givers: list, send_amounts: list, total_send_amount: float, prior_blocks: list):
    if sum(send_amounts) != total_send_amount:
        raise Exception("Unbalanced transfer of funds.")
    remaining_amounts = [0]*len(givers)
    actual_total_amount = 0
    for giver in range(len(givers)):
        giver_total = 0
        for pBlock in range(len(prior_blocks[giver])):
            giver_total += prior_blocks[giver][pBlock].check_value(givers[giver].private_key)
        if giver_total < send_amounts[giver]:
            raise Exception("Giver at index "+str(giver)+" has not provided the necessary funds.")
        actual_total_amount += giver_total
        remaining_amounts[giver] = giver_total - send_amounts[giver]
    if actual_total_amount < total_send_amount:
        raise Exception("Insufficent total funds provided")

def run_join(givers: list, receiver: User, send_amounts: list, total_send_amount: float, prior_blocks: list):
    remaining_amounts = [0]*len(givers)
    actual_total_amount = 0
    for giver in range(len(givers)):
        giver_total = 0
        for pBlock in range(len(prior_blocks[giver])):
            giver_total += prior_blocks[giver][pBlock].get_value(givers[giver].private_key)
        actual_total_amount += giver_total
        remaining_amounts[giver] = giver_total - send_amounts[giver]
    return Output(remaining_amounts+[total_send_amount], [giver.private_key for giver in givers]+[receiver.private_key])



def generateTransactionNumber(i, o, s):
    oRepr = str(o)
    sRepr = ''
    for m in s:
        sRepr += m

    iRepr = ''
    for m in i:
        iRepr += m

    return hex(hash(iRepr + oRepr + sRepr))


def generateSignature(i, o, t, user):
    oRepr = str(o)
    iRepr = ''
    for m in i:
        iRepr += m
    msg = iRepr + oRepr + t

    if userbase.get(user) is None:
        return None

    sk = userbase[user].sk
    
    encryptor = PKCS1_OAEP.new(sk)
    encrypted = encryptor.encrypt(msg)
    print("Encrypted:", binascii.hexlify(encrypted))
    return encrypted


    