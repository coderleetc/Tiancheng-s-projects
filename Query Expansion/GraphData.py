'''
Created on Dec 5, 2015

GraphData.py contains functions of print all kinds of data of one graph
'''

import igraph  
from igraph import *
import matplotlib.pyplot as plt
from math import *
import numpy as np
from itertools import groupby
from collections import Counter


#Print diameter and the two nodes finding at first time of one graph
def PrintDiameter(graph, veList):
    temp = graph.farthest_points()
    vList = []
    for i in range(0, len(temp)-1):
        vList.append(veList[temp[i]])
    print "#Diameter: "
    print graph.diameter()
    print "#The two nodes finding at first time: "       
    print vList

#Print the average degree    
def PrintAverageDegree(graph):
    deList = graph.degree()
    
    print "The average degee: "  
    print float(sum(deList))/len(deList)
    
#Print the average shortest path
def PrintAverageShortestPath(graph, veList):
    length = len(veList)
    sumOfPath = 0
    iCount = 0
    for i in range(0, length):
        for j in range(0, length):
            if veList[i] != veList[j]:
                sumOfPath += (graph.shortest_paths_dijkstra(veList[i], veList[j])[0][0])
                iCount += 1
    
    print "The average shortest path: "
    print float(sumOfPath)/iCount
    
#Print detail data of power law fitted
def PrintPowerLawFitted(self, graph):
    deList = graph.degree()
    results = power_law_fit(deList)
        
    print "PowerLawFitted: "
    print results
    
