import socket
import Queue
import threading
import msgparser as mp
import world
import time

class RoverControl(object):
    def __init__(self, host, port):
        self.roverclient = RoverClient(host, port)
        self.world = None

    def _run_control(self):
        print "Start control thread"
        rc = self.roverclient
        try:
            while rc.running:
                if self.world and self.world.rover and self.world.rover.ok():
                    c = self.world.rover.calc_command()
                    if c:
                        rc.sendq.put(c)
                #time.sleep(0.5)
        except Exception, e:
            print e

    def run(self):
        rc = self.roverclient
        rc.start()
        self.controlthread = threading.Thread(target=self._run_control)
        self.controlthread.setDaemon(True)
        self.controlthread.start()
        while rc.running:
            try:
                m = mp.parse(rc.recvq.get(True, 2))
                self.update_world(m)
            except Queue.Empty:
                pass
        self.controlthread.join()
        rc.stop()

    def update_world(self, m):
        try:
            #print m
            if m.type == mp.TYPE_INIT:
                self.world = world.World(m)
            elif m.type == mp.TYPE_TELEMETRY:
                self.world.update(m)
            elif m.type == mp.TYPE_END_OF_RUN:
                self.world.reset()
            else:
                # not handled yet
                pass
        except Exception, e:
            print e
            raise
            pass
            

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
    r = RoverControl(sys.argv[1], int(sys.argv[2]))
    r.run()    
