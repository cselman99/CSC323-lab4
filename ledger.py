import random
from Output import Output
import binascii
import hashlib
from Crypto.PublicKey import RSA
from GlobalDB import User
import time
from Crypto.Cipher import PKCS1_OAEP
from GlobalDB import UTP
from GlobalDB import VTP
from GlobalDB import userbase
from GlobalDB import compressedUB
# TODO: Task III: Transaction File

# ! Object format:
# NUMBER: the hash of the input, output, and signature fields.
# TYPE: either TRANS, JOIN, or MERGE
# INPUT: a set of transaction numbers
# OUTPUT: a set of (value:public key) pairs
# SIGNATURE: a set of cryptographic signatures on the TYPE, INPUT, and OUTPUT fields

# UTP = None
signatories = {}

class ZCBLOCK:
    def __init__(self, transactionID = None, transactionType = None, _input = None, _output = None, signatures = None, prevs = None, nonce = None, PW = None):
        self.transactionID = transactionID
        self.transactionType = transactionType
        # self._input = _input # [[public_key1,output_id1,amount],[...],...,[public_keyN,NULL,receiving amount]] last one is who receives the money
        self.users = [] # list of public keys [PART ONE OF INPUT]
        self.output_IDs = [] # list of verified transaction IDs [PART TWO OF INPUT]
        self.amounts = [] # list of ammounts to be paid (last one is value paid to last user) [PART THREE OF INPUT]
        self._output = _output # {value:ID}
        self.signature = signatures # [sig1, sig2, ..., sigN]
        self.prevs = prevs 
        self.outputBlock = None

        self.nonce = None 
        self.PW = PW 

    def __repr__(self):
        if self.nonce == None:
            final = "Transaction " + str(self.transactionID) + " | " + self.transactionType + "\n"
        else:
            final = "Transaction " + str(self.transactionID) + " with nonce " + self.nonce + " | " + self.transactionType + "\n"
        for key in self._output:
            final += "\t" + self._output[key] + " gets " + str(key) + "\n"
        return final

def generateTransfers():
    uk = [u for u in compressedUB.keys()]

    t = ["", "", "", "", "", "", "", "", "", ""]

    types = ["GENESIS", "TRANSFER", "TRANSFER", "TRANSFER", "TRANSFER", \
        "MERGE", "JOIN", "TRANSFER", "JOIN", "MERGE"]

    for b in range(10):
        sIndex = 0
        inputs = [
            str(uk[0])+"::25",
            str(uk[0])+":" + t[0] + ":15 " + str(uk[1])+"::15",
            str(uk[1])+":" + t[1] + ":3 " + str(uk[2]) + "::3",
            str(uk[2])+":" + t[2] + ":1 " + str(uk[3]) + "::1",
            str(uk[0])+":" + t[1] + ":2.15 " + str(uk[3]) + "::2.15", 
            str(uk[3])+":" + t[4] + ":2 " + str(uk[3]) + ":" + t[3] + ":1 " + str(uk[2]) + "::3",
            str(uk[2])+":" + t[3] + ":2 " + str(uk[2]) + ":" + t[5] + ":2 " + str(uk[4]) + "::4",
            str(uk[1])+":" + t[2] + ":6 " + str(uk[4]) + "::6",
            str(uk[4])+":" + t[6] + ":4 " + str(uk[4]) + ":" + t[7] + ":6 " + str(uk[2]) + "::10",
            str(uk[0])+":" + t[4] + ":7.85 " + str(uk[3]) + ":" + t[5] + ":0.15 " + str(uk[2]) + ":" + t[8] + ":10 " + str(uk[1]) + "::18"
        ]

        outputs = [
            "25:" + str(uk[0]), 
            "15:" + str(uk[1]) + " 10:" + str(uk[0]), 
            "3:" + str(uk[2]) + " 12:" + str(uk[1]), 
            "1:" + str(uk[3]) + " 2:" + str(uk[2]),
            "2.15:" + str(uk[3]) + " 7.85:" + str(uk[0]), 
            "0.15:" + str(uk[3]) + " 3:" + str(uk[2]),
            "4:" + str(uk[4]) + " 1:" + str(uk[2]),
            "6:" + str(uk[4]) + " 6:" + str(uk[1]),
            "10:" + str(uk[2]),
            "18:" + str(uk[1])
            ]
        
        #endstate: uk[2] has 1 coin, uk[1] has 24 coins
        
        parties = [[], [uk[0]], [uk[1]], [uk[2]], [uk[0]], [uk[3]], [uk[2]], [uk[1]], [uk[4]], [uk[0], uk[3], uk[2]]]
        # UnicodeEncodeError: 'charmap' codec can't encode characters in position 86-87: character maps to <undefined>
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

            if i == b:
                t[b] = transactionID

            result += t[i] + "\n" + types[i] + "\n" + inputs[i] + "\n" \
                + outputs[i] + "\n"
            
            for s in signatures:
                if s is not None:
                    result += str(sIndex) + " "
                    signatories[sIndex] = s
                    sIndex +=1

            result += "\n\n" 
                
    f = open('transfers.txt', 'w')
    f.write(result)
    f.close()


'''
output_database = {}
entry: output_identifier:Output object

inputs: output_id1:public_key:amount, output_id2, ..., outputidN


outID: 10
outID2: 7

MERGE
input: outID:pk:4 outID2:pk:6 NULL:pk:12 

'''

def generateUTP(filename):
    f = open(filename, "r")
    flines = f.read().split('\n')
    f.close()
    # UTP = []
    for i in range(0, len(flines), 6):
        newZCBlock = ZCBLOCK()
        
        # id and type
        if flines[i].strip('\n') == '':
            break

        newZCBlock.transactionID = int(flines[i].strip('\n'), 16)
        newZCBlock.transactionType = flines[i+1].strip('\n')

        # input user_public_key:output_id:secret_key
        inputString = flines[i+2]
        input_list = []
        for userinput in inputString.split(" "):
            # input_list.append(userinput.split(":"))
            split_info = userinput.split(":")
            newZCBlock.users.append(split_info[0])
            newZCBlock.output_IDs.append(split_info[1])
            newZCBlock.amounts.append(split_info[2])
        # newZCBlock._input = input_list
        
        # output
        outputStrings = flines[i+3].strip('\n').split(' ')
        outputDict = {}
        for output in outputStrings:
            separated = output.split(':')
            outputDict[separated[0]] = separated[1]
        newZCBlock._output = outputDict
        
        # signatures
        signatures = flines[i+4].split(' ')
        if len(signatures) > 0 and signatures[0] != '':
            newZCBlock.signature = [int(sig, 16) for sig in signatures if sig != '']
        else:
            newZCBlock.signature = None
        # ValueError: invalid literal for int() with base 16: ''

        # previous block
        if i != 0:
            newZCBlock.prevs = UTP[len(UTP)-1]

        UTP.append(newZCBlock)
    
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

    if compressedUB.get(user) is None:
        print("none")
        return None

    sk = compressedUB[user].sk
    encryptor = PKCS1_OAEP.new(sk)
    encrypted = encryptor.encrypt(str.encode(msg))
    # print("Encrypted:", binascii.hexlify(encrypted))
    return encrypted


    