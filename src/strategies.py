import math
from collections import deque
from vector import Vector 
import path
import astarpath
import world


eps = 1e-7


CLEAR_WAYPOINT_DIST = 5.0


def distance_to_segment(start, end, pos):
    v2 = Vector(pos) - Vector(start)
    v = (Vector(end) - Vector(start)).normalize()
    projd = v2 * v
    return math.sqrt(v2 * v2 - projd ** 2)


class Path(object):
    def __init__(self, points):
        self.points = points

    def current_segment(self, pos, threshold):
        deleted_node = False
        next_seg = None
        if len(self.points) > 2:
            x, y = pos
            p = self.points[1]
            dx = x - p[0]
            dy = y - p[1]
            d = dx * dx + dy * dy
            if d < threshold:
                self.points = self.points[1:]
                deleted_node = True
        if len(self.points) > 2:
            next_seg = self.points[1:3]
        return (deleted_node, self.points[0:2], next_seg)

    def distance(self, pos):
        return distance_to_segment(self.points[0], self.points[1], pos)
    
def cost_fcn_factory(maxcost, sigma):
    def fcn(r, d):
        if abs(d) < r:
            return maxcost
        return maxcost * math.e ** ((-(d - r) ** 2) / (2 * sigma ** 2))
    return fcn

boulder_cost = cost_fcn_factory(10.0, 2.0)
crater_cost = cost_fcn_factory(10.0, 2.0)
martian_cost = cost_fcn_factory(40.0, 3.0)
home_cost = cost_fcn_factory(5.0, 3.0)

def angle_cost(r, a):
    return 0.0 * r * (a ** 3)

class BaseStrategy(object):
    def reset(self):
        return
        
    def calc_path(self, rover):
        return Path([rover.pos, (0.0, 0.0)])

    def calc_command(self, rover):
        return ""

    def calc_angle(self, rover):
        deleted_node, seg, next_seg = rover.path.current_segment(rover.pos, CLEAR_WAYPOINT_DIST ** 2)
        wp = seg[1]
        #print wp
        rdir = math.radians(rover.direction)
        dirvec = Vector(math.cos(rdir), math.sin(rdir))
        wpvec = (Vector(wp) - Vector(rover.pos)).normalize()
        if not rover.world.currentobjects:
            return dirvec.angle_signed(wpvec)
        
        def cost_fcn(v):
            cost = 0.0
            # Calculate cost for obstacles
            for obj in rover.world.currentobjects:
                v2 = Vector(obj.pos) - Vector(rover.pos)
                projd = v2 * v
                if projd > 0.0:
                    try:
                        d = math.sqrt(v2 * v2 - projd ** 2)
                    except ValueError, e:
                        print v2 * v2, projd
                        continue
                    maxr = rover.speed / math.radians(rover.maxhardturn)
                    if d < 2 * maxr:
                        scale = 1.0
                    else:
                        scale = math.e ** ((-(projd - 2 * maxr) ** 2) / (2 * 50.0 ** 2))
                    oc = 0.0
                    if isinstance(obj, world.Boulder):
                        oc = boulder_cost(obj.radius, d) * scale
                    elif isinstance(obj, world.Crater):
                        oc = crater_cost(obj.radius, d)  * scale
                    elif isinstance(obj, world.Martian):
                        oc = martian_cost(obj.radius, d) * scale
                    elif isinstance(obj, world.Home):
                        oc = -martian_cost(obj.radius, d) * scale
                    cost += oc
            # Calculate cost for angle change
            ac = angle_cost(rover.speed / math.radians(rover.maxhardturn), dirvec.angle(v))
            cost += ac
            return cost

        wpcost = cost_fcn(wpvec)
        # if wpvec is good enough
        #print "WPCOST:", wpcost
        if wpcost < 0.1:
            #print "WP is good enough"
            return dirvec.angle_signed(wpvec)

        num = 10
        testvec = []
        for i in range(1, num):
            a = i * (math.pi / 8) / (num - 1)
            testvec.append((a, wpvec.rotate(a)))
            testvec.append((a, wpvec.rotate(-a)))

        costs = [(wpcost, 0, wpvec)]
        for a, v in testvec:
            cost = cost_fcn(v)
            costs.append((cost, a, v))
            
        costs.sort()
        #print "MINC:", costs[0][0], "MAXC:", costs[-1][0]
        c, a, v = costs[0]
        if v != dirvec:
            #print "selecting:", v, c, wpcost
            return dirvec.angle_signed(v)
        return 0.0

