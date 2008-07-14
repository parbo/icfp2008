from vector import Vector, intersection, ITYPE_ENTER, ITYPE_EXIT

def find_nearest(pos, obstacles):
    mind = 1e10
    nearest = []
    for obstacle in obstacles:
        if pos == obstacle[0]:
            continue
        vp = Vector(pos)
        vo = Vector(obstacle[0])
        d = abs(vp - vo)
        nearest.append((d, obstacle))
    nearest.sort()
    return nearest[:3]

def create_nodes(obstacles):
    nodes = set()
    for obstacle in obstacles:
        pos, r = obstacle        
        vp = Vector(pos)
        nearestlist = find_nearest(pos, obstacles)
        for n in nearestlist:
            d, nearest = n
            npos, nr = nearest
            # distance between obstacles egdes
            middist = (d - nr - r) / 2
            # direction to nearest
            vnp = Vector(npos)
            vodn = (vnp - vp).normalize()
            # point between obstacle and nearest
            midpoint = vp + (r + middist) * vodn
            nodes.add(midpoint.point())
    return list(nodes)

def get_pairs(seq):
    pairs = []
    for i, s1 in enumerate(seq):
        for s2 in seq[i:]:
            pairs.append((s1, s2))
    return pairs

class Node(object):
    def __init__(self, pos):        
        self.pos = pos

class Entrance(object):
    def __init__(self, pos):        
        self.pos = pos
        
    def __str__(self):
        return "Entrance(%s)"%(str(self.pos))

class Segment(object):
    TOP = 1
    LEFT = 2
    BOTTOM = 3
    RIGHT = 4
    def __init__(self, t, startx, starty, stopx, stopy):
        self.type = t
        self.startvec = Vector(startx, starty)
        self.stopvec = Vector(stopx, stopy)
        self.intersections = []        
        self.entrances = [Entrance((startx + (stopx - startx) / 2, starty + (stopy - starty) / 2))]

    def adjacent_type(self, segmenttype):
        if segmenttype == Segment.BOTTOM:
            return Segment.TOP
        elif segmenttype == Segment.TOP:
            return Segment.BOTTOM
        elif segmenttype == Segment.LEFT:
            return Segment.RIGHT
        elif segmenttype == Segment.RIGHT:
            return Segment.LEFT

    def add_intersection(self, obj):
        pos, r = obj
        intersections = intersection(self.startvec, self.stopvec, pos, r)
        if not intersections:
            return
        self.intersections.append((obj, intersections))
        linesegments = []
        curr = None
        level = 0
        segmentlength = abs(self.stopvec - self.startvec)
        points = [0.0, segmentlength]
        # find all intersection points
        for obj, isect in self.intersections:
            points.extend([i[0] for i in isect])
        points.sort()
        # find all linesegments
        linesegments = []
        lastp = None
        for p in points:
            if lastp != None:
                linesegments.append((lastp, p))
            lastp = p
        # prune line segments
        pruned = []
        for lstart, lstop in linesegments:
            remove = False
            for obj, isect in self.intersections:                
                start = 0.0
                end = segmentlength
                for i in isect:
                    if i[1] == ITYPE_ENTER:
                        start = i[0]
                    elif i[1] == ITYPE_EXIT:
                        end = i[0]
                if start <=  lstart + (lstop - lstart) / 2.0 < end:
                    remove = True
                    break
            if not remove:
                pruned.append((lstart, lstop))
        self.entrances = []
        vd = (self.stopvec - self.startvec) * (1 / segmentlength)
        for start, stop in pruned:
            midpoint = start + (stop - start) / 2.0
            self.entrances.append(Entrance((self.startvec + midpoint * vd).point()))
        for e in self.entrances:
            print e
                

