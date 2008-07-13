from vector import Vector

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


def create_nodes_obstacles(world):
    obstacles = []
    for boulder in world.boulders.itervalues():
        obstacles.append((boulder.pos, boulder.radius))
    for crater in world.craters.itervalues():
        obstacles.append((crater.pos, crater.radius))
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
    return list(nodes), obstacles

if __name__=="__main__":
    import sys
    import testpath
    if len(sys.argv) > 1:
        map_filename = sys.argv[1]
        svg_filename = map_filename + '_nodes.svg'
        w = testpath.create_world(map_filename)
        nodes, obstacles = create_nodes_obstacles(w)
        svg = []
        print "Nodes found:", len(nodes)
        for n in nodes:
            x, y = n
            #print x, y
            svg.append("<circle cx=\"%d\" cy=\"%d\" r=\"%d\" style=\"fill:%s;\" />\n" % (x, y, 1, "#00ffff"))
        svg = w.get_svg(svg)
        f = open(svg_filename, 'w')
        f.write(''.join(svg))
        f.close()
    else:
        print 'Map name missing.'




        
        
        
