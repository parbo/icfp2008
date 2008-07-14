import math
import strategies
from vector import Vector

class Area(object):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy
        self.left = -dx/2.0
        self.right = dx/2.0
        self.bottom = -dy/2.0
        self.top = dy/2.0

    def __str__(self):
        return "Area(%f, %f)"%(self.dx, self.dy)

class Home(object):
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius

    def __str__(self):
        return "Home((%f, %f), %f)"%(self.pos[0], self.pos[1], self.radius)

class Boulder(object):
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius

    def __str__(self):
        return "Boulder((%f, %f), %f)"%(self.pos[0], self.pos[1], self.radius)

    def get_svg(self):
        x, y = self.pos
        return ["<circle cx=\"%f\" cy=\"%f\" r=\"%f\" style=\"fill:%s;\" />\n" % (x, y, self.radius, "#ff0000")]

class Crater(object):
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius

    def __str__(self):
        return "Crater((%f, %f), %f)"%(self.pos[0], self.pos[1], self.radius)

    def get_svg(self):
        x, y = self.pos
        return ["<circle cx=\"%f\" cy=\"%f\" r=\"%f\" style=\"fill:%s;\" />\n" % (x, y, self.radius, "#00ff00")]

class Martian(object):
    def __init__(self, pos, speed, direction, time):
        self.positions = []
        self.radius = 0.5
        self.update(pos, speed, direction, time)    

    def __str__(self):
        return "Martian((%f, %f), %f, %f, %f)"%(self.pos[0], self.pos[1], self.radius, self.speed, self.direction)

    def get_svg(self):
        svg = ["<polyline fill=\"none\" stroke=\"red\" stroke-width=\"1\" points=\""]
        for p in self.positions:
            x, y = p[0]
            svg.append("%f, %f " % (x, y))
        svg.append("\" />")
        x, y = self.pos
        svg.append("<circle cx=\"%f\" cy=\"%f\" r=\"%f\" style=\"fill:%s;\" />\n" % (x, y, self.radius, "#0000ff"))
        return svg

    def update(self, pos, speed, direction, time):
        #print "Martian updated:", pos, speed, direction, time
        self.positions.append((pos, speed, direction, time))

    def predict(self, time):
        r = math.radians(self.direction)
        x, y = self.pos
        dt = time - self.time
        sp = self.speed
        return (x + dt * sp * math.cos(r) , y + dt * sp * math.sin(r))

    def _get_pos(self):
        return self.positions[-1][0]

    def _get_speed(self):
        return self.positions[-1][1]

    def _get_direction(self):
        return self.positions[-1][2]

    def _get_time(self):
        return self.positions[-1][3]

    pos = property(_get_pos)
    speed = property(_get_speed)
    direction = property(_get_direction)
    time = property(_get_time)

class Rover(object):
    def __init__(self, world, minsensor, maxsensor, maxspeed, maxturn, maxhardturn):
        self.world = world
        self.minsensor = minsensor
        self.maxsensor = maxsensor
        self.maxspeed = maxspeed
        self.maxturn = maxturn
        self.maxhardturn = maxhardturn
        self.acceleration = None
        self.retardation = None
        self.drag = None
        self.path = None
        self.radius = 0.5
        self.time = 0.0
        self.strategy = strategies.PidPathFollower(self, 7.0, 0.0, 1.0)
        self.reset()

    def ok(self):
        return self.old != None

    def reset(self):
        self.path = None
        self.old = None
        self.old_paths = []
        self.calc_needed = False
        self.path_needed = True
        self.ctl_acc = 0
        self.ctl_turn = 0
        self.pos = None
        self.direction = 0
        self.speed = 0
        self.time = 0.0
        self.strategy.reset()

    def get_svg(self):
        svg = ["<polyline fill=\"none\" stroke=\"blue\" stroke-width=\"1\" points=\""]
        for r in self.old:
            x, y = r[2]
            svg.append("%f, %f " % (x, y))
        svg.append("\" />")
        x, y = self.pos
        svg.append("<circle cx=\"%f\" cy=\"%f\" r=\"%f\" style=\"fill:%s;\" />\n" % (x, y, self.radius, "#ffff00"))
        return svg

    def update(self, time, ctl_acc, ctl_turn, pos, direction, speed):
        dt = 0.001 * (time - self.time)
        if self.old != None:
            self.old.append((self.ctl_acc, self.ctl_turn, self.pos, self.direction, self.speed))
        else:
            self.old = []
        if (self.acceleration is None) and ctl_acc == 'a':
            if self.speed > 0.1 * self.maxspeed:
                acceleration = (speed - self.speed) / dt
                self.drag = acceleration / (self.maxspeed ** 2 - speed ** 2)
                print 'Calculated drag coefficient =', self.drag
                self.acceleration = self.drag * self.maxspeed ** 2
                print 'Calculated acceleration =', self.acceleration
        if (self.retardation is None) and (ctl_acc == 'b') and (speed - self.speed) < 0 and (self.drag is not None):
            self.retardation = min((speed - self.speed) / dt + self.drag * speed ** 2, -0.1)
            print 'Calculated retardation =', self.retardation
        self.time = time
        self.ctl_acc = ctl_acc
        self.ctl_turn = ctl_turn
        self.pos = pos
        self.direction = direction
        self.speed = speed
        self.calc_needed = True
        if self.path:
            if self.path.distance(pos) > 10.0:
                #print "Calculating new path!"
                self.schedule_calc_path()

    def schedule_calc_path(self):
        self.path_needed = True

    def set_strategy(self, strategy):
        self.strategy = strategy
        
    def calc_command(self):
        if self.path_needed:
            if self.pos != None:
                self.old_paths.append(self.path)
                self.path = self.strategy.calc_path(self)
                self.path_needed = False
        if not self.calc_needed or self.path == None or self.pos == None:
            #print "no calc needed"
            return ""
        cmd = self.strategy.calc_command(self)
        self.calc_needed = False #True
        #print cmd
        return cmd
        
