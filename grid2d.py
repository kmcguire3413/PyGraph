'''
    2D GRID PATH FROM START TO FINISH

    To solve the problem we must path a valid path from start to
    finish and it shall be the shortest path possible.

    The first step to finding an optimal solution is to reduce the
    problem by removing excess elements from the computation. To do
    that we reduce it from a pixel grid to a graph. 

    The graph represents larger sections containing one or more pixels 
    per node. We then find a solution for the graph which represents a 
    solution for the grid.

    The graph is a more efficient form as well because it contains pointers
    to the next node that require no offset calculations which would be required
    if using the grid (to access an adjacent pixel). For example to determine
    which directions we can go from a single pixel we first need to compute the
    offset of each adjacent pixel then read that pixel value and finally determine
    if it is valid then choose it. For the graph we simply iterate the adjacent nodes
    and need no checks as they were pre-validated. 

    One could imagine the graph as a graph of pixels which links to other pixels 
    that are adjacent, except one shall also have to consider the graph more 
    optimized (less graph nodes than pixels).

    The ratio of pixels:graph-nodes lessens when the grid becomes difficult to navigate
    whereby there are more invalid pixels (pixels that can not be traveled on). This is
    because a graph node repsents a rectangle of passable space. So by having smaller
    passable spaces the number of graph nodes approaches the number of valid pixels, but
    in larger more open areas the ratio can be high as 1:52 or almost 1:1. It shall never
    be lower than 1:1 which is essentially a worst case and likely non-realistic grid.



'''
import array
import math
import random

from tgaimage import TGAImage

def solve(grid, w, h, toohigh, start, end):
    # build rectangle portals across grid
    rportals = []

    UNUSED = 1000000
    used = array.array('I', (UNUSED for x in range(0, w * h)))

    y = 0
    ri = 0
    while y < w:
        x = 0
        while x < h:
            # is valid point?
            if grid[y * w + x] < toohigh and used[y * w + x] == UNUSED:
                # find right most point
                for nx in range(x, w):
                    if grid[y * w + nx] >= toohigh or used[y * w + nx] != UNUSED:
                        nx = nx - 1
                        break
                nx = nx + 1
                # see how tall we can make it
                for ny in range(y, h):
                    for _x in range(x, nx):
                        if grid[ny * w + _x] >= toohigh or used[ny * w + _x] != UNUSED:
                            _x = _x - 1
                            break
                    _x = _x + 1

                    if _x < nx:
                        break
                # create rect
                rect = (x, y, nx, ny)
                # gill area and mark rect's index in rportals
                # we will use this later when building an actual
                # graph of the portals
                for __y in range(y, ny):
                    for __x in range(x, nx):
                        used[__y * w + __x] = len(rportals)

                rportals.append(rect)
                x = nx
            else:
                x = x + 1
        y = y + 1
    # go through and build what other rect portals are accessible from
    # each rect portal
    graph = []
    for rpi in range(0, len(rportals)):
        rect = rportals[rpi]
        # break out components
        sx, sy, ex, ey = rect
        # go around border looking for other portals
        bportals = set()
        if sy - 1 > -1:
            for x in range(sx, ex):
                i = used[(sy - 1) * w + x]
                if i != UNUSED:
                    bportals.add(i)
        if ey < h:
            for x in range(sx, ex):
                i = used[ey * w + x]
                if i != UNUSED:
                    bportals.add(i)
        if sx - 1 > -1:
            for y in range(sy, ey):
                i = used[y * w + (sx - 1)]
                if i != UNUSED:
                    bportals.add(i)
        if ex < w:
            for y in range(sy, ey):
                i = used[y * w + ex]
                if i != UNUSED:
                    bportals.add(i)
        # we now have all the portals that are adjacent
        node = [rect, bportals]
        graph.append(node)

    # go through and optimize graph to include a direct
    # link to the border node instead of using an index
    for gni in range(0, len(graph)):
        gn = graph[gni]

        bportals = gn[1]
        _bportals = list()
        for bp in bportals:
            _bportals.append(graph[bp])
        gn[1] = _bportals

    # our graph is now complete and usable

    tga = TGAImage(w, h)
    # first render impassable areas
    ivp = 0
    for y in range(0, h):
        for x in range(0, w):
            if grid[y * w + x] >= toohigh:
                tga.put(x, y, (0, 0, 0))
                ivp = ivp + 1
    tga.save('passable.tga')

    tga = TGAImage(w, h, 12)
    # first render impassable areas
    ivp = 0
    for y in range(0, h):
        for x in range(0, w):
            if grid[y * w + x] >= toohigh:
                tga.put(x, y, (190, 190, 190))
                ivp = ivp + 1

    pc = len(grid) - ivp
    print('portals', len(graph))
    print('valid-pixels', pc)
    print('speed-factor', pc / len(graph))

    colors = (
        (0, 170, 0),
        (0, 90, 170)
    )
    ci = 0
    rc = 0
    # go through and color and mark portals and links
    for gn in graph:
        rect = gn[0]          # our rect
        bnodes = gn[1]        # our border nodes

        sx, sy, ex, ey = rect
        # calculate our center
        cx = sx + ((ex - sx) / 2)
        cy = sy + ((ey - sy) / 2)

        tga.putboxoutline(sx, sy, ex, ey, (90, rc, 90))

        # iterate through border nodes
        rc = (rc + 40) & 0xff
        for bn in bnodes:
            bsx, bsy, bex, bey = bn[0]
            bcx = bsx + ((bex - bsx) / 2)
            bcy = bsy + ((bey - bsy) / 2)            
            # draw line denoting connection (portal)
            tga.putline(cx, cy, bcx, bcy, (rc, 90, 90))

    tga.save('graph_scaled.tga')

def main():
    w = int(math.sqrt(100 * 100))
    h = w

    # create the grid with random values
    random.seed(1029382)

    print('generating grid..')
    grid = array.array('f', (random.random() for x in range(0, int(w*h))))

    print('solving..')
    solve(grid, w, h, 0.8, None, None)


main()