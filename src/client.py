import socket
import Queue
import threading

class RoverClient(object):
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket.connect((host, port))
        self.stop = False
        self.sendthread = threading.Thread(target=self.send)
        self.sendthread.setDaemon(True)
        self.recvthread = threading.Thread(target=self.recv)
        self.recvthread.setDaemon(True)
        self.sendq = Queue.Queue()
        self.recvq = Queue.Queue()

    def send(self):
        while not self.stop:
            try:
                message = self.sendq.get(True, 1)
                self.socket.send(message + ";")
            except Queue.Empty:
                pass

    def recv(self):
        buf = ""
        while not self.stop:
            buf = buf + self.socket.recv(4096)
            messages = buf.split(";")
            for m in messages[:-1]:
                self.recvq.put(m)
            # if last in messages is non-empty, there was no ; last in buf
            buf = messages[-1]            

    def start(self):
        self.sendthread.start()
        self.recvthread.start()


if __name__=="__main__":
    import sys
    r = RoverClient(sys.argv[1], int(sys.argv[2]))
    r.start()    
    counter = 0
    while True:
        print r.recvq.get()
        r.sendq.put(str(counter))
        counter += 1
