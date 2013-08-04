import socket, sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
MAX = 65535
PORT = 1060
if sys.argv[1:] == ['server']:
    s.bind(('127.0.0.1', PORT))
    print 'Listening at', s.getsockname()
    while True:
        data, address = s.recvfrom(MAX)
        print 'The client at', address, 'says', repr(data)
        s.sendto('Your data was [[%s]], %d bytes' % (data, len(data)), address)
elif sys.argv[1:] == ['client']:
    print 'Address before sending:', s.getsockname()
    server = ('127.0.0.1', PORT)
    s.sendto('This is my message', server)
    print 'Address after sending', s.getsockname()
    data, address = s.recvfrom(MAX) # overly promiscuous - see text!
    if not address == server:
        print 'attacker', address
        exit() 
    print 'The server', address, 'says', repr(data)
    print 'Address after receiving', s.getsockname()
    s.sendto('This is my message', ('127.0.0.1', PORT))
    print 'Address after another sending', s.getsockname()
else:
    print 'error, usage: python udp_server_or_client.py server|client'
