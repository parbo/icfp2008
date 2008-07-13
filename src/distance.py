import math

def distance(pix, w, h):
    # create map with max distance
    maxsq = h*h+w*w 
    dm = [(w, h, maxsq)]*h*w
    for y in range(h):
        offs = y * w
        for x in range(w):
            if pix[x + offs] == 255:
                dm[x + offs] = (0, 0, 0)
            else:
                if y > 0:
                    minx, miny, minsq = dm[x + offs]
                    tminx, tminy, tminsq = dm[x + offs - w]
                    tminy -= 1
                    tminsq = tminx * tminx + tminy * tminy
                    if minsq > tminsq:
                        dm[x + y * w] = tminx, tminy, tminsq
                if x > 0:
                    minx, miny, minsq = dm[x + offs]
                    tminx, tminy, tminsq = dm[(x-1) + offs]
                    tminx -= 1
                    tminsq = tminx * tminx + tminy * tminy
                    if minsq > tminsq:
                        dm[x + offs] = tminx, tminy, tminsq
        for x in range(w-1, -1, -1):
            if pix[x + offs] == 255:
                dm[x + offs] = (0, 0, 0)
            else:
                if x + 1 < w:
                    minx, miny, minsq = dm[x + offs]
                    tminx, tminy, tminsq = dm[(x+1) + offs]
                    tminx += 1
                    tminsq = tminx * tminx + tminy * tminy
                    if minsq > tminsq:
                        dm[x + offs] = tminx, tminy, tminsq
    for y in range(h-1, -1, -1):
        offs = y * w
        for x in range(w):
            if pix[x + offs] == 255:
                dm[x + offs] = (0, 0, 0)
            else:
                if x > 0:
                    minx, miny, minsq = dm[x + offs]
                    tminx, tminy, tminsq = dm[(x-1) + offs]
                    tminx -= 1
                    tminsq = tminx * tminx + tminy * tminy
                    if minsq > tminsq:
                        dm[x + offs] = tminx, tminy, tminsq
        for x in range(w-1, -1, -1):
            if pix[x + offs] == 255:
                dm[x + offs] = (0, 0, 0)
            else:
                if y + 1 < h:
                    minx, miny, minsq = dm[x + offs]
                    tminx, tminy, tminsq = dm[x + offs +  w]
                    tminy += 1
                    tminsq = tminx * tminx + tminy * tminy
                    if minsq > tminsq:
                        dm[x + y * w] = tminx, tminy, tminsq
                if x + 1 < w:
                    minx, miny, minsq = dm[x + offs]
                    tminx, tminy, tminsq = dm[(x+1) + offs]
                    tminx += 1
                    tminsq = tminx * tminx + tminy * tminy
                    if minsq > tminsq:
                        dm[x + offs] = tminx, tminy, tminsq
    return dm

def set_pixel(im, x, y, val):
    pix, w, h = im
    pix[x + y * w] = val

def get_pixel(im, x, y):
    pix, w, h = im
    return pix[x + y * w]

def circle_midpoint(im, xc, yc, r):
    x = 0
    y = r
    def plot():
        set_pixel(im, xc + x, yc + y, 255)
        set_pixel(im, xc - x, yc + y, 255)
        set_pixel(im, xc + x, yc - y, 255)
        set_pixel(im, xc - x, yc - y, 255)
        set_pixel(im, xc + y, yc + x, 255)
        set_pixel(im, xc - y, yc + x, 255)
        set_pixel(im, xc + y, yc - x, 255)
        set_pixel(im, xc - y, yc - x, 255)
    plot()
    p = 1 - r
    while x < y:
        if p < 0:
            x += 1
        else:
            x += 1
            y -= 1
        if p < 0:
            p = p + 2 * x + 1
        else:
            p = p + 2* (x - y) + 1
        plot()


def fill(im, pos, oldp, newp):
    stack = []
    stack.append(pos)
    while stack:
        x, y = stack.pop()
        try:
            if get_pixel(im, x, y) == oldp:
                set_pixel(im, x, y, newp)
                stack.append((x, y + 1))
                stack.append((x, y - 1))
                stack.append((x + 1, y))
                stack.append((x - 1, y))
        except IndexError:                                                                                
            pass
                                                                                                              
