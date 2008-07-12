import sys
import json
import path
import world
import msgparser

def create_world(map_filename):
    f = open(map_filename, 'r')
    mapdata = json.read(f.read())
    f.close()
    w = world.World(create_init_msg(mapdata))
    for b in mapdata['boulders']:
        pos = (b['x'], b['y'])
        boulder = world.Boulder(pos, b['r'])
        w.boulders[pos] = boulder
    for c in mapdata['craters']:
        pos = (c['x'], c['y'])
        crater = world.Crater(pos, c['r'])
        w.craters[pos] = crater
    return w
    
def create_init_msg(mapdata):
    s = ['I']
    s.append(str(mapdata['size']))
    s.append(str(mapdata['size']))
    s.append(str(mapdata['timeLimit']))
    s.append(str(mapdata['vehicleParams']['rearView']))
    s.append(str(mapdata['vehicleParams']['frontView']))
    s.append(str(mapdata['vehicleParams']['maxSpeed']))
    s.append(str(mapdata['vehicleParams']['turn']))
    s.append(str(mapdata['vehicleParams']['hardTurn']))
    s.append(';')
    return msgparser.InitMsg(' '.join(s))
    
def write_svg(filename, wrld, svg):
    f = open(filename, 'w')
    f.write(''.join(wrld.get_svg(svg)))
    f.close()
    
def create_svg(pathlist):
    svg = ['<polyline fill="none" stroke="blue" stroke-width="1" points="']
    for x, y in pathlist:
        svg.append('%f, %f ' % (x, y))
    svg.append('" />')
    return svg

if __name__ == '__main__':
    if len(sys.argv) > 1:
        map_filename = sys.argv[1]
        svg_filename = map_filename + '.svg'
        w = create_world(map_filename)
        start = (w.area.left, w.area.top)
        pathlist = path.find_path(start, (0.0, 0.0), w)
        write_svg(svg_filename, w, create_svg(pathlist))
    else:
        print 'Map name missing.'
