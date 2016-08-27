import string
import time
import random
import hashlib
import pyopencl as cl
import numpy as np
import scipy as sp
from multiprocessing import Process, Queue



def multicoregpu():
    print "what?"


def multicorecpu():
    # ----- User Options ----- #
    keyBitLength = 24
    numTestSubjects = 40000000
    numCores = 6
    # --- End User Options --- #



    q = Queue()
    hashProcesses = {}

    splitSubs = numTestSubjects / numCores

    for i in range(numCores):
        hashProcesses[i] = Process(target=genHashDict, args=(q, splitSubs, keyBitLength, i))
        hashProcesses[i].start()
        time.sleep(0.2)



    storedHash = {}
    for i in range(numCores):
        storedHash.update(q.get())

    print " --- Combining Dictionaries: DONE --- "
    print " --- Total Size: " + str(len(storedHash))
    print " --- Collisions: " + str(numTestSubjects - len(storedHash))




    for i in range(numCores):
        bruteProcesses = {}
        process = Process(target=bruteJob, args=(q, storedHash, keyBitLength, i))
        process.start()
        bruteProcesses[i] = process



def genHashDict(q, numTestSubjects, keyBitLength, id):

    random.seed(hashlib.sha1(str(id + time.time())).hexdigest())

    storedHash = {}

    print " --- Starting Keygen Num: " + str(id) + " --- "

    # Generate dictionary of entries for collision detection (limited to conserve memory)
    for i in range(numTestSubjects):

        currKey = random.getrandbits(keyBitLength)
        currHash =  hashlib.sha1(str(currKey)).hexdigest()

        if storedHash.has_key(currHash) == False:
            storedHash[currHash] = currKey


    print " !!! Finished Keygen Num: " + str(id) + " !!! "

    q.put(storedHash)



def bruteJob(q, storedHash, keyBitLength, id):

    random.seed(hashlib.sha1(str(id + time.time())).hexdigest())

    print " --- Starting Brute Force Num: " + str(id) + " --- "

    cracked = False

    while cracked != True:
        # Generate a random key and hash for testing
        currKey = random.getrandbits(keyBitLength)
        currHash =  hashlib.sha1(str(currKey)).hexdigest()

        # See if generated key is present in dictionary, if it is we are finished.
        if storedHash.has_key(currHash):
            print " ---- Collision Detected ---- "
            print "First Key:   " + str(currKey)
            print "Target Hash: " + str(currHash)
            print "             ----             "
            print "Second Key:  " + str(storedHash[currHash])
            print "Second Hash: " + str(currHash)
            print " ---------------------------- "

            cracked = True

            print " !!! Finished Brute Force Num: " + str(id) + " !!! "

            q.put("Done!")



multicorecpu()