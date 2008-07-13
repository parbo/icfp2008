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
        
        
class PiPathFollower(BaseStrategy):
    def __init__(self, p, i):
        self.p = p
        self.i = i
        self.errint = 0.0
        self.time = 0.0
        self.turn_history = deque(10 * ['-'])
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
        #print "difference", a
        
        # Speed control.
        cmd = ""
        absa = abs(a)
        if absa > 0.7:
            cmd = "b"
        elif absa > 0.4:
            pass
        else:            
            cmd = "a"

        # Turn control.
        self.turn_history.append(rover.ctl_turn)
        self.turn_history.popleft()
        maxturn = math.radians(rover.maxturn)
        maxhardturn = math.radians(rover.maxhardturn)
        wanted_turn_rate = self.p * a + self.i * self.errint
        
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
            if (pwm < history_pwm) and (rover.ctl_turn == turn_cmd.upper()):
                cmd += neutral_cmd
            else:
                cmd += turn_cmd
        else:
            # Normal turn
            pwm = abs(wanted_turn_rate) / maxturn
            history_pwm = sum(1.0 for cmd in self.turn_history if cmd == turn_cmd.upper() or cmd == turn_cmd) / len(self.turn_history)
            if rover.ctl_turn == turn_cmd.upper():
                cmd += neutral_cmd
            elif (pwm < history_pwm) and (rover.ctl_turn == turn_cmd):
                cmd += neutral_cmd
            elif rover.ctl_turn != turn_cmd:
                cmd += turn_cmd

        #print rover.ctl_turn
        #print cmd
        return cmd
