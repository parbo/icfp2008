TYPE_INIT = 'I'
TYPE_TELEMETRY = 'T'

class InitMsg(object):
    def __init__(self, msg):
        tokens = msg.split()
        self.type = TYPE_INIT
        self.dx = float(tokens[1])
        self.dy = float(tokens[2])
        self.time_limit = float(tokens[3])
        self.min_sensor = float(tokens[4])
        self.max_sensor = float(tokens[5])
        self.max_speed = float(tokens[6])
        self.max_turn = float(tokens[7])
        self.max_hard_turn = float(tokens[8])
        return
        
        
class TelemetryMsg(object):
    def __init__(self, msg):
        tokens = msg.split()
        self.type = TYPE_TELEMETRY
        self.time = float(tokens[1])
        self.vehicle_ctl_acc = tokens[2][0]
        self.vehicle_ctl_turn = tokens[2][1]
        self.vehicle_x = float(tokens[3])
        self.vehicle_y = float(tokens[4])
        self.vehicle_dir = float(tokens[5])
        self.vehicle_speed = float(tokens[6])
        self.boulders = []
        self.craters = []
        self.enemies = []
        self.home = None
        self._parse_objects(tokens[7:])
        return
        
    def _parse_objects(self, tokens):
        while len(tokens) > 0:
            if tokens[0] == 'b':
                # Boulder: Represent with tuple (x, y, radius)
                self.boulders.append((float(tokens[1]), float(tokens[2]), float(tokens[3])))
                tokens = tokens[4:]
            elif tokens[0] == 'c':
                # Crater: Represent with tuple (x, y, radius)
                self.craters.append((float(tokens[1]), float(tokens[2]), float(tokens[3])))
                tokens = tokens[4:]
            elif tokens[0] == 'h':
                # Home base: Represent with tuple (x, y, radius)
                self.home = (float(tokens[1]), float(tokens[2]), float(tokens[3]))
                tokens = tokens[4:]
            elif tokens[0] == 'm':
                # Martian: Represent with tuple (x, y, dir, speed)
                self.enemies.append((float(tokens[1]), float(tokens[2]), float(tokens[3]), float(tokens[4])))
                tokens = tokens[5:]
            else:
                raise ValueError('Invalid object type.')
        return