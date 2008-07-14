import sys
import math
import strategies
import world
from vector import Vector

TIME_STEP = 0.1

class DummyWorld(object):
    def __init__(self):
        self.currentobjects = []
        return
        

class State(object):
    def __init__(self, pos, direction, maxspeed, acc, brake, turn, hardturn, rotacc):
        self.posvect = Vector(pos[0], pos[1])
        self.dirvect = Vector(math.cos(direction), math.sin(direction))
        self.speed = 0.0
        self.angvel = 0.0
        self.ctl_acc = '-'
        self.ctl_turn = '-'
        self.maxspeed = maxspeed
        self.drag = acc / maxspeed ** 2
        self.acc = acc
        self.brake = brake
        self.turn = turn
        self.hardturn = hardturn
        self.rotacc = rotacc
        return
        
    def update(self, ctl_acc, ctl_turn):
        # New position.
        self.posvect = self.posvect + TIME_STEP * rover.speed * self.dirvect
        # New direction.
        self.dirvect = self.dirvect.rotate(TIME_STEP * self.angvel)
        # New speed.
        acc = 0.0
        if self.ctl_acc == 'a':
            acc = self.acc
        elif self.ctl_acc == 'b':
            acc = -self.brake
        self.speed = max(self.speed + TIME_STEP * acc - TIME_STEP * self.drag * self.speed ** 2, 0.0)
        # New angular velocity.
        if self.ctl_turn == 'l':
            if self.angvel > self.turn:
                self.angvel = max(self.turn, self.angvel - TIME_STEP * self.rotacc)
            else:
                self.angvel = min(self.turn, self.angvel + TIME_STEP * self.rotacc)
        elif self.ctl_turn == 'L':
            if self.angvel > self.hardturn:
                self.angvel = max(self.hardturn, self.angvel - TIME_STEP * self.rotacc)
            else:
                self.angvel = min(self.hardturn, self.angvel + TIME_STEP * self.rotacc)
        elif self.ctl_turn == 'r':
            if self.angvel < -self.turn:
                self.angvel = min(-self.turn, self.angvel + TIME_STEP * self.rotacc)
            else:
                self.angvel = max(-self.turn, self.angvel - TIME_STEP * self.rotacc)
        elif self.ctl_turn == 'R':
            if self.angvel < -self.hardturn:
                self.angvel = min(-self.hardturn, self.angvel + TIME_STEP * self.rotacc)
            else:
                self.angvel = max(-self.hardturn, self.angvel - TIME_STEP * self.rotacc)
        # New control commands.
        self.ctl_acc = ctl_acc
        self.ctl_turn = ctl_turn
        return
        
def update_rover(rover, state, time):
    pos = state.posvect.point()
    direction = math.degrees(-state.dirvect.angle_signed(Vector(1.0, 0.0)))
    #print direction
    rover.update(time, state.ctl_acc, state.ctl_turn, pos, direction, state.speed)
    return
    
def simulate(rover, state, maxtime, path):
    t = 0.0
    goal = Vector(path[-1])
    controller = strategies.PidPathFollower(rover, 10.0, 0.0, 1.0)
    rover.strategy = controller
    update_rover(rover, state, 1000 * t)
    while t <= maxtime:
        cmd = controller.calc_command(rover)
        #print cmd
        #print state.posvect, state.dirvect
        ctl_acc = '-'
        ctl_turn = '-'
        if len(cmd) > 0:
            if cmd[0] in 'ab':
                ctl_acc = cmd[0]
            if cmd[-1] in 'lLrR':
                ctl_turn = cmd[-1]
        state.update(ctl_acc, ctl_turn)
        update_rover(rover, state, 1000 * t)
        if abs(goal - Vector(rover.pos)) < 5.0:
            print 'Reached goal. Time =', t
            break
        t += TIME_STEP
    return
    
def get_svg(rover, svg_include = []):
    dx = 500.0
    dy = 500.0
    svg = ["<?xml version=\"1.0\" standalone=\"no\"?>\n",
           "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n",
           "<svg width=\"%f\" height=\"%f\" viewbox=\"0 0 %f %f\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\">\n" % (dx, dy, dx, dy),
           "<g transform=\"translate(%f, %f) scale(1.0, -1.0)\" style=\"fill-opacity:1.0; stroke:black; stroke-width:1;\">\n" % (dx/2.0, dy/2.0),
           "<rect x=\"0\" y=\"0\" width=\"%f\" height=\"%f\" style=\"fill:#ffffff;\"/>"]
    try:
        svg.extend(rover.get_svg())
    except TypeError:
        pass
    svg.extend(svg_include)
    svg.append("</g>\n</svg>\n")
    return svg
    
def create_path_svg(pathlist):
    svg = ['<polyline fill="none" stroke="red" stroke-width="1" points="']
    for x, y in pathlist:
        svg.append('%f, %f ' % (x, y))
    svg.append('" />')
    return svg
    
def write_svg(filename, svg):
    f = open(filename, 'w')
    f.write(''.join(svg))
    f.close()
    return
    

if __name__ == '__main__':
    pos = (0.0, 0.0)
    direction = math.radians(90.0)
    minsensor = 30.0
    maxsensor = 60.0
    maxspeed = 20.0
    maxturn = 20.0
    maxhardturn = 60.0
    acc = 2.0
    brake = 3.0
    rotacc = 120.0
    maxturn_rad = math.radians(maxturn)
    maxhardturn_rad = math.radians(maxhardturn)
    rotacc_rad = math.radians(rotacc)
    rover = world.Rover(DummyWorld(), minsensor, maxsensor, maxspeed, maxturn, maxhardturn)
    state = State(pos, direction, maxspeed, acc, brake, maxturn_rad, maxhardturn_rad, rotacc_rad)
    path = [(0.0, 0.0), 
            (200.0, 50.0), 
            (200.0, 100.0), 
            (150.0, 150.0), 
            (-150.0, 150.0), 
            (-200.0, 100.0), 
            (-200.0, -150.0),
            (200.0, -150.0),
            (200.0, -75.0),
            (-100.0, -100.0),
            (-50.0, 100.0)]
    rover.path = strategies.Path(path)
    simulate(rover, state, 300.0, path)
    write_svg('testcontrol.svg', get_svg(rover, create_path_svg(path)))
    