import math
from vector import Vector

BOULDER_RADIUS_MODIFIER = 0.5
CRATER_RADIUS_MODIFIER = 0.2

def find_path(start, goal, world, obstacles = None):
    # Find obstacles along the path from start to goal.
    if obstacles is None:
        obstacles = find_obstacles(start, goal, world)
    if len(obstacles) > 0:
        # Sort obstacles and take the one which is closest to the start point.
        obstacles.sort()
        # Calculate new paths passing both sides of the closest obstacle.
        obstacle = obstacles[0]
        n1, n2 = find_new_nodes(start, obstacle.pos, obstacle.radius)
        # Find the number of obstacles along the new paths.
        obstacles_start_n1 = find_obstacles(start, n1)
        obstacles_start_n2 = find_obstacles(start, n2)
        obstacles_n1_goal = find_obstacles(n1, goal)
        obstacles_n2_goal = find_obstacles(n2, goal)
        obstacle_num_1 = len(obstacles_start_n1) + len(obstacles_n1_goal)
        obstacle_num_2 = len(obstacles_start_n2) + len(obstacles_n2_goal)
        # Select the path with the fewest obstacles and discard the other one.
        # Calculate new path segments recursively.
        if obstacle_num_1 < obstacle_num_2:
            path = find_path(start, n1, world, obstacles_start_n1)[:-1]
            path.extend(find_path(n1, goal, world, obstacles_n1_goal))
            return path
        else:
            path = find_path(start, n2, world, obstacles_start_n2)[:-1]
            path.extend(find_path(n2, goal, world, obstacles_n2_goal))
            return path
    else:
        return [start, goal]
    
def find_new_nodes(start, center, radius):
    xs, ys = start
    xc, yc = center
    # Vector pointing at start:
    vs = Vector(xs, ys)
    # Vector pointing at center:
    vc = Vector(xc, yc)
    # Distance from start to center:
    dsc = abs(vc - vs)
    # Distance from start to tangent:
    dst = math.sqrt(dsc ** 2 - radius ** 2)
    # Angle between vector(start->center) and vector(start->tangent):
    a = math.acos(dst / dsc)
    # Normalized vector pointing at center:
    vcn = vc.normalize()
    # Vectors pointing in the direction of the tangents, but with an extra distance
    # added (1.0 * radius). These are the new nodes:
    vt1 = (dst + radius) * vcn.rotate(a)
    vt2 = (dst + radius) * vcn.rotate(-a)
    return (vt1.point(), vt2.point())
    
def find_obstacles(start, goal, world):
    obstacles = []
    xs, ys = start
    xg, yg = goal
    # Vector pointing at start:
    vs = Vector(xs, ys)
    # Vector pointing at goal:
    vg = Vector(xg, yg)
    # Find boulders along the path:
    for boulder in world.boulders.itervalues():
        if intersection(vs, vg, boulder.pos, boulder.radius + BOULDER_RADIUS_MODIFIER):
            # Vector pointing at boulder:
            vb = Vector(boulder.pos[0], boulder.pos[1])
            # Distance to boulder:
            d = abs(vb - vs)
            obstacles.append((d, boulder))
    # Find craters along the path:
    for crater in world.craters.itervalues():
        if intersection(vs, vg, crater.pos, crater.radius + CRATER_RADIUS_MODIFIER):
            # Vector pointing at crater:
            vc = Vector(crater.pos[0], crater.pos[1])
            # Distance to crater:
            d = abs(vc - vs)
            obstacles.append((d, crater))
    return obstacles
    
def intersection(start_vector, goal_vector, center, radius):
    xc, yc = center
    # Vector pointing at center:
    vc = Vector(xc, yc)
    # Vector (start->goal):
    vsg = goal_vector - start_vector
    # Vector (start->center):
    vsc = vc - start_vector
    # Intersection test:
    s = vsg * vsc
    if s < 0:
        return False
    else:
        m2 = abs(vsc) ** 2 - s ** 2
        return radius ** 2 > m2
        
    
if __name__ == '__main__':
    print find_new_nodes((0.0, 0.0), (5.0, 0.0), 1.0)
    