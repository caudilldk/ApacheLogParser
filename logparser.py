# Apache Log Parser and Reverse Lookup
# Created on Jul 4, 2013
# @author: dk

import socket
import optparse
import re
from threading import Thread
from threading import BoundedSemaphore

#Script level variable
ipSet = dict()
        
def listReader(addressPath):
    for line in open(addressPath, 'r'):
        info = line.split("->")
        if len(info) == 2:
            info[1] = info[1].replace('\n', '')
            ipSet[info[0]] = info[1]

def listWriter(addressPath):
    file = open(addressPath, 'w')
    for key in sorted(ipSet.iterkeys(), key=socket.inet_aton):
        file.write("%s->%s\n" % (key, ipSet[key]))
    file.close()

ipRegex = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')    
def logParser(logPath):
    newIPList = set()
    try:
        for line in open(logPath, 'r'):
            try:
                value = re.findall(ipRegex, line)
                ipAddress = value[0]
                #Handles IPs regardless of if they have a PTR or not
                if ipAddress not in ipSet and ipAddress not in newIPList:
                    newIPList.add(ipAddress)
            except:
                pass
        return newIPList
    except IOError:
        print 'Log File not found. This program will now exit'
        return False

def reverseLookup(ipAddress):
    try:
        name,alias,addressList = socket.gethostbyaddr(ipAddress)
        ipSet[ipAddress] = name
    except:
        pass
    finally:
        maxConnection.release()

connections = 100
maxConnection = BoundedSemaphore(value=connections)        
def ipLookup(newIPList, verbose):
    threads = []
    for ipAddress in newIPList:
        if(verbose):
            print ipAddress
        # These lines important for threading
        maxConnection.acquire()
        t = Thread(target=reverseLookup, args=(ipAddress,))
        t.start()
        threads.append(t)
    
    [lookup.join() for lookup in threads]
               
def main():
    parser = optparse.OptionParser('usage%prog -L <log file> -H <address list> -v <verbose mode>')
    parser.add_option('-L', dest='logPath', type='string', help='specify log file')
    parser.add_option('-H', dest='addressPath', type='string', \
        help='specify address list file')
    parser.add_option('-v', dest='verbose', action='store_true', \
        default=False, help='show ip addresses being looked up')
    (options, args) = parser.parse_args()
    logPath = options.logPath
    addressPath = options.addressPath
    verbose = options.verbose
    if logPath == None:
        print parser.usage
        exit(0)
    if addressPath != None:
        listReader(addressPath)
    else:
        # If no address list is given, a new one is generated
        addressPath = 'addressList.txt'
    newIPList = logParser(logPath)
    if(newIPList == False):
        exit()
    print "Log read, now looking up addresses"
    ipLookup(newIPList, verbose)
    listWriter(addressPath)

if __name__ == '__main__':
    main()