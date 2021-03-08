import client
from client import *

class tester:
    def __init__(self, val):
        self.val = val

CLICOUNT = 20
assert CLICOUNT % 5 == 0

clients = []
for _ in range(CLICOUNT):
    clients.append(keystoreClient('teststore'))

clients[0].put('test', 123)

for c in clients:
    assert c.get('test') == 123

for i in range(CLICOUNT - 1):
    clients[i].put('test', i)
    assert clients[i+1].get('test') == i

clients[0].put('tester', tester(23))

testObj = clients[19].get('tester')

assert testObj.val == 23

for i in range(CLICOUNT * 5):
    clients[i % CLICOUNT].put('test', i)
    clients[(i * 3) % CLICOUNT].delete('test')
    raised = False
    try:
        clients[(i + 2) % CLICOUNT].get('test')
    except:
        raised = True
    assert raised

tv = [123,456,'abc','def', 123.78923848472, float.fromhex('0x23.d12p-100'),
      {'zzz': 12378, 'yyy': 77777}, complex('234-73j'), dir()]

clients[0].put('test', tv)

assert clients[CLICOUNT-1].get('test') == tv

size = clients[CLICOUNT // 2].size()

for i in range(CLICOUNT):
    if i % 5 == 4:
        s = clients[i].size()
        assert s == size
    else:
        if (i % 5) % 2 == 0:
            clients[i].put('abc' + str(i), 1239487293738488)
        else:
            clients[i].delete('abc' + str(i-1))

for c in clients:
    assert c.size() == size

for c in clients:
    c.shutdown()

