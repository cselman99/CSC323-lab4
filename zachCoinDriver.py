import lab4
import ledger
from threading import Thread
import GlobalDB


# ! RUN PROGRAM ! #
# Create the userbase
lab4.createUsers()

# Create the Unverified Transfer Pool
ledger.generateTransfers()
ledger.generateUTP('transfers.txt')

#print(GlobalDB.UTP)
VTP = {}

names = ["Thread 1", "Thread 2", "Thread 3", "Thread 4", "Thread 5", \
   "Thread 6", "Thread 7", "Thread 8", "Thread 9", "Thread 10"]

lab4.run(names[0], 0)
# Verify values in pool using 10 nodes
# t = Thread(target=lab4.run, args=(names[0], 0, VTP, UTP))
# t.start()
# #c = lab4.myThread(i, "Thread " + str(i))
# t1 = Thread(target=lab4.run, args=(names[1], 1, VTP, UTP))
# t1.start()

# t2 = Thread(target=lab4.run, args=(names[2], 2, VTP, UTP))
# t2.start()

# t3 = Thread(target=lab4.run, args=(names[3], 3, VTP, UTP))
# t3.start()

# t4 = Thread(target=lab4.run, args=(names[4], 4, VTP, UTP))
# t4.start()

# t5 = Thread(target=lab4.run, args=(names[5], 5, VTP, UTP))
# t5.start()
# #c = lab4.myThread(i, "Thread " + str(i))
# t6 = Thread(target=lab4.run, args=(names[6], 6, VTP, UTP))
# t6.start()

# t7 = Thread(target=lab4.run, args=(names[7], 7, VTP, UTP))
# t7.start()

# t8 = Thread(target=lab4.run, args=(names[8], 8, VTP, UTP))
# t8.start()

# t9 = Thread(target=lab4.run, args=(names[9], 9, VTP, UTP))
# t9.start()
   

#t.join()
# t1.join()
# t2.join()
# t3.join()
# t4.join()
# t5.join()
# t6.join()
# t7.join()
# t8.join()
# t9.join()