class World(object):
    def __init__(self, initmsg):
        self.area = Area(initmsg.dx, initmsg.dy)
        self.time_limit = initmsg.time_limit
        self.rover = Rover(self, 
                           initmsg.min_sensor, 
                           initmsg.max_sensor, 
                           initmsg.max_speed, 
                           initmsg.max_turn, 
                           initmsg.max_hard_turn)                           
        self.boulders = {}                   
        self.craters = {}                   
        self.martians = []
        self.old_martians = []
        self.runs = 0
        self.currentobjects = []

    def reset(self):
        #f = open("map_%d.svg" % self.runs, "w")
        #f.write("".join(self.get_svg()))
        self.martians = []
        self.old_martians = []
        self.rover.reset()
        self.runs += 1
        print "Completed run", self.runs

    def find_martian(self, pos, time):
        x, y = pos
        candidate = None
        mindsq = 1.0e10
        recent = (m for m in self.martians if (time - m.time) < 2000.0)
        for m in recent:
            mx, my = m.predict(time)
            dx = x - mx
            dy = y - my
            dsq = dx * dx + dy * dy
            if dsq < mindsq:
                mindsq = dsq
                candidate = m        
        return candidate

    def remove_martians(self):
        # remove old martians
        newm = []
        for m in self.martians:
            if (self.time - m.time) < 5000.0:
                newm.append(m)
            else:
                self.old_martians.append(m)

    def update(self, tmsg):
        self.rover.update(tmsg.time,
                          tmsg.vehicle_ctl_acc,
                          tmsg.vehicle_ctl_turn,
                          (tmsg.vehicle_x, tmsg.vehicle_y),
                          tmsg.vehicle_dir,
                          tmsg.vehicle_speed)
        self.time = tmsg.time
        self.currentobjects = []
        if tmsg.home:
            x, y, radius = tmsg.home
            self.currentobjects.append(Home((x, y), radius))
            dhome = abs(Vector(self.rover.pos) - Vector(0.0, 0.0))
            if dhome < 5.0:
                # Home!
                print "Reached home!"
                return
        for b in tmsg.boulders:
            x, y, radius = b
            self.currentobjects.append(Boulder((x, y), radius))
            if (x, y) not in self.boulders:                
                self.boulders[(x, y)] = Boulder((x, y), radius)
                self.rover.schedule_calc_path()
        for c in tmsg.craters:
            x, y, radius = c
            self.currentobjects.append(Crater((x, y), radius))
            if (x, y) not in self.craters:
                self.craters[(x, y)] = Crater((x, y), radius)
                self.rover.schedule_calc_path()
        numm = len(self.martians)
        for e in tmsg.enemies:
            x, y, direction, speed = e
            self.currentobjects.append(Martian((x, y), speed, direction, tmsg.time))
            m = self.find_martian((x, y), tmsg.time)
            if m:
                m.update((x, y), speed, direction, tmsg.time)
            else:
                self.martians.append(Martian((x, y), speed, direction, tmsg.time))
            self.rover.schedule_calc_path()
        self.remove_martians()
        if numm != len(self.martians):
            print "Number of martians:", len(self.martians)

    def get_svg(self, svg_include = []):
        svg = ["<?xml version=\"1.0\" standalone=\"no\"?>\n",
               "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n",
               "<svg width=\"%f\" height=\"%f\" viewbox=\"0 0 %f %f\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\">\n" % (self.area.dx, self.area.dy, self.area.dx, self.area.dy),
               "<g transform=\"translate(%f, %f) scale(1.0, -1.0)\" style=\"fill-opacity:1.0; stroke:black; stroke-width:1;\">\n" % (self.area.dx/2.0, self.area.dy/2.0),
               "<rect x=\"0\" y=\"0\" width=\"%f\" height=\"%f\" style=\"fill:#ffffff;\"/>"]
        for k, b in self.boulders.items():
            svg.extend(b.get_svg())
        for k, c in self.craters.items():
            svg.extend(c.get_svg())
        for m in self.martians:
            svg.extend(m.get_svg())
        for m in self.old_martians:
            svg.extend(m.get_svg())
        try:
            svg.extend(self.rover.get_svg())
        except TypeError:
            pass
        svg.extend(svg_include)
        svg.append("</g>\n</svg>\n")
        return svg

        

        
        