class Cluster(object):
    def __init__(self, pos, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.segments = [None, 
                         Segment(Segment.TOP, left, top, right, top), 
                         Segment(Segment.LEFT, left, top, left, bottom), 
                         Segment(Segment.BOTTOM, left, bottom, right, bottom), 
                         Segment(Segment.RIGHT, right, top, right, bottom)]
        self.objects = []
        self.pos = pos

    def __str__(self):
        return "Cluster: (%d, %d)"%(self.pos[0], self.pos[1])

    def get_svg(self):
        svg = ["<rect x=\"%f\" y=\"%f\" width=\"%f\" height=\"%f\" style=\"fill:blue;stroke:pink;stroke-width:2;fill-opacity:0.05;stroke-opacity:0.9\"/>\n" % (self.left, self.bottom, self.right-self.left, self.top-self.bottom)]
        return svg

    def get_segments_svg(self):
        svg = []
        for s in self.segments[1:]:
            for e in s.entrances:
                x, y = e.pos
                svg.append("<circle cx=\"%f\" cy=\"%f\" r=\"%f\" style=\"fill:%s;\" />\n" % (x, y, 3, "#ff00ff"))
        return svg

    def adjacent(self, other):
        x1, y1 = self.pos
        x2, y2 = other.pos
        if x1 == x2:
            if y1 - y2 == 1:
                return Segment.TOP
            elif y2 - y1 == 1:
                return Segment.BOTTOM
        elif y1 == y2:
            if x1 - x2 == 1:
                return Segment.LEFT
            elif x2 - x1 == 1:
                return Segment.RIGHT
        return False

    def add_segment_intersection(self, segmenttype, obj):
        self.segments[segmenttype].add_intersection(obj)

    def any_inside(self, obj):
        pos, r = obj
        x, y = pos
        res = self.left - r <= x < self.right + r and self.top - r <= y < self.bottom + r
        return res

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

    def find_path():
        pass

    def get_svg(self):
        svg = []
        for c in self.clusters:
            svg.extend(c.get_svg())
        for c in self.clusters:
            svg.extend(c.get_segments_svg())
        return svg

    def add_object(self, obj):
        added_to = []
        for c in self.clusters:
            if c.any_inside(obj):
                c.add(obj)
                added_to.append(c)
        for c1, c2 in get_pairs(added_to):
            segmenttype = c1.adjacent(c2)
            if segmenttype:
                self.update_entrances(c1, c2, segmenttype, obj) 

    def update_entrances(self, c1, c2, segmenttype, obj):
        c1.add_segment_intersection(segmenttype, obj)
        c1seg = c1.segments[segmenttype]
        c2.segments[c1seg.adjacent_type(segmenttype)] = c1seg

    def _build_clusters(self):
        x, y = self.left, self.bottom
        xp = 0
        yp = 0
        while y < self.top:
            ch = min(self.top - y, self.maxclustersize)
            while x < self.right:
                cw = min(self.right - x, self.maxclustersize)
                c = Cluster((xp, yp), x, y, x + cw, y + ch)
                self.clusters.append(c)
                xp += 1
                x += cw
            x = self.left
            xp = 0
            yp += 1
            y += ch

if __name__=="__main__":
    import sys
    import testpath

    if len(sys.argv) > 1:
        map_filename = sys.argv[1]
        w = testpath.create_world(map_filename)
        obstacles = [(b.pos, b.radius) for b in w.boulders.itervalues()] + [(c.pos, c.radius) for c in w.craters.itervalues()]
        print w.area.left, w.area.top, w.area.right, w.area.bottom
        m = Map(obstacles, w.area.left, w.area.top, w.area.right, w.area.bottom, 64)
        svg_filename = map_filename + '_hrgreppa.svg'
        svg = w.get_svg(m.get_svg())
        f = open(svg_filename, 'w')
        f.write(''.join(svg))
        f.close()
    else:
        print get_pairs([1, 2, 3, 4, 5])
        obstacles = [((42, 100), 30),
                     ((6, 100), 10),
                     ((142, 100), 10)]
        m = Map(obstacles, -250, -250, 250, 250, 64)
