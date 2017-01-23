'''
Created on Dec 5, 2015

GraphGenerator: 
    Connect to Database
    Generate Graph and other corresponding data
'''

from __future__ import division
import psycopg2
import igraph  
from igraph import *
import matplotlib.pyplot as plt
from math import *
import numpy as np
from itertools import groupby
from collections import Counter

from Unit import *
from GraphDisplay import *
from GraphData import *

class GraphGenerator:
    
    #Initialization function
    def __init__(self, tableName, className):
        
        #Connecting database    
        conn_string = "host='localhost' dbname='restoretestdb' user='ponza' password='123456'"
        conn = psycopg2.connect(conn_string)
        cusor = conn.cursor()
        cusor.execute("select * from %s;" % tableName)
        self.record = cusor.fetchall()
        
        #List of feature in record
        self.tagList = []           #tagList
        self.qUserList = []         #questionuserid
        self.aUserList = []         #acceptuserid
        self.aUserGeneralList = []  #answeruserid
        
        self.tagVeList = []         #tag vertex list
        self.tagEdList = []         #tag based edge list
        self.tagEdListX = []        #tag share user edge list
        
        
        self.userVeList = []        #user vertex list
        self.userEdList = []        #user based edge list
        self.userEdListX = []       #user share tag edge list
        
        self.tagEdListW = []        #tag based edge list with weighted
        self.tagEdListXW = []       #tag share user edge list weighted
        self.userEdListW = []       #user based edge list
        self.userEdListXW = []      #user share tag edge list
        
        #Getting list of feature in record from specific table in database
        self.GetData(className)
    
    #Get data from the record of database and arrange them
    def GetData(self, className):    
        #Getting taglist, qUserList, aUserList, aUserGeneralList
        for itemR in self.record:
            temp = []
            for word in list(itemR)[2].split(','):   
                if word not in self.tagVeList:
                    self.tagVeList.append(word)
                temp.append(word)
                
            self.tagList.append(temp)    
        
            q = str(itemR[3])
            a = str(itemR[5])
            
            #Get question user list
            self.qUserList.append(q)         
                        
            #Get answer user list
            self.aUserList.append(a)
    
            #Get user vertex List
            if q not in self.userVeList:
                self.userVeList.append(q)    
        
            tempp = []
            for word in itemR[6].split(','):
                if word not in self.userVeList:
                    self.userVeList.append(word)
                tempp.append(word)
            self.aUserGeneralList.append(tempp)
           
        #Getting based tag edge list and edge weighted list
        self.GetTagEdge()
        #Getting advanced edge list and edge weighted list
        self.GetTagEdgeX()
        #Getting based user edge list and edge weighted list
        self.GetUserEdge()
        #Getting advanced user edge list and edge weighted list
        self.GetUserEdgeX(className)
        
    #Getting based tag edge list and edge weighted list    
    def GetTagEdge(self):
        edListW = []
        for item in self.tagList:
            length = len(item)
            for i in range(0, length):
                for j in range(0, length):
                    if item[i] != item[j]:
                        #Getting the edge list without remove dual item for calculating weighted
                        edListW.append((item[i], item[j]))
                        edListW.append((item[j], item[i]))
        
        tempList = edListW
        self.tagEdList = list(set(tempList))
        edList = self.tagEdList
        self.tagEdListW = GetWeighted(edList, edListW)
        
    #Getting advanced edge list and edge weighted list
    def GetTagEdgeX(self):
        edListW = []
        
        i = 0
        lenT = len(self.tagList)
        while i < lenT:
            for j in range(i+1, lenT):
                tempX = []
                if self.qUserList[i] == self.qUserList[j] or (set(self.qUserList[i])&set(self.aUserGeneralList[j])) or (set(self.qUserList[j])&set(self.aUserGeneralList[i])) or (set(self.aUserGeneralList[i])&set(self.aUserGeneralList[j])):
                    tempX = list(set(self.tagList[i])|set(self.tagList[j]))
                    lenX = len(tempX)
                    
                    for x in range(0, lenX):
                        for y in range(x+1, lenX):
                            edListW.append((tempX[x], tempX[y]))
                            edListW.append((tempX[y], tempX[x]))
            
            if set(self.qUserList[i])&set(self.aUserGeneralList[j]):   
                tempY = self.tagList[i]
                lenY = len(tempY)
                for m in range(0, lenY):
                    for n in range(m+1, lenY):
                        edListW.append((tempY[m], tempY[n]))
                        edListW.append((tempY[n], tempY[m]))
                        
            i = i + 1
        
        tempList = edListW
        self.tagEdListX = list(set(tempList))
        edList = self.tagEdListX
        self.tagEdListXW = GetWeighted(edList, edListW)
    
    #Getting based user edge list and edge weighted list
    def GetUserEdge(self):
        edListW = []
        
        length = len(self.tagList)
        
        for i in range(0, length):
            SetUserEdge(self.qUserList[i], self.aUserGeneralList[i], edListW)
                  
        tempList = edListW
        self.userEdList = list(set(tempList))
        edList = self.userEdList 
        self.userEdListW = GetWeighted(edList, edListW)
    
    #Getting advanced user edge list and edge weighted list
    def GetUserEdgeX(self, className):
        edListW = []
        length = len(self.tagList)
        
        i= 0
        while i<length:
            for j in range(i+1, length): 
                temp = [self.qUserList[i], self.qUserList[j]]
                if IsTagSame(self.tagList[i], self.tagList[j], className):                  
                    unionList1 = list( set(temp) | set(self.aUserGeneralList[i]) | set(self.aUserGeneralList[j]) )
                    lenU = len(unionList1)
                    for m in range(0, lenU):
                        for n in range(m+1, lenU):
                            edListW.append((unionList1[m], unionList1[n]))
                            edListW.append((unionList1[n], unionList1[m]))
            
            i = i + 1
        tempList = edListW
        self.userEdListX = list(set(tempList))
   
        edList = self.userEdListX
        self.userEdListXW = GetWeighted(edList, edListW)  

    #Generating Graph
    def GetGraph(self, veList, edList, wList):
        g = Graph()
        g.add_vertices(veList)
        g.add_edges(edList)
        
        DisplayGraph(g, edList, wList, veList)
    
    #Output result
    def Output(self):
        print "/// Based tag /// "
        self.GetGraph(self.tagVeList, self.tagEdList, self.tagEdListW)
        print '\n'
        
        print "/// Advanced tag /// "
        self.GetGraph(self.tagVeList, self.tagEdListX, self.tagEdListXW)
        print '\n'
        
        print "/// Based user /// "
        self.GetGraph(self.userVeList, self.userEdList, self.userEdListW) 
        print '\n'
        
        print "/// Advanced user /// "
        self.GetGraph(self.userVeList, self.userEdListX, self.userEdListXW)