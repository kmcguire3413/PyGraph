'''
    Leonard Kevin McGuire Jr 2014

    TSP 2D

    The graph is very simple. It is a 2D plane of nodes. The cost is the
    distance between each node with sqrt(dx*dx+dy*dy).

    In this system we first build a path of all the nodes in the graph.
    Then we randomly swap nodes in the path and if it produces a positive
    result (in which we reduce the total distance) we keep the change and
    if not we discard the change.

    This is in contrast to just randomly building a path and then testing it,
    instead we test as we change and instead of recalculating the entire length
    of the path we only recalculate the portion that we changed.

    You can move from any node to any other node but the goal is to find the
    shortest path that goes through all nodes.
'''
import array
import os
import struct
import random
import math
import time

from tgaimage import TGAImage

def solve(points):
    hd = None
    hp = None

    # seeds for the solver not the graph builder
    random.seed(time.time())

    # 49,074,747
    # 48,098,597
    # 47,192,588

    totaltime = 60 * 60 * 10

    path = []
    for x in range(0, len(points)):
        path.append(x)
    # get initial total path distance
    d = getpathdistance(points, path)

    fst = time.time()
    lmt = None
    iend = len(path) - 1
    while time.time() - fst < totaltime:
        # shuffle path a little
        a = random.randrange(0, iend)
        b = random.randrange(0, iend)
        # calculate distance added by [a] and [b]
        adis = backforwpointdis(points, path, a)
        bdis = backforwpointdis(points, path, b)
        # subtract from total distance
        dsub = adis + bdis
        # swap [a] and [b]
        tmp = path[a]
        path[a] = path[b]
        path[b] = tmp
        # calculate new distance added by [a] and [b]
        adis = backforwpointdis(points, path, a)
        bdis = backforwpointdis(points, path, b)
        dadd = adis + bdis
        if dsub > dadd:
            d = d - dsub
            d = d + dadd
            print('new; d:%s count:%s' % (numtocommastr(d).rjust(20), numtocommastr(len(points)).rjust(20)))
        else:
            # revert the change.. it made it worse
            tmp = path[a]
            path[a] = path[b]
            path[b] = tmp
            # check if very little change in period of time
                # yes, very little change, so its getting stuck or it
                # is already stuck in the local minima so we need to 
                # try to yank it out
    return hp

def backforwpointdis(points, path, index):
    cur = path[index]
    aback = 0.0
    aforw = 0.0
    if index > 0:
        iback = path[index - 1]
        aback = pointdistance(points[iback], points[cur])
    if index < len(points) - 1:
        iforw = path[index + 1]
        aforw = pointdistance(points[iforw], points[cur])
    return aback + aforw

def pointdistance(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.sqrt(dx*dx + dy*dy)

def numtocommastr(i):
    s = '%s' % int(i)
    groups = []
    
    x = len(s) % 3
    if x > 0:
        groups.append(s[0:x])
    for x in range(x, len(s), 3):
        groups.append(s[x:x+3])

    return ','.join(groups)

####################################
############## SETUP ###############
####################################

def getrandomfloat(m):
    return random.random() * m

def getrandompoint(m):
    return (getrandomfloat(m), getrandomfloat(m))

def getrandompoints(c, m, rcpoint, points, *args):
    if points is None:
        points = []

    if len(args) > 1:
        for x in range(0, c):
            cpoint = getrandompoint(m)
            cpoint = (cpoint[0] + rcpoint[0], cpoint[1] + rcpoint[1])
            getrandompoints(args[0], args[1], cpoint, points, *args[2:])
        return points

    for x in range(0, c):
        point = getrandompoint(random.random() * m)
        points.append((point[0] + rcpoint[0], point[1] + rcpoint[1]))
    return points

def getpathdistance(points, path):
    td = 0.0
    lpoint = None
    for pindex in path:
        point = points[pindex]
        if lpoint is None:
            lpoint = point
            continue

        dx = lpoint[0] - point[0]
        dy = lpoint[1] - point[1]
        d = math.sqrt(dx*dx + dy*dy)
        td = td + d
        lpoint = point
    return td

def main():
    random.seed(38272932)
    points = getrandompoints(
        30, 1000, (0.0, 0.0), None,
        30, 600,
        30, 200,
        30, 50
    )
    # mix them up for a specified amount of time
    imax = len(points) - 1
    st = time.time()
    random.seed(time.time())
    print('rendering output image of nodes..')
    tga = TGAImage(1000, 1000)
    tga.drawpoints(points)
    tga.save('test.tga')
    print('mixing initial node list..')
    random.shuffle(points)
    #while time.time() - st < 10:
    #    a = random.randint(0, imax)
    #    b = random.randint(0, imax)
    #    tmp = points[a]
    #    points[a] = points[b]
    #    points[b] = tmp
    print('starting solver..')
    st = time.time()
    path = solve(points)
    tt = time.time() - st
    if len(path) < len(points):
        raise Exception('All points must be included in the path.')

    td = getpathdistance(points, path)

    print('total-distance:   %.2f' % td)
    print('time-taken:       %.2f' % tt)

main()