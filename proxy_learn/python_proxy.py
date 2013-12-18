#coding=utf8
import socket, thread, select, time

__version__ = '0.1.0 Draft 1'
BUFLEN = 8192
VERSION = 'Python Proxy/'+__version__
HOST = 'localhost'
PORT = 8080

class ConnectionHandler(object):
    def __init__(self, connection, address, timeout):
        self.client = connection
        self.client_buffer = ''
        self.timeout = timeout
        # POST http://www.voanews.com/ HTTP/1.1
        self.method, self.path, self.protocol = self.get_base_header()
        if self.method=='CONNECT':
            self.method_CONNECT()
        elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE'):
            self.method_others()
        self.client.close()
        if self.target:
            self.target.close()

    def get_base_header(self):
        while 1:
            time.sleep(0.5)
            self.client_buffer += self.client.recv(BUFLEN)
            end = self.client_buffer.find('\n')
            if end!=-1:
                break
        show(self.client_buffer)
        data = (self.client_buffer[:end+1]).split() # not .split(' ')
        self.client_buffer = self.client_buffer[end+1:]
        return data

    def method_CONNECT(self):
        self._connect_target(self.path)
        self.client.sendall('HTTP/1.1 200 Connection established\n'+
                         'Proxy-agent: %s\n\n'%VERSION)
        self.client_buffer = ''
        self._read_write()

    def method_others(self):
        #self.path = self.path[7:]
        # http://www.voanews.com/
        self.path = self.path.split('://')[1]
        i = self.path.find('/')
        if i != -1:
            host = self.path[:i]
            path = self.path[i:]
        else:
            host = self.path
            path = '/'
        self._connect_target(host)
        request = '%s %s %s\r\n' % (self.method, path, self.protocol) + self.client_buffer
        self.target.sendall(request)
        self.client_buffer = ''
        self._read_write()

    def _connect_target(self, host):
        i = host.find(':')
        if i!=-1:
            port = int(host[i+1:])
            host = host[:i]
        else:
            port = 80
        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(soc_family, socket.SOCK_STREAM)
        self.target.connect(address)

    def _read_write(self):
        time_out_max = self.timeout/3
        socs = [self.client, self.target]
        count = 0
        while 1:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN)
                    if in_ is self.client:
                        out = self.target
                    else:
                        out = self.client
                    if data:
                        out.sendall(data)
                        count = 0
            if count == time_out_max:
                break

def show(s):
    print [s]
    print '-'*30
    print s
    print '-'*30

def start_server(host=HOST, port=PORT, IPv6=False, timeout=60,
                  handler=ConnectionHandler):
    '''
    socket.accept()

    Accept a connection. The socket must be bound to an address and listening for connections. 
    The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data on the connection, 
    and address is the address bound to the socket on the other end of the connection.


    thread.start_new_thread(function, args[, kwargs])

    Start a new thread and return its identifier. 
    The thread executes the function function with the argument list args (which must be a tuple). 
    The optional kwargs argument specifies a dictionary of keyword arguments. 
    When the function returns, the thread silently exits. 
    When the function terminates with an unhandled exception, 
    a stack trace is printed and then the thread exits (but other threads continue to run).

    def __init__(self, connection, address, timeout):
    '''
    if IPv6==True:
        soc_type=socket.AF_INET6
    else:
        soc_type=socket.AF_INET
    soc = socket.socket(soc_type, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((host, port))
    soc.listen(0)
    while 1:
        thread.start_new_thread(handler, soc.accept()+(timeout,))

if __name__ == '__main__':
    start_server()













