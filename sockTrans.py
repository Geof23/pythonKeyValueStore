import struct
import pickle

def nothing(msg):
    pass
trace = nothing
#trace = print

class sockTrans:
    def __init__(self, sock):
        trace('init sockTrans')
        self.sock = sock

    def send(self, val):
        trace('sockTrans send')
        pval = pickle.dumps(val)
        self.sock.sendall(pval)
        
    def recv(self):
        trace('sockTrans recv')
        data = self.sock.recv(2**16).strip()
        return pickle.loads(data)

