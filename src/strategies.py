import math
from collections import deque
from vector import Vector 
import path
import astarpath

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
    def __init__(self, rover, p, i, d):
        self.rover = rover
        self.p = p
        self.i = i
        self.d = d
        self.errint = 0.0
        self.last_ang_err = 0.0
        self.time = 0.0
        self.ctl_acc = ''
        self.prev_direction = None
        self.est_ang_acc = 0.0      # Estimated angular acceleration [radians / s^2]
        self.maxturn = math.radians(rover.maxturn)
        self.maxhardturn = math.radians(rover.maxhardturn)
        self.current_turn = ''
        self.current_turn_rate = 0.0  # Calculated rate of turn [radians / s]
        return
        
    def calc_path(self, rover):
        return Path(path.find_path(rover.pos, (0.0, 0.0), rover.world))
        
    def calc_wanted_ang_vel(self, ang_err, dt):
        # Turn control.
        wanted_turn_rate = 0.0
        
        try:
            wanted_turn_rate = self.p * ang_err + self.i * self.errint + self.d * (ang_err - self.last_ang_err) / dt
        except ZeroDivisionError: 
            pass
        
        if wanted_turn_rate > self.maxhardturn:
            wanted_turn_rate = self.maxhardturn
        if wanted_turn_rate < -self.maxhardturn:
            wanted_turn_rate = -self.maxhardturn
            
        return wanted_turn_rate
        
    def calc_turn_command(self, wanted_turn_rate, dt):
        estimated_turn_rate = self.current_turn_rate
        turn_rate_change = dt * self.est_ang_acc
        turn_cmd = ''
        
        if self.current_turn == 'l':
            if self.current_turn_rate < self.maxturn:
                estimated_turn_rate = min(estimated_turn_rate + turn_rate_change, self.maxturn)
            else:
                estimated_turn_rate = max(estimated_turn_rate - turn_rate_change, self.maxturn)
        elif self.current_turn == 'L':
            estimated_turn_rate = min(estimated_turn_rate + turn_rate_change, self.maxhardturn)
        elif self.current_turn == 'r':
            if self.current_turn_rate > -self.maxturn:
                estimated_turn_rate = max(estimated_turn_rate - turn_rate_change, -self.maxturn)
            else:
                estimated_turn_rate = min(estimated_turn_rate + turn_rate_change, -self.maxturn)
        elif self.current_turn == 'R':
            estimated_turn_rate = max(estimated_turn_rate - turn_rate_change, -self.maxhardturn)
        
        diff = wanted_turn_rate - estimated_turn_rate
        
        if wanted_turn_rate == self.maxturn:
            # Max turn left.
            turn_cmd = 'l'
        elif wanted_turn_rate > self.maxturn:
            # Hard turn left.
            if diff > 0:
                turn_cmd = 'l'
            elif self.current_turn == 'L':
                turn_cmd = 'r'
        elif wanted_turn_rate > 0.5 * turn_rate_change:
            # Soft turn left.
            if diff > 0:
                if self.current_turn == 'L':
                    turn_cmd = 'r'
                elif self.current_turn != 'l':
                    turn_cmd = 'l'
            else:
                if self.current_turn in 'lL':
                    turn_cmd = 'r'
                elif self.current_turn in 'rR':
                    turn_cmd = 'l'
        elif wanted_turn_rate == -self.maxturn:
            # Max turn right.
            turn_cmd = 'r'
        elif wanted_turn_rate < -self.maxturn:
            # Hard turn right.
            if diff < 0:
                turn_cmd = 'r'
            elif self.current_turn == 'R':
                turn_cmd = 'l'
        elif wanted_turn_rate < 0.5 * turn_rate_change:
            # Soft turn right.
            if diff < 0:
                if self.current_turn == 'R':
                    turn_cmd = 'l'
                elif self.current_turn != 'r':
                    turn_cmd = 'r'
            else:
                if self.current_turn in 'rR':
                    turn_cmd = 'l'
                elif self.current_turn in 'lL':
                    turn_cmd = 'r'
        else:
            # No turn
            if self.current_turn in 'rR':
                turn_cmd = 'l'
            elif self.current_turn in 'lL':
                turn_cmd = 'r'
             
        return turn_cmd

    def calc_command(self, rover):       
        x, y = rover.pos
        dt = (rover.time - self.time) / 1000.0 # in seconds
        
        rotv = 0.0
        rota = 0.0
        
        if self.prev_direction and dt:            
            rotv = (rover.direction - self.prev_direction) / dt
            print "ROTV:", rotv
        if self.current_turn_rate and dt:            
            rota = (rotv - math.degrees(self.current_turn_rate)) / dt
            print "ROTA:", rota
        self.current_turn_rate = math.radians(rotv)
        self.prev_direction = rover.direction
        self.est_ang_acc = max(self.est_ang_acc, abs(math.radians(rota)))
        print "SPEED:", rover.speed, "(", rover.maxspeed, ")"       
        print "DIR:", rover.direction
        #print "SPEED:", rover.speed, "(", rover.maxspeed, ")"

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
        
        new_acc_cmd = ''
        
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
        wanted_turn_rate = self.calc_wanted_ang_vel(a, dt)
        new_turn_cmd = self.calc_turn_command(wanted_turn_rate, dt)
                
        print wanted_turn_rate / self.maxhardturn
        
        if deleted_node:
            print '***** New segment *****'
        
        self.ctl_acc = new_acc_cmd
        
        if new_turn_cmd == 'l':
            if self.current_turn == 'R':
                self.current_turn = 'r'
            elif self.current_turn == 'r':
                self.current_turn = ''
            elif self.current_turn == '':
                self.current_turn = 'l'
            else:
                self.current_turn = 'L'
        elif new_turn_cmd == 'r':
            if self.current_turn == 'L':
                self.current_turn = 'l'
            elif self.current_turn == 'l':
                self.current_turn = ''
            elif self.current_turn == '':
                self.current_turn = 'r'
            else:
                self.current_turn = 'R'
        
        self.last_ang_err = a

        return new_acc_cmd + new_turn_cmd
