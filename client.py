import socket
from socket import *
import pickle
import sockTrans
from sockTrans import *
import server
from server import *
import os.path
from os import path
import sys

def nothing(msg):
    pass
trace = nothing
#trace = print

class keystoreClient:
    def __init__(self, store: str, ipaddr = ''):
        """Init a client at path for store file `store`.
        `ipaddr` is optional for overriding the address of the 
        server.
        If there exists a lockfile (at store + '.lock'), the lock
        file is read for the server connection info, and the client
        makes a connection.  Otherwise, the client spins up a new
        server from `hostname` or `ipaddr`.
        """
        if len(ipaddr) > 0:
            self.addr = ipaddr
        else:
            self.addr = socket.gethostbyname(socket.gethostname())
        print('creating keystoreClient for ' + os.path.abspath(store))
        self.store = store
        lockfile = store + '.lock'
        if not os.path.exists(lockfile):
            trace('*lockfile not found')
            self.srv = keystoreServer(store, self.addr)
        else:
            trace('*lockfile found')
        self.setSrvInfo()
        self.verifyServer()
        self.beenShutdown = False
        trace('*completed client init')
        
    def verifyServer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                if sock.connect((self.addr, self.port)) == 0:
                    raise RuntimeError('Couldn\'t communicate with server @ ' +
                                       str(self.addr) + ':' + str(self.port) + 
                                       'Perhaps old server didn\'t finish cleanup ' \
                                       '-- try again later')
                else:
                    sockTrans(sock).send(['ping'])
            except ConnectionRefusedError as e:
                print('received ' + str(e))
                print('check for orphaned lockfile (' + self.store + '.lock)')
                sys.exit(1)
                
    def setSrvInfo(self):
        lockfile = self.store + '.lock'
        with open(lockfile, 'rb') as lf:
            addrPort = pickle.load(lf)
            self.addr = addrPort[0]
            self.port = addrPort[1]
            trace('*using ' + self.addr + ":" + str(self.port))
            
    def procResponse(self, resp):
        if resp[0] != 'success':
            if issubclass(type(resp[0]), Exception):
                raise resp[0]
            else:
                raise RuntimeError('received ambiguous response from server:\n' +
                                   str(resp[0]))
            return False
        else:
            return True
        
    def procRequest(self, req):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            trace('*client connect to server at ' + self.addr + ':' + str(self.port))
            sock.connect((self.addr, self.port))
            ssock = sockTrans(sock)
            ssock.send(req)
            trace('*completed socket.sendall in client.put')
            return ssock.recv()
        
    def put(self, key: str, val: any):
        """ Store `val` at `key`
        Can be any type supported by `pickle`
        """
        jval = pickle.dumps(val)
        resp = self.procRequest(['put', key, jval])
        self.procResponse(resp)
        trace('*completed put on client')
    
    def get(self, key: str) -> any:
        """get value at `key`
        Can be any type supported by `pickle`
        """
        resp = self.procRequest(['get', key])
        if(self.procResponse(resp)):
            return pickle.loads(resp[1])
        else:
            return 'shouldNeverHitThis'
        trace('*completed get on client')
        
    def delete(self, key: str):
        """delete entry for `key`
        """
        resp = self.procRequest(['delete', key])
        self.procResponse(resp)
        trace('*completed delete on client')
        
    def size(self):
        """return the number of entries in the store
        """
        resp = self.procRequest(['size'])
        if(self.procResponse(resp)):
            return resp[1]
        else:
            return 'shouldNeverHitThis'
        
    def shutdown(self):
        """shutdown the server, if it was created by this client
        """
        if 'srv' in self.__dict__:
            self.srv.shutdown()
        self.beenShutdown = True
        trace('*completed keystoreClient shutdown')
        
    def __del__(self):
        if(hasattr(self, 'beenShutdown') and not self.beenShutdown):
            self.shutdown()
        trace('*destroyed keystoreClient.')

        
