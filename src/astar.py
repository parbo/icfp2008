import heapq

class PriorityQueue(object):
    def __init__(self):
        self.queue = []
        
    def push(self, v):
        heapq.heappush(self.queue, v)

    def pop(self):
        return heapq.heappop(self.queue)

    def __len__(self):
        return len(self.queue)

def astar(start, goal, g_fcn, h_fcn, find_neighbours_fcn):
    def path(came_from, node):
        curr = node
        path = []
        while curr != None:
            path.append(curr)
            curr = came_from[curr]
        path.reverse()
        return path

    closedlist = set()
    openlist = PriorityQueue()
    openlist.push((h_fcn(start), start))
    g_score = {start : 0.0}
    came_from = {start : None}
    while openlist:
        f, node = openlist.pop()
        if node in closedlist:
            continue
        if node == goal:
            return path(came_from, node)
        closedlist.add(node)
        nb = find_neighbours_fcn(node)
        for n in nb:            
            new_g = g_score[node] + g_fcn(node, n)
            new_is_better = False
            if n in closedlist:
                if new_g < g_score[n]:
                    new_is_better = True
                    closedlist.remove(n)
            else:
                new_is_better = True
            if new_is_better:
                f = new_g + h_fcn(n)
                openlist.push((f, n))
                came_from[n] = node
                g_score[n] = new_g
    return []


if __name__=="__main__":
    import math
    def testworld(world):
        world = [list(s) for s in world]
        def g(n1, n2):
            return 1    
        def nf(w):
            def neighbours(n):
                x, y = n
                nb = []
                for dx, dy in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= ny < len(w) and 0 <= nx < len(w[0]):
                        if w[ny][nx] != "*":
                            nb.append((nx, ny))
                return nb
            return neighbours
        def hf(goal):
            def h(n):
                x, y = n
                gx, gy = goal
                return math.sqrt((x - gx)**2 + (y - gy)**2)
            return h
        def find(w, sym):
            for y, row in enumerate(w):
                for x , col in enumerate(row):
                    if col == sym:
                        return x, y
        start = find(world, "s")
        goal = find(world, "g")
        p = astar(start, goal, g, hf(goal), nf(world))
        for x, y in p[1:-1]:
            world[y][x] = "+"
        print "\n".join(["".join(row) for row in world])    

    testworld(["**************************",
               "*                        *",
               "*                     s  *",
               "*                        *",
               "*     ********************",
               "*                        *",
               "*                        *",
               "***********   ************",
               "* g                      *",
               "*                        *",
               "**************************"])
    testworld(["**************************",
               "*                 s      *",
               "*                        *",
               "*                        *",
               "*     ********************",
               "*                        *",
               "*                        *",
               "***********   ************",
               "* g                      *",
               "*                        *",
               "**************************"])
    testworld(["**************************",
               "* s                      *",
               "*                        *",
               "*                        *",
               "*     ********************",
               "*                        *",
               "*                        *",
               "***********   ************",
               "*                        *",
               "*                   g    *",
               "**************************"])
