#
# This is testing framework for running algorithmic solutions for the Multiple Traveling Salesmen Problem.
#
# created by Jared McKlemurry for Dakota State University, CSC 705, Fall 2024
#

import argparse
import math
import matplotlib.pyplot as plt
import os
import time
import traceback
import tsplib95
import warnings

from aco_mtsp import runACOImpl
from ga_mtsp import runGAImpl
from slm_mtsp import runSLMImpl

warnings.filterwarnings("ignore")

def output(message, outputfile=None):
    if outputfile is not None:
        # write to file
        try:
            with open(outputfile, "a") as f:
                f.write(message)
                f.close()
        except:
            print(f"Error: unable to print to output file '{outputfile}'")
    else:
        # write to console
        print(message.replace(",", " "))

if __name__ == "__main__":
    # define args and parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--inputfile", help="Single dataset input file")
    parser.add_argument("-l", "--inputlist", help="List file of multiple datasets")
    parser.add_argument("-a", "--algorithms", help="List string of algorithms to test from: slm, ga, aco")
    parser.add_argument("-n", "--nsalesmen", help="List string of number of salesmen to test")
    parser.add_argument("-p", "--plot", help="Show individual final plot route", action="store_true")
    parser.add_argument("-o", "--outputfile", help="Test data CSV output file")
    args = parser.parse_args()
    
    # add TSP files to read
    tspFiles = []
    if args.inputfile is not None:
        tspFiles.append(args.inputfile)
    if args.inputlist is not None:
        try:
            with open(args.inputlist, "r") as f:
                for t in f.readlines():
                    tspFiles.append(t.strip())
                f.close()
        except:
            print(f"Error: unable to read input list '{args.inputlist}'")
    
    # add algorthims to test
    algorithms = ["slm", "ga", "aco"]
    if args.algorithms is not None:
        algorithms = args.algorithms.split(",")
    
    # add numbers of salesmen to test
    numsSalesmen = []
    if args.nsalesmen is not None:
        numsSalesmen = [int(x) for x in args.nsalesmen.split(",")]
    
    # early exit, print usage
    if len(tspFiles) == 0 or len(numsSalesmen) == 0:
        parser.print_usage()
        exit()
    
    #results = ""
    
    # print column headers
    out = args.outputfile
    headers = ["dataset"] + [f"{a}-{n}" for a in algorithms for n in numsSalesmen]
    ns = len(numsSalesmen)
    if ns > 1:
        avgs = [a + "-avg" for a in algorithms]
        for i in range(len(algorithms)):
            headers.insert((i + 1) * ns + i + 1, avgs[i])
    output(",".join(headers), out)
    
    # main loop
    # iterate through TSP files
    for t in tspFiles:
        #t = repr(t)
        
        try:
            tspData = tsplib95.load(t)
            tspName = os.path.basename(t).split(".")[0]
        except:
            print(f"Error: unable to load TSP file '{t}'")
            continue
        #results += f"\n{tspName}"
        output(f"\n{tspName}", out)
        
        # select depot
        # find centroid of nodes
        nodes = list(tspData.node_coords.values())
        center = [0.0, 0.0]
        for n in nodes:
            center[0] += n[0]
            center[1] += n[1]
        center[0] /= len(nodes)
        center[1] /= len(nodes)
        dist = float("inf")
        depot = -1
        
        # select closest node to centroid
        for i, n in enumerate(nodes):
            newDist = math.sqrt(((center[0] - n[0]) ** 2) + ((center[1] - n[1]) ** 2))
            if newDist < dist:
                dist = newDist
                depot = i
        
        # iterate through algorithms
        for a in algorithms:
            func = None
            dataIn = nodes
            match a:
                case "slm":
                    func = runSLMImpl
                case "ga":
                    func = runGAImpl
                case "aco":
                    func = runACOImpl
                    dataIn = tspData
            
            # iterate through n salesmen
            avgCost, avgTime = 0.0, 0.0
            for n in numsSalesmen:
                print(f"Running {tspName} {a} {n} ...")
                
                # time and execute solution
                timeStart = time.perf_counter()
                try:
                    result = func(dataIn, depot, n)
                except Exception as e:
                    print(f"Error: problem executing solution; {tspName} {a} {n}")
                    print(traceback.print_exc())
                    continue
                timeDelta = time.perf_counter() - timeStart
                
                # record solution results
                # expecting result in format: {"routes": [[0, 1, 2, 0], [0, 3, 4, 0], ...], "cost": 10.0}
                avgCost += result["cost"]
                avgTime += timeDelta
                #results += f",({'{0:.1f}'.format(result["cost"])} {'{0:.3f}'.format(timeDelta)}s)"
                output(f",({'{0:.1f}'.format(result["cost"])} {'{0:.3f}'.format(timeDelta)}s)", out)
                
                if args.plot and result is not None:
                    #fig, ax = plt.subplots()
                    for r in result["routes"]:
                        points = [nodes[n] for n in r]
                        plt.plot(*list(zip(*[(p[0], p[1]) for p in points])))
                    plt.show()
            
            # record average solution results across different n salesmen
            if len(numsSalesmen) > 1:
                avgCost /= len(numsSalesmen)
                avgTime /= len(numsSalesmen)
                #results += f",({'{0:.1f}'.format(avgCost)} {'{0:.3f}'.format(avgTime)}s)"
                output(f",({'{0:.1f}'.format(avgCost)} {'{0:.3f}'.format(avgTime)}s)", out)
    
    #output(results, out)
    print("Done!")