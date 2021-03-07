import random
from Output import Output
import binascii
import hashlib
from Crypto.PublicKey import RSA
# TODO: Task III: Transaction File

# ! Object format:
# NUMBER: the hash of the input, output, and signature fields.
# TYPE: either TRANS, JOIN, or MERGE
# INPUT: a set of transaction numbers
# OUTPUT: a set of (value:public key) pairs
# SIGNATURE: a set of cryptographic signatures on the TYPE, INPUT, and OUTPUT fields


class ZCBLOCK:
    def __init__(self, transactionID = None, _input = None, _output = None, signatures = None, prevs = None, nonce = None, PW = None):
        self.transactionID = transactionID
        self._input = _input
        self._output = _output
        self.signature = signature
        self.prevs = prevs
        self.nonce = None
        self.PW = PW


def generateUTP(filename, users):
    f = open(filename, "r")
    lines = []
    for line in f:
        lines.append(line)
    f.close()
    UTP = []
    for i in range(round(len(lines) / 4) + 0.5):
        if lines[i * 4] == "TRANSFER\n":
            #giver = users[UTP[int(lines[i * 4 + 1][0])].
            transfer()
        elif lines[i * 4] == "MERGE\n":
            merge()
        elif lines[i * 4] == "JOIN\n":
            join()
        elif i == 0 and lines[i * 4] == "GENESIS\n":
            genesis()
        randTime = random() % 10 / 10
        sleep(randTime * 2)


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
def join(givers: list, receiver: User, send_amounts: list, total_send_amount: float prior_blocks: list):
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
    return Output(remaining_amounts+[total_send_amount], [giver.private_key for giver in givers]+[reciever.private_key])



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

    sk = privateKeyDatabase[user]
    
    encryptor = PKCS1_OAEP.new(sk)
    encrypted = encryptor.encrypt(msg)
    print("Encrypted:", binascii.hexlify(encrypted))
    return encrypted


    