import math
from collections import deque
from vector import Vector 
import path

class Path(object):
    def __init__(self, points):
        self.points = points

    def current_segment(self, pos, threshold):
        deleted_node = False
        if len(self.points) > 2:
            x, y = pos
            p = self.points[1]
            dx = x - p[0]
            dy = y - p[1]
            d = dx * dx + dy * dy
            if d < threshold:
                self.points = self.points[1:]
                deleted_node = True
        return (deleted_node, self.points[0:2])

class BaseStrategy(object):
    def calc_path(self, rover):
        return Path([rover.pos, (0.0, 0.0)])

    def calc_command(self, rover):
        return ""
        

class SimplePathFollower(BaseStrategy):
    def calc_path(self, rover):
        return Path(path.find_path(rover.pos, (0.0, 0.0), rover.world))

    def calc_command(self, rover):
        x, y = rover.pos
        nowvec = Vector(x, y)
        dr = math.radians(rover.direction)
        dirvec = Vector(math.cos(dr), math.sin(dr))
        deleted_node, seg = rover.path.current_segment(rover.pos, 4.0)
        x1, y1 = seg[0]
        x2, y2 = seg[1]
        goalvec = Vector(x2, y2)
        #print "segment:", seg
        #print "pos:", x, y
        a = dirvec.angle_signed(goalvec - nowvec)
        #print "difference", a
        cmd = ""
        absa = abs(a)
        if absa > 0.7:
            cmd = "b"
        elif absa > 0.4:
            pass
        else:            
            cmd = "a"

        if absa > 0.7:
            # turn hard
            if a > 0:
                cmd += "l"
            else:
                cmd += "r"
        elif absa > 0.2:
            # turn
            if a > 0:
                if rover.ctl_turn == "L":
                    cmd += "r"
                elif rover.ctl_turn == "l":
                    pass
                else:
                    cmd += "l"
            else:
                if rover.ctl_turn == "R":
                    cmd += "l"
                elif rover.ctl_turn == "r":
                    pass
                else:
                    cmd += "r"            

        #print rover.ctl_turn
        #print cmd
        return cmd
        
        
class PidPathFollower(BaseStrategy):
    def __init__(self, p, i, d):
        self.p = p
        self.i = i
        self.d = d
        self.errint = 0.0
        self.lasterr = 0.0
        self.time = 0.0
        self.turn_history = deque(10 * ['-'])
        self.ctl_acc = ''
        self.ctl_turn = ''
        return
        
    def calc_path(self, rover):
        return Path(path.find_path(rover.pos, (0.0, 0.0), rover.world))

    def calc_command(self, rover):
        x, y = rover.pos
        dt = rover.time - self.time
        self.time = rover.time
        nowvec = Vector(x, y)
        dr = math.radians(rover.direction)
        dirvec = Vector(math.cos(dr), math.sin(dr))
        deleted_node, seg = rover.path.current_segment(rover.pos, 4.0)
        x1, y1 = seg[0]
        x2, y2 = seg[1]
        goalvec = Vector(x2, y2)
        #print "segment:", seg
        #print "pos:", x, y
        a = dirvec.angle_signed(goalvec - nowvec)
        
        if deleted_node:
            self.errint = 0.0
            
        self.errint += a * dt
        
        # History
        self.turn_history.append(self.ctl_turn)
        self.turn_history.popleft()
        
        new_acc_cmd = ''
        new_turn_cmd = ''
        
        #print "difference", a
        
        # Speed control.
        absa = abs(a)
        if absa > 0.7:
            new_acc_cmd = "b"
        elif absa > 0.4:
            pass
        else:            
            new_acc_cmd = "a"

        # Turn control.
        maxturn = math.radians(rover.maxturn)
        maxhardturn = math.radians(rover.maxhardturn)
        wanted_turn_rate = 0.0
        
        try:
            wanted_turn_rate = self.p * a + self.i * self.errint + self.d * (a - self.lasterr) / dt
        except ZeroDivisionError: 
            pass
        
        if wanted_turn_rate > maxhardturn:
            wanted_turn_rate = maxhardturn
        if wanted_turn_rate < -maxhardturn:
            wanted_turn_rate = -maxhardturn
        
        turn_cmd = ''
        neutral_cmd = ''
        pwm = 0.0
        
        if wanted_turn_rate > 0:
            turn_cmd = 'l'
            neutral_cmd = 'r'
        else:
            turn_cmd = 'r'
            neutral_cmd = 'l'
            
        if abs(wanted_turn_rate) > maxturn:
            # Hard turn
            pwm = (abs(wanted_turn_rate) - maxturn) / (maxhardturn - maxturn)
            history_pwm = sum(1.0 for cmd in self.turn_history if cmd == turn_cmd.upper()) / len(self.turn_history)
            if (pwm < history_pwm) and (self.ctl_turn == turn_cmd.upper()):
                new_turn_cmd = neutral_cmd
            else:
                new_turn_cmd = turn_cmd
        else:
            # Normal turn
            pwm = abs(wanted_turn_rate) / maxturn
            history_pwm = sum(1.0 for cmd in self.turn_history if cmd == turn_cmd.upper() or cmd == turn_cmd) / len(self.turn_history)
            if self.ctl_turn == turn_cmd.upper():
                new_turn_cmd += neutral_cmd
            elif (pwm < history_pwm) and (self.ctl_turn == turn_cmd):
                new_turn_cmd += neutral_cmd
            elif self.ctl_turn != turn_cmd:
                new_turn_cmd += turn_cmd
                
        print wanted_turn_rate / maxhardturn
        
        if deleted_node:
            print '***** New segment *****'
        
        self.ctl_acc = new_acc_cmd        
        self.ctl_turn = new_turn_cmd
        self.lasterr = a

        return new_acc_cmd + new_turn_cmd
