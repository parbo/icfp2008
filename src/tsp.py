import graph
import math
import random
import heapq
import copy
import time

def VertexDistance(v, w):
    return Distance(v.Data(), w.Data())

def Distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
def MstCost(nodes):
    distance = dict.fromkeys(nodes)
    notProcessed = dict.fromkeys(nodes)
    v = nodes[0]
    distance[v] = 0
    q = [(distance[v], v)]
    
    while (len(notProcessed) > 0):
        d, v = heapq.heappop(q)
        if v in notProcessed:
            del notProcessed[v]
            for v2 in notProcessed.iterkeys():
                if (distance[v2] == None) or (distance[v2] > Distance(v, v2)):
                    distance[v2] = Distance(v, v2)
                    heapq.heappush(q, (distance[v2], v2))
   
    return sum(distance.itervalues())
    
def g(state):
    # Solution cost so far.
    v, nv = state
    return sum([Distance(v[i - 1], v[i]) for i in range(1, len(v))])
    
def h1(state):
    # Estimated cost to goal.
    # Estimation = MST of remaining nodes, including start node and last added node.
    v, nv = state
    vertices = [graph.Vertex(data = v[0])]
    if len(v) > 1:
        vertices.append(graph.Vertex(data = v[-1]))
    vertices.extend([graph.Vertex(data = d) for d in nv])
    nvg = graph.MakeCompleteGraph(vertices, VertexDistance)
    return nvg.MinSpanTree(True)
    
def h2(state):
    # Estimated cost to goal.
    # Estimation = Distance to most remote node + distance from most remote node to goal node.
    v, nv = state
    if nv:
        d = [Distance(v[-1], n) for n in nv]
        # Find most remote node.
        mrd = d[0]
        mri = 0
        for i, di in enumerate(d[1:]):
            if di > mrd:
                mrd = di
                mri = i + 1
        return mrd + Distance(v[0], nv[mri])
    else:
        return Distance(v[0], v[-1])
                
def h3(state):
    # Estimated cost to goal.
    # Estimation = MST of remaining nodes, including start node and last added node.
    # Remember previously calculated MST values.
    v, nv = state
    p = v[0:1]
    if len(v) > 1:
        p.append(v[-1])
    p.extend(nv)
    t = tuple(p)
    if t not in h3.mstcache:
        h3.mstcache[t] = h4(state)
    return h3.mstcache[t]
        
h3.mstcache = {}

def h4(state):
    # Estimated cost to goal.
    # Estimation = MST of remaining nodes, including start node and last added node.
    # Uses optimized MST function.
    v, nv = state
    nodes = [v[0]]
    if len(v) > 1:
        nodes.append(v[-1])
    nodes.extend(nv)
    return MstCost(nodes)
    
# Estimated total cost.
f1 = lambda state: g(state) + h1(state)
f2 = lambda state: g(state) + h2(state)
f3 = lambda state: g(state) + h3(state)
f4 = lambda state: g(state) + h4(state)
    
def CreateInitialState(n):
    visited = [(random.random(), random.random())]
    notVisited = [(random.random(), random.random()) for k in range(n - 1)]
    return (visited, notVisited)
    
def GenerateSuccessors(state):
    v, nv = state
    for i, n in enumerate(nv):
        v2 = copy.copy(v)
        nv2 = copy.copy(nv)
        v2.append(nv2.pop(i))
        yield (v2, nv2)
    return
    
def Goal(state):
    v, nv = state
    return (len(nv) == 0)
    
def SolutionCost(state):
    v, nv = state
    return sum([Distance(v[i - 1], v[i]) for i in range(len(v))])
    
def Solve(state, f = f3):
    # Solve problem using A* algorithm.
    numExpanded = 0
    queue = []
    while not Goal(state):
        for s in GenerateSuccessors(state):
            heapq.heappush(queue, (f(s), s))
        v, state = heapq.heappop(queue)
        numExpanded += 1
    print 'Expanded ' + str(numExpanded) + ' nodes.'
    print 'Remaining heap size: ' + str(len(queue))
    return state
        
if __name__ == '__main__':
    state = CreateInitialState(12)
    state2 = copy.copy(state)
    t = time.clock()
    state = Solve(state, f4)
    print 'Cost: ' + str(SolutionCost(state))
    print 'Time: ' + str(round(time.clock() - t, 3))
    print ''
    t = time.clock()
    state2 = Solve(state2, f3)
    print 'Cost: ' + str(SolutionCost(state))
    print 'Time: ' + str(round(time.clock() - t, 3))
    print 'MST cache size: ' + str(len(h3.mstcache))