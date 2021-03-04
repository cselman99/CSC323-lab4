# Carter Selman

# *  -------------------------------- * #
# *  Lab 4: Minimum Viable Blockchain * #
# *  -------------------------------- * #

# TODO: Task I: Define a Transaction

class ZCBLOCK:
    def __init__(self, transactionID = None, _input = None, _output = None, signatures = None, prevs = None, nonce = 0, PW = None):
        self.transactionID = transactionID
        self._input = _input
        self._output = _output
        self.signatures = signatures
        self.prevs = prevs
        self.nonce = nonce
        self.PW = PW


a = ZCBLOCK(_input='abc')

def transfer():
    pass


def merge():
    pass


def join():
    pass


# TODO: Task II: Create Verifying Nodes



# TODO: Task III: Transaction File



# TODO: Task IV: Simulation Driver
