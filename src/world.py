import math

class Area(object):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy
        self.left = -dx/2.0
        self.right = dx/2.0
        self.bottom = -dy/2.0
        self.top = dy/2.0

class Boulder(object):
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius

    def get_svg(self):
        x, y = self.pos
        return ["<circle cx=\"%d\" cy=\"%d\" r=\"%d\" style=\"fill:%s;\" />\n" % (x, y, self.radius, "#ff0000")]

class Crater(object):
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius

    def get_svg(self):
        x, y = self.pos
        return ["<circle cx=\"%d\" cy=\"%d\" r=\"%d\" style=\"fill:%s;\" />\n" % (x, y, self.radius, "#00ff00")]

class Martian(object):
    def __init__(self, pos, speed, direction, time):
        self.positions = []
        self.radius = 0.5
        self.update(pos, speed, direction, time)    

    def get_svg(self):
        svg = []
        x, y = self.pos
        svg.append("<circle cx=\"%d\" cy=\"%d\" r=\"%d\" style=\"fill:%s;\" />\n" % (x, y, self.radius, "#0000ff"))
        return svg

    def update(self, pos, speed, direction, time):
        print "Martian updated:", pos, speed, direction, time
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
    def __init__(self, minsensor, maxsensor, maxspeed, maxturn, maxhardturn):
        self.minsensor = minsensor
        self.maxsensor = maxsensor
        self.maxspeed = maxspeed
        self.maxturn = maxturn
        self.maxhardturn = maxhardturn
        self.acceleration = 1.0
        self.retardation = -1.0
        self.update("-", "-", (0.0, 0.0), 0.0, 0.0)
        self.radius = 0.5

    def get_svg(self):
        x, y = self.pos
        return ["<circle cx=\"%d\" cy=\"%d\" r=\"%d\" style=\"fill:%s;\" />\n" % (x, y, self.radius, "#ffff00")]

    def update(self, ctl_acc, ctl_turn, pos, direction, speed):
        self.ctl_acc = ctl_acc
        self.ctl_turn = ctl_turn
        self.pos = pos
        self.direction = direction
        self.speed = speed
        
    def calc_command(self):
        return "a"

        
class World(object):
    def __init__(self, initmsg):
        self.area = Area(initmsg.dx, initmsg.dy)
        self.time_limit = initmsg.time_limit
        self.rover = Rover(initmsg.min_sensor, 
                           initmsg.max_sensor, 
                           initmsg.max_speed, 
                           initmsg.max_turn, 
                           initmsg.max_hard_turn)
        self.boulders = {}                   
        self.craters = {}                   
        self.martians = []
        self.old_martians = []
        self.runs = 0

    def reset(self):
        f = open("map_%d.svg" % self.runs, "w")
        f.write("".join(self.get_svg()))
        self.martians = []
        self.old_martians = []
        self.rover.update("-", "-", (0.0, 0.0), 0.0, 0.0)
        self.runs += 1

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
        self.rover.update(tmsg.vehicle_ctl_acc,
                          tmsg.vehicle_ctl_turn,
                          (tmsg.vehicle_x, tmsg.vehicle_y),
                          tmsg.vehicle_dir,
                          tmsg.vehicle_speed)
        self.time = tmsg.time
        for b in tmsg.boulders:
            x, y, radius = b
            if (x, y) not in self.boulders:                
                self.boulders[(x, y)] = Boulder((x, y), radius)
        for c in tmsg.craters:
            x, y, radius = c
            if (x, y) not in self.craters:
                self.craters[(x, y)] = Crater((x, y), radius)
        numm = len(self.martians)
        for e in tmsg.enemies:
            x, y, direction, speed = e
            m = self.find_martian((x, y), tmsg.time)
            if m:
                m.update((x, y), speed, direction, tmsg.time)
            else:
                self.martians.append(Martian((x, y), speed, direction, tmsg.time))
        self.remove_old_martians()
        if numm != len(self.martians):
            print "Number of martians:", len(self.martians)

    def get_svg(self):
        svg = ["<?xml version=\"1.0\" standalone=\"no\"?>\n",
               "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n",
               "<svg width=\"%f\" height=\"%f\" viewbox=\"0 0 %f %f\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\">\n" % (self.area.dx, self.area.dy, self.area.dx, self.area.dy),
               "<g transform=\"translate(%f, %f) scale(1.0, -1.0)\" style=\"fill-opacity:1.0; stroke:black; stroke-width:1;\">\n" % (self.area.dx/2.0, self.area.dy/2.0)]
        for k, b in self.boulders.items():
            svg.extend(b.get_svg())
        for k, c in self.craters.items():
            svg.extend(c.get_svg())
        for m in self.martians:
            svg.extend(m.get_svg())
        for m in self.old_martians:
            svg.extend(m.get_svg())
        svg.extend(self.rover.get_svg())
        svg.append("</g>\n</svg>\n")
        return svg

        

        
        
