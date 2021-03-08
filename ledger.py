import random
from lab4 import userbase
from Output import Output
import binascii
import hashlib
from Crypto.PublicKey import RSA
from lab4 import User
import time
from Crypto.Cipher import PKCS1_OAEP

# TODO: Task III: Transaction File

# ! Object format:
# NUMBER: the hash of the input, output, and signature fields.
# TYPE: either TRANS, JOIN, or MERGE
# INPUT: a set of transaction numbers
# OUTPUT: a set of (value:public key) pairs
# SIGNATURE: a set of cryptographic signatures on the TYPE, INPUT, and OUTPUT fields

UTP = None

class ZCBLOCK:
    def __init__(self, transactionID = None, transactionType = None, _input = None, _output = None, signatures = None, prevs = None, nonce = None, PW = None):
        self.transactionID = transactionID
        self.transactionType = transactionType
        self._input = _input
        self._output = _output # {value:ID}
        self.signature = signatures # [sig1, sig2, ..., sigN]
        self.prevs = prevs # need?
        self.nonce = None 
        self.PW = PW 


def generateTransfers():
    types = ["GENESIS, ""TRANSFER", "TRANSFER", "TRANSFER", "TRANSFER", \
        "MERGE", "JOIN", "TRANSFER", "JOIN", "MERGE", "TRANSFER"]

    inputs = ["a", "a", "a", "a", "a", "a", "a", "a", "a", "a"]

    outputs = ["25:ID_1", "15:ID_2 10:ID_1", "3:ID_3 12:ID_2", "1:ID_4 2:ID_3",\
        "2.15:ID_4 7.85:ID_1", "MERGE", "JOIN", "2:ID_4 10:ID_2", "JOIN", "MERGE", "0.85:ID_3 7:ID_1"]

    parties = [[], ["1"], ["2"], ["3"], ["1"], ["1", "2"], ["3","4"], ["2"], ["1", "3"], ["2", "4"], ["1"]]

    result = ""
    for i in range(len(types)):
        signatures = []
        for p in parties[i]:
            signatures.append(generateSignature(inputs[i], outputs[i], types[i], p))

        IDVals = inputs[i] + outputs[i]
        
        for s in signatures:
            IDVals += s
        
        transactionID = str(hex(hash(IDVals)))[2:]
        result += transactionID + "\n" + types[i] + "\n" + inputs[i] + "\n"\
            + outputs[i] + "\n"
        
        for s in signatures:
            result += s + " "

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

        # input
        inputString = flines[i+2] #!!!! have to decide formatting (asking professor) 
        
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


def transfer(giver: User, reciever: User, send_amount: float, prior_block: Output):
    total_amount = prior_block.get_value(giver.private_key)
    if total_amount < send_amount:
        raise Exception("Insufficient funds")
    giver_output_amount = total_amount - send_amount
    return Output([giver_output_amount, send_amount], [giver.private_key, reciever.private_key])

def merge(giver: User, reciever: User, send_amount: float, prior_blocks: list):
    total_amount = 0
    for i in range(len(prior_blocks)):
        total_amount += prior_blocks[i].get_value(giver.private_key)
    if total_amount < send_amount:
        raise Exception("Insufficient funds")
    giver_output_amount = total_amount - send_amount
    return Output([giver_output_amount, send_amount], [giver.private_key, reciever.private_key])

'''
givers: list of identities
reciever: the identity who the transaction is directed towards
send_amounts: the total amount that each giver will be contributing
prior_blocs: 2d list- each item is a list of prior_blocks that each user will be using
'''
def join(givers: list, receiver: User, send_amounts: list, total_send_amount: float, prior_blocks: list):
    #check that the send amounts match the total send amount
    if sum(send_amounts) != total_send_amount:
        raise Exception("Unbalenced transfer of funds.")
    # Calculate the sum of the provided blocks and calculate the remaining amounts for each giver
    remaining_amounts = [0]*len(givers)
    actual_total_amount = 0
    for giver in range(len(givers)):
        giver_total = 0
        for pBlock in range(len(prior_blocks[giver])):
            giver_total += prior_blocks[giver][pBlock].get_value(givers[giver].private_key)
        if giver_total < send_amounts[giver]:
            raise Exception("Giver at index "+str(giver)+" has not provided the necessary funds.")
        actual_total_amount += giver_total
        remaining_amounts[giver] = giver_total - send_amounts[giver]
    # make sure that the actual total amount is sufficient
    if actual_total_amount < total_send_amount:
        raise Exception("Insufficent total funds provided")
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


    