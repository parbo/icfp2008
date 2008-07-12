import math

class Path(object):
    def __init__(self, points):
        self.points = points

    def current_segment(self, pos, threshold):        
        if len(self.points) > 2:
            x, y = pos
            p = self.points[1]
            dx = x - p[0]
            dy = y - p[1]
            d = dx * dx + dy * dy
            if d < threshold:
                self.points = self.points[1:]
        return self.points[0:2]                           

class BaseStrategy(object):
    def calc_command(self, rover):
        return ""
        

class SimplePathFollower(BaseStrategy):
    def calc_command(self, rover):
        x, y = rover.pos
        r = math.radians(rover.direction)
        seg = rover.path.current_segment(rover.pos, 4.0)
        x2, y2 = seg[1]
        print "segment:", (x, y), (x2, y2)
        h = math.atan2(y2-y, x2-x)
        a = r - h
        print "Wanted", a, "current", r, "difference", h
        cmd = ""
        absa = abs(a)
        if absa > 0.7:
            cmd = "b"
        elif absa > 0.4:
            pass
        else:            
            cmd = "a"

        cmd = ""

        if absa > 2.0:
            # turn hard
            if a < 0:
                cmd += "l"
            else:
                cmd += "r"
        elif absa > 0.2:
            # turn
            if a < 0:
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
        return cmd
