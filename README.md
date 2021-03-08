# Simple Distributed Keystore

This is a no-frills key-value store that allows a group to maintain
a store at a specific filesystem location, and share the store
concurrently.  As it is python based, it is able to store a large
variety of python objects as values.  It is recommended to use
strings as the key type.

For users to share the store, they must share:

* access to a shared filesystem
* mutual reachability on a *private* network, with *trusted* users
* open TCP ports 9999 - 10100

This is a simple client-server system, where:

* initial access / creation of the keystore initializes a store file
* accessing the store, through the client, launches a server, from
  the client's host system, if there isn't already an active server
* also, when the client accesses the store, they will connect to
  the active server for the specified keystore file

The API is written in python, so a user should import `client` in their
code, after adding the root directory of this project to their classpath.
The included file `test.py` illustrates usage.

For example:

```python
import client

ksc = keystoreClient('/mnt/d/infoKeys.keystore')

widgetRepo = ksc.get('widgetRepoURL')

print('keys in ' + ksc.store + ': ' + ksc.size())

testRepo = ksc.put('testRepoURL', 'git@github.com:user23/testRepo.git')

...

```

The system manages concurrency and should scale to 10s to 100s of users, based
on the system that the server is launched from.  It will create a
new thread per request.  It is built with
standard python libraries, the components consist of:

* TCP server / request handler (`socketserver`)
* serialization (`pickle`)
* TCP socket client (i.e. _AF_INET_, _SOCK_STREAM_) (`socket`)
* concurrent access syncronization to the keystore is provided by `threading.Lock`
* per-user isolation is achieved via TCP request handlers, 

A reminder, that this system does not provide any type of access control
for either the files or the network access.  Also, the serialization library,
`pickle`, is not robust in hostile environments.


