import lab4
import ledger

# ! RUN PROGRAM ! #
# Create the userbase
lab4.createUsers()

# Create the Unverified Transfer Pool
ledger.generateTransfers()
UTP = ledger.generateUTP('transfers.txt')

print(UTP)

# Verify values in pool using 10 nodes
#for i in range(10):
#    c = lab4.myThread(i, "Thread " + i)
#    c.start()
