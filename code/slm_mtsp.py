#
# This algorithm, "SLM", is my proposed solution for the Multiple Traveling Salesmen Problem. First, clusters are created
# based on their relative direction from the depot. Then, simple paths are created within each cluster. Finally, routes
# are refined to find a near-optimal solution.
#
# created by Jared McKlemurry for Dakota State University, CSC 705, Fall 2024
#

import math

depot = None
d = (0, 0)

class City:
    def __init__(self, x, y, id):
        # using x and y for euclidean coordinates from dataset
        self.x, self.y = x, y
        dx, dy = (d[0] - x), (d[1] - y)
        
        # using r and theta for polar coordinates relative to depot
        self.r = math.sqrt(dx ** 2 + dy ** 2)
        self.theta = math.atan2(dy, dx) + math.pi
        
        # set ID for route tracking
        self.id = id
        
        # variables set during execution
        self.localTheta = None
        self.onR = False
    
    def __str__(self):
        return f"City({self.id}: {self.x}, {self.y})"

def distance(c1, c2):
    return math.sqrt((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2)

def solve(cities, nSalesmen):
    # sort cities by heading from depot
    cities.sort(key=(lambda c: c.theta))

    # calculate difference in angle between adjacent city headings
    angleDiffs = []
    for i in range(len(cities) - 1):
        angleDiffs.append([cities[i + 1].theta - cities[i].theta, cities[i], cities[i + 1]])
    angleDiffs.append([cities[0].theta + (math.pi * 2) - cities[-1].theta, cities[-1], cities[0]])

    # find widest angle gaps between cities
    gaps = (sorted(angleDiffs, key=(lambda a: a[0]), reverse=True)[:nSalesmen])
    # order gaps by heading
    gaps.sort(key=(lambda g: g[1].theta))
    
    # assign cities to clusters
    clusters = []
    for i in range(len(gaps)):
        # check for circle boundary
        if gaps[i - 1][2].theta > gaps[i][1].theta:
            clusters.append([c for c in cities if c.theta >= gaps[i - 1][2].theta or c.theta <= gaps[i][1].theta])
        else:
            clusters.append([c for c in cities if c.theta >= gaps[i - 1][2].theta and c.theta <= gaps[i][1].theta])
    
    routes = []
    totalCost = 0
    
    # create Hamiltonian cycles for each cluster
    cycles = []
    for k in clusters:
        cycL = [depot] # left (prograde) half of cycle moving outward
        cycR = [depot] # right (retrograde) half of cycle moving inward
        edgeL = k[-1].theta # left edge of sector
        edgeR = k[0].theta #right edge of sector
        sectorAngle = (edgeL - edgeR + (math.pi * 2 if edgeL < edgeR else 0))
        cost = 0
        
        # sort cities in cluster k by distance from depot
        kDist = sorted(k, key=(lambda c: c.r))

        # add to left or right side
        for c in kDist:
            c.localTheta = c.theta - edgeR
            c.localTheta += math.pi * 2 if c.localTheta < 0 else 0
            
            # determine half sector c belongs to; check for circle boundary
            if c.localTheta > sectorAngle / 2:
                cycL.append(c)
            else:
                cycR.insert(0, c)
                c.onR = True
        
        # sort cities by proximity to centerline of sector
        kCenter = sorted(k, key=(lambda c: abs((sectorAngle / 2) - c.localTheta)))
        
        # crossover mutation
        for c in kCenter:
            cycX = [cycR, cycL] if c.onR else [cycL, cycR]
            
            index = cycX[0].index(c)
            if index < len(cycX[0]) - 1 and ((c.onR and c.r < cycX[1][-1].r) or (c.r < cycX[1][0].r)):
                polarity = -1 if c.onR else 1
                nextSS = cycX[0][index + polarity] # next city on same side
                prevSS = cycX[0][index - polarity] # previous city on same side
                
                tempSwap = sorted([c] + cycX[1], key=(lambda c: c.r))
                tempIndex = tempSwap.index(c)
                
                nextOS = cycX[0][index - polarity] # next city on other side
                prevOS = cycX[0][index + polarity] # previous city on other side
                
                # calculate potential costs
                curCost = distance(prevSS, c) + distance(c, nextSS) + distance(prevOS, nextOS)
                potCost = distance(prevSS, nextSS) + distance(prevOS, c) + distance(c, nextOS)
                if potCost < curCost:
                    # swap c to other side
                    cycX[1].insert(tempIndex, c)
                    cycX[0].pop(index)
                    c.onR = not c.onR
        
        cyc = cycL + cycR
        
        # reorder mutation
        if len(cyc) > 4:
            repeat = True
            while repeat:
                repeat = False
                
                for i in range(1, len(cyc) - 2):
                    # calculate potential costs
                    curCost = distance(cyc[i - 1], cyc[i]) + distance(cyc[i + 1], cyc[i + 2])
                    potCost = distance(cyc[i - 1], cyc[i + 1]) + distance(cyc[i], cyc[i + 2])
                    if potCost < curCost:
                        # swap order of i and i + 1
                        cyc[i], cyc[i + 1] = cyc[i + 1], cyc[i]
                        repeat = True
        
        # calculate cost
        for i in range(len(cyc) - 1):
            totalCost += distance(cyc[i], cyc[i + 1])
        
        routes.append([c.id for c in cyc])
        
    return {"routes": routes, "cost": totalCost}

def runSLMImpl(nodes, depotIndex, nSalesmen):
    # initialize data
    global d
    d = (nodes[depotIndex][0], nodes[depotIndex][1]) 
    global depot
    depot = City(d[0], d[1], depotIndex)
    cities = []
    for i, n in enumerate(nodes):
        cities.append(City(n[0], n[1], i))
    cities.pop(depotIndex)
    
    return solve(cities, nSalesmen)