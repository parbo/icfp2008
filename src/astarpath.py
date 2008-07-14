import math
import heapq
from vector import Vector, intersection
import  world as WorldModule
import nearest

def create_nodes_obstacles(world):
    nodes = []
    obstacles = []
    for boulder in world.boulders.itervalues():
        x, y = boulder.pos
        r = boulder.radius + 5
        nodes.append((x + r, y + r))
        nodes.append((x + r, y - r))
        nodes.append((x - r, y + r))
        nodes.append((x - r, y - r))
        obstacles.append((boulder.pos, boulder.radius))
    for crater in world.craters.itervalues():
        x, y = crater.pos
        r = crater.radius + 5
        nodes.append((x + r, y + r))
        nodes.append((x + r, y - r))
        nodes.append((x - r, y + r))
        nodes.append((x - r, y - r))
        obstacles.append((crater.pos, crater.radius))
    return nodes, obstacles

def find_neighbour_nodes(node, closedlist, nodes, obstacles):
    vs = Vector(node)
    nb = []
    for n in nodes:
        if n == node:
            continue
        if n in closedlist:
            continue
        vn = Vector(n)
        for pos, radius in obstacles:
            if intersection(vs, vn, pos, radius):
                break
        else:
            nb.append(n)
    return nb

# Wikipedia reference
# function A*(start,goal)
#      closedlist := the empty set               % The set of nodes already evaluated.
#      openlist := set containing the start node % The set of tentative nodes to be evaluated.
#      g_score[start] := 0                       % Distance from start along optimal path.
#      while openlist is not empty
#          x := the node in openlist having the lowest f_score[] value
#          if x = goal
#              return path traced through came_from[]
#          remove x from openlist
#          add x to closedlist
#          foreach y in neighbor_nodes(x)
#              if y in closedlist
#                  continue
#              tentative_g_score := g_score[x] + dist_between(x,y)
#              tentative_is_better := false
#              if y not in openlist
#                  add y to openlist
#                  h_score[y] := estimated_distance_to_goal(y)
#                  tentative_is_better := true
#              elsif tentative_g_score < g_score[y]
#                  tentative_is_better := true
#              if tentative_is_better = true
#                  came_from[y] := x
#                  g_score[y] := tentative_g_score
#                  f_score[y] := g_score[y] + h_score[y] % Estimated total distance from start to goal through y.
#      return failure

BUDGET = 1000
def find_path(start, goal, world):
    # Solve problem using A* algorithm.
    allnodes, obstacles = nearest.create_nodes_obstacles(world)    
    allnodes.append(goal)

    came_from = {}
    def reconstruct_path(node):
        path = [node]
        while node in came_from:
            node = came_from[node]
            path.append(node)
        path.reverse()
        return path

    closedlist = set()
    openlist = set()
    openlist.add(start)
    queue = []
    heapq.heappush(queue, (abs(Vector(start) - Vector(goal)), start))
    g_score = {}
    g_score[start] = 0    
    h_score = {}
    ctr = 0
    while openlist and ctr < 4:
        ctr += 1
        v, node = heapq.heappop(queue)
        if node in closedlist:
            continue
        openlist.remove(node)
        if node == goal:
            path = reconstruct_path(node)
            print "Returning complete path", len(path), ctr
            print path
            return path
        closedlist.add(node)
        nb = find_neighbour_nodes(node, closedlist, allnodes, obstacles)
        for n in nb:
            # closedlist is checked in find_neighbour_nodes instead of here
            t_g_score = g_score[node] + abs(Vector(node) - Vector(n))
            t_is_better = False
            if n not in openlist:
                h_score[n] = abs(Vector(n) - Vector(goal))
                t_is_better = True
            elif t_g_score < g_score[n]:
                t_is_better = True

            if t_is_better:
                came_from[n] = node
                g_score[n] = t_g_score
                f_score = t_g_score + h_score[n]
                heapq.heappush(queue, (f_score, n))
                openlist.add(n)                
    if openlist:
        v, node = heapq.heappop(queue)
        path = reconstruct_path(node)
        path.append(goal)
        print "Returning incomplete path", len(path), ctr
        print path
        return path        
    return []
                    