class SimplePathFollower(BaseStrategy):
    def calc_path(self, rover):
        return Path(path.find_path(rover.pos, (0.0, 0.0), rover.world))

    def calc_command(self, rover):
        x, y = rover.pos
        nowvec = Vector(x, y)
        dr = math.radians(rover.direction)
        dirvec = Vector(math.cos(dr), math.sin(dr))
        deleted_node, seg, next_seg = rover.path.current_segment(rover.pos, 4.0)
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
        
SPEED_CTRL_ACC = 0
SPEED_CTRL_TURN = 1
SPEED_CTRL_BRAKE_TURN = 2
SPEED_CTRL_BRAKE_TGT = 3
SPEED_CTRL_BRAKE_CALIB = 4

MIN_TURN_RADIUS = 5.0
ANGLE_DIFF_LIMIT = 0.4

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
        self.current_speed_ctrl = SPEED_CTRL_ACC
        self.maxturnradius = rover.maxspeed / self.maxhardturn
        self.speed_limit = 0.0
        self.target_distance = None
        self.safe_turn_speed = 0.8 * CLEAR_WAYPOINT_DIST * self.maxhardturn
        self.next_turn_max_radius = self.maxturnradius
        return
        
    def reset(self):
        self.errint = 0.0
        self.last_ang_err = 0.0
        self.time = 0.0
        self.ctl_acc = ''
        self.prev_direction = None
        self.est_ang_acc = 0.0      # Estimated angular acceleration [radians / s^2]
        self.current_turn = ''
        self.current_turn_rate = 0.0  # Calculated rate of turn [radians / s]
        self.current_speed_ctrl = SPEED_CTRL_ACC
        self.speed_limit = 0.0
        self.target_distance = None
        self.next_turn_max_radius = self.maxturnradius
        return
        
    def calc_path(self, rover):
        return Path(path.find_path(rover.pos, (0.0, 0.0), rover.world))
        #return Path([rover.pos, (0.0, 0.0)])
        
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
        
        #print diff, wanted_turn_rate, estimated_turn_rate
        
        if wanted_turn_rate == self.maxhardturn:
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
        elif wanted_turn_rate == -self.maxhardturn:
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
        
        #print turn_cmd
        return turn_cmd
        
    def calc_speed_command(self, heading_vect, target_vect):
        speed_cmd = 'a'
        pi2 = math.pi / 2
        angle = heading_vect.angle(target_vect)
        target_distance = abs(target_vect)
        if self.current_speed_ctrl == SPEED_CTRL_TURN:
            turn_radius = MIN_TURN_RADIUS
            if angle > pi2:
                turn_radius = MIN_TURN_RADIUS + (angle - pi2) * (max(self.maxturnradius, MIN_TURN_RADIUS) - MIN_TURN_RADIUS) / pi2
            self.speed_limit = turn_radius * self.maxhardturn
            #print 'Starting turn.' 
            #print 'Turn radius =', turn_radius
            #print 'Speed limit =', self.speed_limit
            self.current_speed_ctrl = SPEED_CTRL_BRAKE_TURN
            
        if self.current_speed_ctrl == SPEED_CTRL_BRAKE_TURN:
            if angle < ANGLE_DIFF_LIMIT:
                #print 'Leaving brake mode.'
                self.current_speed_ctrl = SPEED_CTRL_ACC
            if self.rover.speed > self.speed_limit:
                #print 'Braking. Speed =', self.rover.speed
                speed_cmd = 'b'
        elif self.current_speed_ctrl == SPEED_CTRL_BRAKE_TGT:
            if angle < ANGLE_DIFF_LIMIT:
                self.current_speed_ctrl = SPEED_CTRL_ACC
            else:
                speed_cmd = 'b'
        elif self.current_speed_ctrl == SPEED_CTRL_BRAKE_CALIB:
            if (self.rover.retardation is not None):
                self.current_speed_ctrl = SPEED_CTRL_ACC
            else:
                speed_cmd = 'b'
        else:
            if (self.rover.retardation is None) and (self.rover.acceleration is not None):
                # Calibration of retardation.
                self.current_speed_ctrl = SPEED_CTRL_BRAKE_CALIB
                speed_cmd = 'b'
            elif self.target_distance is not None:
                if (target_distance > self.target_distance) and (self.rover.speed > self.safe_turn_speed):
                    # Distance to target increasing.
                    self.current_speed_ctrl = SPEED_CTRL_BRAKE_TGT
                    speed_cmd = 'b'
            if self.rover.retardation is not None:
                turn_speed_limit = self.next_turn_max_radius * self.maxhardturn
                try:
                    brake_distance = -0.5 * (self.rover.speed ** 2 - turn_speed_limit ** 2) / self.rover.retardation
                except ZeroDivisionError:
                    brake_distance = 0.0
                #print target_distance, brake_distance
                if target_distance < brake_distance:
                    print 'Approaching target - braking.'
                    speed_cmd = 'b'
                
        self.target_distance = target_distance
        return speed_cmd
        
    def calc_next_turn_max_radius(self, current_seg, next_seg):
        angle = math.pi
        pi2 = math.pi / 2
        pi34 = 0.75 * math.pi
        if next_seg is not None:
            angle = math.pi - (Vector(next_seg[1]) - Vector(next_seg[0])).angle(Vector(current_seg[1]) - Vector(current_seg[0]))
        if angle < pi2:
            self.next_turn_max_radius = MIN_TURN_RADIUS
        elif angle > pi34:
            self.next_turn_max_radius = self.maxturnradius
        else:
            self.next_turn_max_radius = MIN_TURN_RADIUS + (angle - pi2) * (max(self.maxturnradius, MIN_TURN_RADIUS) - MIN_TURN_RADIUS) / (pi34 - pi2)
        #print math.degrees(angle), self.next_turn_max_radius
        return

    def calc_command(self, rover):       
        x, y = rover.pos
        dt = (rover.time - self.time) / 1000.0 # in seconds
        
        rotv = 0.0
        rota = 0.0
        
        if self.prev_direction and dt:            
            rotv = (rover.direction - self.prev_direction) / dt
            #print "ROTV:", rotv
        if self.current_turn_rate and dt:            
            rota = (rotv - math.degrees(self.current_turn_rate)) / dt
            #print "ROTA:", rota
        self.current_turn_rate = math.radians(rotv)
        self.prev_direction = rover.direction
        self.est_ang_acc = max(self.est_ang_acc, abs(math.radians(rota)))
        #print "SPEED:", rover.speed, "(", rover.maxspeed, ")"       
        #print "DIR:", rover.direction
        #print "SPEED:", rover.speed, "(", rover.maxspeed, ")"

        self.time = rover.time
        
        nowvec = Vector(x, y)
        dr = math.radians(rover.direction)
        dirvec = Vector(math.cos(dr), math.sin(dr))
        deleted_node, seg, next_seg = rover.path.current_segment(rover.pos, CLEAR_WAYPOINT_DIST ** 2)
        x1, y1 = seg[0]
        x2, y2 = seg[1]
        goalvec = Vector(x2, y2)
        tgtvec = goalvec - nowvec
        
        #print "segment:", seg
        #print "pos:", x, y
        
        a = self.calc_angle(rover)
        #print "ANGLE:", a, old_a
        
        if deleted_node:
            self.errint = 0.0
            print '***** New segment *****'
            self.current_speed_ctrl = SPEED_CTRL_TURN
            self.target_distance = None
            
        self.calc_next_turn_max_radius(seg, next_seg)
            
        self.errint += a * dt
        
        # Speed control.
        new_acc_cmd = self.calc_speed_command(dirvec, tgtvec)

        # Turn control.
        wanted_turn_rate = self.calc_wanted_ang_vel(a, dt)
        new_turn_cmd = self.calc_turn_command(wanted_turn_rate, dt)
                
        #print wanted_turn_rate / self.maxhardturn
                
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


if __name__=="__main__":
    rg = range(-10, 10, 1)

    print [boulder_cost(5, r) for r in rg]
    print [crater_cost(5, r) for r in rg]
    print [martian_cost(5, r) for r in rg]
    print [wp_cost(r) for r in rg]
    
