import math
from vector import Vector, intersection
import world as WorldModule

BOULDER_RADIUS_MODIFIER = 1.0
CRATER_RADIUS_MODIFIER = 1.0

def find_path(start, goal, world):
    # Find obstacles along the path from start to goal.
    obstacles = find_obstacles(start, goal, world)
    if len(obstacles) > 0:
        # Sort obstacles and take the one which is closest to the start point.
        obstacles.sort()
        # Calculate new paths passing both sides of the closest obstacle.
        distance, obstacle = obstacles[0]
        modifier = 0
        if isinstance(obstacle, WorldModule.Boulder):
            modifier = BOULDER_RADIUS_MODIFIER
        elif isinstance(obstacle, WorldModule.Crater):
            modifier = CRATER_RADIUS_MODIFIER
        n1, n2 = find_new_nodes(start, obstacle.pos, obstacle.radius + modifier)
        # Find the number of obstacles along the new paths.
        obstacles_start_n1 = find_obstacles(start, n1, world)
        obstacles_start_n2 = find_obstacles(start, n2, world)
        obstacles_n1_goal = find_obstacles(n1, goal, world)
        obstacles_n2_goal = find_obstacles(n2, goal, world)
        obstacle_num_1 = len(obstacles_start_n1) + len(obstacles_n1_goal)
        obstacle_num_2 = len(obstacles_start_n2) + len(obstacles_n2_goal)
        # Select the path with the fewest obstacles and discard the other one.
        # Calculate new path segments recursively.
        if obstacle_num_1 < obstacle_num_2:
            path = find_path(start, n1, world)[:-1]
            path.extend(find_path(n1, goal, world))
            return path
        else:
            path = find_path(start, n2, world)[:-1]
            path.extend(find_path(n2, goal, world))
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
    # Vector pointing from start to center
    vsc = vc - vs
    # Distance from start to center:
    dsc = abs(vsc)
    # Distance from start to tangent:
    dst = math.sqrt(max(dsc ** 2 - radius ** 2, 0))
    # Angle between vector(start->center) and vector(start->tangent):
    a = 1.01 * math.acos(dst / dsc)
    # Normalized vector pointing from start to center:
    vcn = vsc * (1.0 / dsc)
    # Vectors pointing in the direction of the tangents, but with an extra distance
    # added (1.0 * radius). These are the new nodes:
    vt1 = vs + (dst + radius) * vcn.rotate(a)
    vt2 = vs + (dst + radius) * vcn.rotate(-a)
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
  
      
    
if __name__ == '__main__':
    print find_new_nodes((0.0, 0.0), (5.0, 0.0), 1.0)
    
