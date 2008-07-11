import socket
import Queue
import threading

class RoverClient(object):
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket.connect((host, port))
        self.running = False
        self.sendthread = threading.Thread(target=self.send)
        self.sendthread.setDaemon(True)
        self.recvthread = threading.Thread(target=self.recv)
        self.recvthread.setDaemon(True)
        self.sendq = Queue.Queue()
        self.recvq = Queue.Queue()

    def send(self):
        while self.running:
            try:
                message = self.sendq.get(True, 1)
                self.socket.send(message + ";")
            except Queue.Empty:
                print "Queue is empty"
                pass

    def recv(self):
        buf = ""
        try:
            while self.running:
                buf = buf + self.socket.recv(4096)
                if not buf:
                    raise
                messages = buf.split(";")
                for m in messages[:-1]:
                    self.recvq.put(m)
                # if last in messages is non-empty, there was no ; last in buf
                buf = messages[-1]            
        except:            
            print "Stopping!!"
            self.running = False

    def start(self):
        self.running = True
        self.sendthread.start()
        self.recvthread.start()

    def stop(self):
        self.running = False
        self.sendthread.join()
        self.recvthread.join()

if __name__=="__main__":
    import sys
    r = RoverClient(sys.argv[1], int(sys.argv[2]))
    r.start()    
    while r.running:
        try:
            print r.recvq.get(True, 2)
            r.sendq.put("a")
        except Queue.Empty:
            pass
    r.stop()
