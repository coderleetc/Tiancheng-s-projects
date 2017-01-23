'''
Created on Dec 5, 2015

GraphDisplay.py contains functions of drawing different kinds of graph
'''

import igraph  
from igraph import *
import matplotlib.pyplot as plt
from math import *
import numpy as np

#Drawing general graph(edges and vertices)
def DrawGraph(graph, veList):
    deList = graph.degree()
    temp = deList  
        
    p = mean(deList)
    
    for i in range(0, len(temp)):
        if temp[i] >= p:
            graph.vs[i]["color"] = "red"
        else:
            graph.vs[i]["color"] = "pink"
    plot(graph, vertex_size=1, bbox=(0,0,1000,1000))
 
#Drawing graph with weighted value(edges, vertices, weighted value)   
def DrawGraphWeighted(graph, edList, wList, veList):
        deList = graph.degree()
        
        lenX = len(edList)
        for i in range(0, lenX):
            if wList[i] == 2:
                graph.es[i]["color"] = "#FFCCCC"
            if wList[i] == 3:
                graph.es[i]["color"] = "#FF6666"
            if wList[i] == 4:
                graph.es[i]["color"] = "#FF3333"    
            if wList[i] == 5:
                graph.es[i]["color"] = "#FF0000"
            if wList[i] == 6:
                graph.es[i]["color"] = "#CC0000"  
            if wList[i] == 7:
                graph.es[i]["color"] = "#990000"
            if wList[i] == 8:
                graph.es[i]["color"] = "#660000"
            if wList[i] >= 9:
                graph.es[i]["color"] = "#000000"
        temp = deList  
        p = mean(deList)
        for i in range(0, len(temp)):
            if temp[i] >= p:
                graph.vs[i]["color"] = "red"
            else:
                graph.vs[i]["color"] = "pink"
        
        plot(graph ,vertex_size=1,bbox=(0,0,1000, 1000))
        
#Drawing power law distribution without limiting x&y coordinate
def DrawPLDistribution(graph):
    deList = graph.degree()
    xList = []
    yList = []
        
    for item in deList:
        if item not in xList:
            xList.append(item)
        
    for itemX in xList:
        iCount = 0
        for itemY in deList:
            if itemX == itemY:
                iCount += 1
        yList.append(iCount)  
            
    plt.plot(xList, yList, 'ro')
        
    if max(xList) > 10:
        plt.axis([-2, max(xList)+2, -2, max(yList)+2])
    else:
        plt.axis([-0.2, max(xList)+0.2, -2, max(yList) + 0.2])
        
    plt.ylabel('number')
    plt.xlabel('degree')
    plt.show()
    
#Draw page rank distribution contains no weighted value and adding weighted value
def DrawPageRankDistrubution(graph, wList):
    deList = graph.degree()
    pgList = graph.pagerank()
    pgListW = graph.pagerank(weights=wList)
        
    intrValue = max(pgList)
        
    fig = plt.figure(figsize=(10, 10))
    ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax1 = plt.plot(deList, pgList, 'ro', deList, pgListW, 'g^')
    plt.ylabel('pagerank')
    plt.xlabel('degree')
    if intrValue > 0.1:
        ax2 = fig.add_axes([0.155,0.57, 0.28, 0.28])
        ax2 = plt.axis([0, 100, 0, 0.03])
        ax2 = plt.plot(deList, pgList, 'ro', deList, pgListW, 'g^')
        
    plt.show()
    
#Draw page rank distribution just contains no weighted value
def DrawPageRank(graph):
    deList = graph.degree()
    pgList = graph.pagerank()
        
    intrValue = max(pgList)
        
    fig = plt.figure(figsize=(10, 10))
    ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax1 = plt.plot(deList, pgList, 'ro')
    plt.ylabel('pagerank')
    plt.xlabel('degree')
    if intrValue > 0.1:
        ax2 = fig.add_axes([0.155,0.57, 0.28, 0.28])
        ax2 = plt.axis([0, 100, 0, 0.03])
        ax2 = plt.plot(deList, pgList, 'ro')
        
    plt.show()

#Display all kinds of the graphs    
def DisplayGraph(graph, edList, wList, veList):
    DrawGraph(graph, veList)
    DrawGraphWeighted(graph, edList, wList, veList)
    DrawPageRank(graph)
    DrawPageRankDistrubution(graph, wList)
    DrawPLDistribution(graph)