

class Entrance(object):
    def __init__(self):        
        pass

class Side(object):
    def __init__(self):
        pass

class Cluster(object):
    TOP = 1
    LEFT = 2
    BOTTOM = 3
    RIGHT = 4
    def __init__(self, pos, coords):
        self.entrances = []
        self.objects = []
        self.pos = pos
        self.coords = coords

    def __str__(self):
        return "Cluster: (%d, %d), ((%f, %f), (%f, %f)"%(self.pos[0], 
                                                         self.pos[1], 
                                                         self.coords[0][0], 
                                                         self.coords[0][1],
                                                         self.coords[1][0], 
                                                         self.coords[1][1])

    def adjacent(self, other):
        x1, y1 = self.pos
        x2, y2 = other.pos
        if x1 == x2:
            if y1 - y2 == 1:
                return Cluster.BOTTOM
            elif y2 - y1 == 1:
                return Cluster.TOP
        elif y1 == y2:
            if x1 - x2 == 1:
                return Cluster.RIGHT
            elif x2 - x1 == 1:
                return Cluster.LEFT
        return False

    def any_inside(self, obj):
        pos, r = obj
        x, y = pos
        left, top = self.coords[0]
        right, bottom = self.coords[1]
        return left - r <= x < right + r and top - r <= y < bottom + r

    def add(self, obj):
        print obj, "added to", str(self)
        self.objects.append(obj)

class Node(object):
    pass

class Map(object):
    def __init__(self, obstacles, left, top, right, bottom, maxclustersize):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.maxclustersize = maxclustersize
        self.clusters = []
        self._build_clusters()        
        for obj in obstacles:            
            self.add_object(obj)

    def add_object(self, obj):
        added_to = []
        for c in self.clusters:
            if c.any_inside(obj):
                c.add(obj)
                added_to.append(c)
        for c1 in added_to:
            for c2 in added_to:
                side = c1.adjacent(c2)
                if side:
                    self.update_entrances(c1, c2, side, obj) 

    def update_entrances(self, c1, c2, side, obj):
        
        pass

    def _build_clusters(self):
        x, y = self.left, self.top
        xp = 0
        yp = 0
        while y < self.bottom:
            ch = min(self.bottom - y, self.maxclustersize)
            while x < self.right:
                cw = min(self.right - x, self.maxclustersize)
                c = Cluster((xp, yp), ((x, y), (x + cw, y + ch)))
                self.clusters.append(c)
                xp += 1
                x += cw
            x = self.left
            xp = 0
            yp += 1
            y += ch

    def build_entrances(self, c1, c2):        
        pass        
    
    def build_clusters(self):
        pass

    def abstract_maze(self):
        pass


if __name__=="__main__":
    obstacles = [((42, 100), 7),
                 ((142, 100), 10)]
    m = Map(obstacles, -250, -250, 250, 250, 64)
    for c in m.clusters:
        print c
