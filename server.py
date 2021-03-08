import socketserver
import sockTrans
from sockTrans import *
import socket
import pickle
import os.path
from os import path
import threading

def nothing(msg):
    pass
trace = nothing
#trace = print

class keystoreHandler(socketserver.BaseRequestHandler):
    def setup(self):
        trace('**creating keystoreHandler and init sockTrans object')
        self.sock = sockTrans(self.request)

    def get(self, req):
        trace('**entered get in keystoreHandler')
        try:
            val = keystoreServer.get(req[1])
        except KeyError as err:
            self.sock.send([err])
            return
        self.sock.send(['success', val])

    def put(self, req):
        trace('**putting')
        msg = ['success']
        keystoreServer.put(req[1],req[2])
        self.sock.send(msg)
        
    def delete(self, req):
        trace('**delete')
        msg = ['success']
        try:
            keystoreServer.delete(req[1])
        except Exception as err:
            msg = [err]
        self.sock.send(msg)
        
    def size(self, req):
        trace("size")
        size = keystoreServer.size()
        self.sock.send(['success', size])
        
    def ping(self, req):
        trace('got ping from client ' + str(self.client_address))
        
    def handle(self):
        trace('**entering handle from client ' + str(self.client_address))
        commands = {
            'get' : self.get,
            'put' : self.put,
            'delete' : self.delete,
            'size' : self.size,
            'ping' : self.ping
        }
        req = self.sock.recv()
        commands[req[0]](req)
        
    def __del__(self):
        trace('**destroyed handle (server request)')
        
class myLock:
    def __init__(self):
        if(hasattr(self, 'id')):
            self.id +=1
        else:
            self.id = 0
        self.lock = threading.Lock()
    def __enter__(self):
        self.acquire()
    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
    def acquire(self):
        trace("acquired lock on " + str(self.id))
        return self.lock.acquire()
    def release(self):
        trace("releasing lock on " + str(self.id))
        self.lock.release()
        trace("lock released on " + str(self.id))
    def __del__(self):
        trace("destroying lock " + str(self.id))
            
class keystoreServer:
    protectCont = myLock()
    contents = {}
    def __init__(self, store: str, ipaddr = ''):
        trace('**creating keystoreServer.')
        self.store = store
        if path.exists(self.store + '.lock'):
            raise FileExistsError('store is locked @: ' + self.store + '.lock')
        if len(ipaddr) > 0:
            addr = ipaddr
        else:
            addr = socket.gethostbyname(socket.gethostname())
        good = False
        port = 9999
        while not good:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if sock.connect_ex((addr, port)) == 0:
                port += 1
            else:
                good = True;
            sock.close()
        with open(self.store + '.lock', 'wb') as lf:
            pickle.dump([addr,port], lf)
        if path.exists(self.store):
            with open(self.store, 'rb') as sf:
                __class__.contents = pickle.load(sf)
        else:
            print('**WARNING:keystore did not exist at: \'' + self.store +
                  '\'; created') 
            open(self.store, 'wb')
        self.beenShutdown = False
        self.thread = threading.Thread(group = None, target=self.runServer, args=(addr, port)).start()
    def runServer(self, addr, port):
        with socketserver.TCPServer((addr, port), keystoreHandler) as server:
            print('**launching server at ' + addr + ':' + str(port))
            self.handler = server
            server.serve_forever()
    def shutdown(self):
        self.handler.shutdown()
        trace('**completed server.shutdown')
        with open(self.store, 'wb') as sf:
            with __class__.protectCont:
                pickle.dump(__class__.contents, sf)
        os.remove(self.store + '.lock')
        trace('**finished file handling on server shutdown')
        self.beenShutdown = True
    def get(key:str) -> str:
        trace('**get on key: \'' + key + '\'')
        with __class__.protectCont:
            return __class__.contents[key]
    def put(key:str, val:any):
        trace('**put on key: \'' + key + '\'')
        with __class__.protectCont:
            __class__.contents[key] = val
        trace('**finished put on server')
    def delete(key:str):
        trace('**delete on key: \'' + key + '\'')
        with __class__.protectCont:
            del __class__.contents[key]
        trace('**finished delete on server')
    def size():
        trace('**size on server')
        with __class__.protectCont:
            return len(__class__.contents)
        
    def __del__(self):
        trace('**entered __del__ on server')
        if(hasattr(self, 'beenShutdown') and not self.beenShutdown):
            self.shutdown()
        trace('**destroyed keystoreServer')

    
