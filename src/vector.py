import math

class Vector(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        return
        
    def __str__(self):
        return 'Vector(' + str(self.x) + ', ' + str(self.y) + ')'
        
    def __mul__(self, other):
        if isinstance(other, Vector):
            # Dot product.
            return self.x * other.x + self.y * other.y
        elif isinstance(other, int) or isinstance(other, float):
            # Element product.
            return Vector(other * self.x, other * self.y)
        else:
            raise TypeError
        
    def __rmul__(self, other):
        return self * other
        
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        else:
            raise TypeError
            
    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        else:
            raise TypeError
            
    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
        
    def normalize(self):
        return Vector(self.x / abs(self), self.y / abs(self))
        
    def rotate(self, angle):
        return Vector(self.x * math.cos(angle) - self.y * math.sin(angle), self.x * math.sin(angle) + self.y * math.cos(angle))
        
    def angle(self, other):
        return math.acos(self * other / (abs(self) * abs(other)))

    def point(self):
        return (self.x, self.y)           


class Sphere(Primitive):                                                                                      
    def intersect(self, raypos, raydir):                                                                      
        tr = self.transform                                                                                   
        raydir = tr.inv_transform_vector(raydir)                                                              
        scale = 1.0 / length(raydir)                                                                          
        raydir = mul(raydir, scale) # normalize                                                               
        raypos = tr.inv_transform_point(raypos)                                                               
        s = dot(neg(raypos), raydir)                                                                          
        lsq = dot(raypos, raypos)                                                                             
        if s < 0.0 and lsq > 1.0:                                                                             
            return []                                                                                         
        msq = lsq - s * s                                                                                     
        if msq > 1.0:                                                                                         
            return []                                                                                         
        q = math.sqrt(1.0 - msq)                                                                              
        t1 = s + q                                                                                            
        t2 = s - q                                                                                            
        if t1 > t2:                                                                                           
            t1, t2 = t2, t1                                                                                   
        ts = []                                                                                               
        if t1 > 0.0:                                                                                          
            ts.append(Intersection(scale, t1, raypos, raydir, self, Intersection.ENTRY, 0))                   
        if t2 > 0.0:                                                                                          
            ts.append(Intersection(scale, t2, raypos, raydir, self, Intersection.EXIT, 0))                    
        return ts                                                                                             
                                                                                                            
        
if __name__ == '__main__':
    v1 = Vector(1, 2)
    v2 = Vector(4, 5)
    v3 = Vector(1, 0)
    v4 = Vector(1, 1)
    print 'v1 =', v1
    print 'v2 =', v2
    print 'v3 =', v3
    print 'v4 =', v4
    print 'v1 + v2 =', v1 + v2
    print 'v1 - v2 =', v1 - v2
    print 'v1 * v2 =', v1 * v2
    print '2 * v1 =', 2 * v1
    print 'v2 * 0.5 =', v2 * 0.5
    print 'abs(v1) =', abs(v1)
    print 'v1.normalize() =', v1.normalize()
    print 'abs(v1.normalize()) =', abs(v1.normalize())
    print 'v3.rotate(pi / 2) =', v3.rotate(math.pi / 2)
    print 'v3.rotate(pi / 4) =', v3.rotate(math.pi / 4)
    print 'v3.rotate(-pi / 4) =', v3.rotate(-math.pi / 4)
    print 'v3.angle(v4) =', v3.angle(v4)
    print 'v4.angle(v3) =', v4.angle(v3)