def create_im(world, maxpix=512):
    dx = world.area.dx
    dy = world.area.dy
    maxw = max(dx, dy)
    sc = maxpix / maxw
    w = int(math.ceil(sc * dx))
    h = int(math.ceil(sc * dy))
    im = ([0]*w*h, w, h)
    for boulder in world.boulders.itervalues():
        x, y = boulder.pos
        x = int(math.ceil((x - dx / 2) * sc))
        y = int(math.ceil((y + dy / 2) * sc))
        r = int(math.ceil(boulder.radius * sc))
        circle_midpoint(im, x, y, r)
        fill(im, (x, y), 0, 255)
    for crater in world.craters.itervalues():
        x, y = crater.pos
        x = int(math.ceil((x - dx / 2) * sc))
        y = int(math.ceil((y + dy / 2) * sc))
        r = int(math.ceil(crater.radius * sc))
        circle_midpoint(im, x, y, r)
        fill(im, (x, y), 0, 255)
    return im

def threshold(im, t):
    pix, w, h = im
    tpix = []
    for p in pix:
        v = 0.0
        if p > t:
            v = 1.0
        tpix.append(v)    
    return (tpix, w, h)

def convolve(im, kernel):
    pix, w, h = im
    cpix = []
    ks = len(kernel) // 2
    for y in range(h):
        for x in range(w):
            v = 0
            for i, row in enumerate(kernel):
                for j, col in enumerate(row): 
                    px = x - ks + j 
                    py = y - ks + i 
                    if 0 <= px < w and 0 <= py < h:
                        v += col * pix[px + w * py]
            cpix.append(v)
    return (cpix, w, h)
            
def gradient(im):
    kx = [[0.1171, 0, -0.1171], 
          [0.1931, 0, -0.1931], 
          [0.1171, 0, -0.1171]]
    ky = [[0.1171, 0.1931, 0.1171],
          [0, 0, 0], 
          [-0.1171, -0.1931, -0.1171]]
    cx = convolve(im, kx)
    cy = convolve(im, ky)
    write_ppm(cx,"gx.ppm")        
    write_ppm(cy,"gy.ppm")        
    return zip(cx[0], cy[0])

def suppress_non_max(im, g):
    pix, w, h = im
    offsets = [(-1,     1),       # 0
               (-1 - w, 1 + w),   # pi / 4
               (-w,     w),       # pi / 2
               (1 - w,  -1 + w)]  # 3 * pi / 2
    def offset_from_angle(a):
        if a < 0.0:
            a += math.pi
        if (a < math.pi / 8):
            return offsets[0]
        elif (a < 3 * math.pi / 8):
            return offsets[1]
        elif (a < 5 * math.pi / 8):
            return offsets[2]
        elif (a < 7 * math.pi / 8):
            return offsets[3]
        elif (a <= math.pi):
            return offsets[0]
    nm = []
    lp = len(pix)
    for i, p in enumerate(pix):
        gx, gy = g[i]
        a = math.atan2(gy, gx)
        offs = offset_from_angle(a)
        o1, o2 = offs
        if 0 <= i + o1 < lp:
            n1 = pix[i + o1]
        else:
            nm.append(0.0)
            continue
        if 0 <= i + o2 < lp:
            n2 = pix[i + o2]
        else:
            nm.append(0.0)
            continue        
        if p < n1 or p < n2:
            nm.append(0.0)
        else:
            nm.append(1.0)
    return (nm, w, h)        

def write_ppm(im, filename):
    f = open(filename, 'wb')
    pix, w, h = im
    f.write("P6 %s %s 255\n"%(w, h))
    maxp = max(pix)
    if maxp == 0.0:
        maxp = 1.0
    for p in pix:
        scp = int(255.0 * min(max(p, 0.0), maxp) / maxp)
        f.write(chr(scp))
        f.write(chr(scp))
        f.write(chr(scp))
                                                                                                              
if __name__=="__main__":
    import sys
    import testpath
    if len(sys.argv) > 1:
        map_filename = sys.argv[1]
        w = testpath.create_world(map_filename)
        im = create_im(w, 512)
        pix, w, h = im
        write_ppm(im, map_filename + ".ppm")
        dm = distance(pix, w, h)
        dmpix = [math.log(1 + d[2]) for d in dm]
        #dmpix = [d[2] for d in dm]
        dmim = (dmpix, w, h)
        write_ppm(dmim, map_filename + "_dist.ppm")        
        dg = gradient(dmim)
        gim = ([math.sqrt(gx ** 2 + gy ** 2) for gx, gy in dg], w, h)
        write_ppm(gim, map_filename + "_dist_g.ppm")        
        nm = suppress_non_max(dmim, dg)
        write_ppm(nm, map_filename + "_dist_max.ppm")        
    else:
        print 'Map name missing.'
