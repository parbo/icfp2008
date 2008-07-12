import math

def class Area(object):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy
        self.left = -dx/2.0
        self.right = dx/2.0
        self.bottom = -dy/2.0
        self.top = dy/2.0

def class Boulder(object):
    def __init__(self, radius, pos):
        self.radius = radius
        self.pos = pos

def class Crater(object):
    def __init__(self, radius, pos):
        self.radius = radius
        self.pos = pos

def class Martian(object):
    def __init__(self, pos, speed, direction, time):
        self.positions = []
        self.update(pos, speed, direction, time)    

    def update(self, pos, speed, direction, time)
        self.positions.append((pos, speed, direction, time))
        self._predicted = None

    def _predict(self):
        r = radians(self.direction)
        x, y = self.pos
        return (x + speed * math.cos(r), y + speed * math.sin(r))

    def _get_pos(self):
        return self.positions[-1][0]

    def _get_speed(self):
        return self.positions[-1][1]

    def _get_direction(self):
        return self.positions[-1][2]

    def _get_time(self):
        return self.positions[-1][3]

    def _get_predicted(self):
        if self._predicted == None:
            self._predicted = self._predict()
        return self._predicted    

    pos = property(_get_pos)
    speed = property(_get_speed)
    direction = property(_get_direction)
    time = property(_get_time)
    predicted = property(_get_predicted)

def class Rover(object):
    def __init__(self, minsensor, maxsensor, maxspeed, maxturn, maxhardturn):
        self.minsensor = minsensor
        self.maxsensor = maxsensor
        self.maxspeed = maxspeed
        self.maxturn = maxturn
        self.maxhardturn = maxhardturn
        self.acceleration = 1.0
        self.retardation = -1.0
        self.update("-", "-", (0.0, 0.0), 0.0, 0.0)

    def update(self, ctl_acc, ctl_turn, pos, direction, speed):
        self.ctl_acc = ctl_acc
        self.ctl_turn = ctl_turn
        self.pos = pos
        self.direction = direction
        self.speed = speed
        
    def calc_command(self):
        return "a"

        
def class World(object):
    def __init__(self, initmsg):
        self.area = Area(initmsg.dx, initmsg.dy)
        self.time_limit = initmsg.time_limit
        self.rover = Rover(initmsg.min_sensor, 
                           initmsg.max_sensor, 
                           initmsg.max_speed, 
                           initmsg.max_turn, 
                           initmsg.max_hardturn)
        self.boulders = {}                   
        self.craters = {}                   
        self.martians = []

    def reset(self):
        self.martians = []
        self.rover.update("-", "-", (0.0, 0.0), 0.0, 0.0)

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
                self.boulders[(x, y)] = b
        for c in tmsg.craters:
            x, y, radius = s
            if (x, y) not in self.craters:
                self.craters[(x, y)] = c
        for e in tmsg.enemies:
            x, y, direction, speed = e
            m = find_martian((x, y))
            if m:
                m.update((x, y), speed, direction, tmsg.time)
            else:
                self.martians.append(Martian((x, y), speed, direction, tmsg.time))
        
