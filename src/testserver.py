import sys
import time
import socket
import asyncore
import asynchat

class Producer(object):
    def __init__(self):
        self.msg = ['I 2000 2000 10000 2.0 20.0 1.0 3.0 6.0 ;',
                    'T 3450 aL -234.040 811.100 47.5 8.450 b -220.000 750.000 12.000 m -240.000 812.000 90.0 9.100 ;',
                    'S 1234 ;',
                    'E 1234 1234 ;']
        return
        
    def more(self):
        time.sleep(0.5)
        m = self.msg.pop(0)
        self.msg.append(m)
        return m
        

class Server(asynchat.async_chat):
    def __init__(self, connection):
        asynchat.async_chat.__init__(self, conn = connection)
        self.set_terminator(';')
        self.buffer = ''
        self.push_with_producer(Producer())
        return
        
    def collect_incoming_data(self, msg):
        self.buffer += msg
        return
        
    def found_terminator(self):
        print self.buffer
        self.buffer = ''
        return
        
        
def create_connection(port):
    server = socket.socket()
    server.bind(('localhost', port))
    server.listen(1)
    print 'Listen on port', port
    client, address = server.accept()
    print 'Accepted connection from', address
    server.close()
    return client

if __name__ == '__main__':
    if len(sys.argv) > 1:
        connection = create_connection(int(sys.argv[1]))
        server = Server(connection)
        asyncore.loop()
        print 'Connection terminated.'
    else:
        print 'Need port number.'