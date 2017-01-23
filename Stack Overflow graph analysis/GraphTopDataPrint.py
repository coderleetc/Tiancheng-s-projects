'''
Created on Dec 5, 2015

GraphTopDataPrint.py is used for print the specific data 
    of top ten data mainly including the PageRank value, 
    degree, and PageRank　value with weights 
    to help us analyze the result efficiently;
It's not contained in the main function during executing;
It should be executed with the Test.py when output the result.
'''

import psycopg2
import igraph  
from igraph import *
from math import *
from itertools import groupby
from collections import Counter


class GraphAnalysis:
    
    def __init__(self, tableName, className):
        
        #Connecting database    
        conn_string = "host='localhost' dbname='restoretestdb' user='ponza' password='123456'"
        conn = psycopg2.connect(conn_string)
        cusor = conn.cursor()
        cusor.execute("select * from %s;" % tableName)
        self.record = cusor.fetchall()
        
        #List of feature in record
        self.tagList = []       #tagList
        self.qUserList = []     #questionuserid
        self.aUserList = []     #acceptuserid
        self.aUserGeneralList = []  #answeruserid
        
        self.tagVeList = []     #tag vertex list
        self.tagEdList = []     #tag based edge list
        self.tagEdListX = []    #tag share user edge list
        
        
        self.userVeList = []    #user vertex list
        self.userEdList = []    #user based edge list
        self.userEdListX = []   #user share tag edge list
        
        self.tagEdListW = []    #tag based edge list with weighted
        self.tagEdListXW = []   #tag share user edge list weighted
        self.userEdListW = []   #user based edge list
        self.userEdListXW = []  #user share tag edge list
        
        #Getting list of feature in record from specific table in database
        self.GetData(className)
        print ".....Statistic begin....."
    
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
           
        #Getting based tag edge list
        
        self.GetTagEdge()
        
        self.GetTagEdgeX()
    
        self.GetUserEdge()
        
        self.GetUserEdgeX(className)
        #print len(self.userEdListX)
    #Getting based tag edge list and edge weighted list    
    def GetTagEdge(self):
        edList = []
        edListW = []
        for item in self.tagList:
            length = len(item)
            for i in range(0, length):
                for j in range(0, length):
                    if item[i] != item[j]:
                        '''
                        if (item[i], item[j]) not in edList:
                            edList.append((item[i], item[j]))        
                            edList.append((item[j], item[i]))
                        '''
                        #Getting the edge list without remove dual item for calculating weighted
                        edListW.append((item[i], item[j]))
                        edListW.append((item[j], item[i]))
        
        tempList = edListW
        self.tagEdList = list(set(tempList))
        edList = self.tagEdList
        self.tagEdListW = self.GetWeighted(edList, edListW)
        
    #Getting shared user edge list and edge weighted list
    def GetTagEdgeX(self):
        edList = []
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
                            '''
                            if (tempX[x], tempX[y]) not in edList:
                                edList.append((tempX[x], tempX[y]))
                                edList.append((tempX[y], tempX[x]))
                            '''
                            edListW.append((tempX[x], tempX[y]))
                            edListW.append((tempX[y], tempX[x]))
            
            if set(self.qUserList[i])&set(self.aUserGeneralList[j]):   
                tempY = self.tagList[i]
                lenY = len(tempY)
                for m in range(0, lenY):
                    for n in range(m+1, lenY):
                        '''
                        if (tempY[m], tempY[n]) not in edList:
                            edList.append((tempY[m], tempY[n]))
                            edList.append((tempY[n], tempY[m]))
                        '''
                        edListW.append((tempY[m], tempY[n]))
                        edListW.append((tempY[n], tempY[m]))
                        
            i = i + 1
        
        tempList = edListW
        self.tagEdListX = list(set(tempList))
        edList = self.tagEdListX
        self.tagEdListXW = self.GetWeighted(edList, edListW)
    
    def GetUserEdge(self):
        edList = []
        edListW = []
        
        length = len(self.tagList)
        
        for i in range(0, length):
            self.SetUserEdge(self.qUserList[i], self.aUserGeneralList[i], edListW)
                  
        tempList = edListW
        self.userEdList = list(set(tempList))
        edList = self.userEdList 
        self.userEdListW = self.GetWeighted(edList, edListW)
        
    def GetUserEdgeX(self, className):
        edList = []
        edListW = []
        length = len(self.tagList)
        
        i= 0
        while i<length:
            for j in range(i+1, length): 
                temp = [self.qUserList[i], self.qUserList[j]]
                if self.IsTagSame(self.tagList[i], self.tagList[j], className):                  
                    #unionList1 = list( set(list(self.qUserList[i])) | set(self.aUserGeneralList[i]) | set(list(self.qUserList[j])) | set(self.aUserGeneralList[j]) )
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
        self.userEdListXW = self.GetWeighted(edList, edListW)  
   
    def SetUserEdge(self, strValue, xList, eList):
        
        for item in xList:
            if strValue != item:
                eList.append((item, strValue))
    
    def SetUserEdgeX(self, strValue, vList, wList):
        
        for item in vList:
            if item != strValue:
                wList.append((strValue, item)) 
                wList.append((item, strValue)) 
    
    def SetEdge(self, vertexX, vertexY, wList):
        
        if vertexX != vertexY:
            wList.append((vertexX, vertexY)) 
            wList.append((vertexY, vertexX))  
     
    def SetEdgeX(self, xList, yList, wList):
        
        for itemX in xList:
            for itemY in yList:
                if itemX != itemY:
                    wList.append((itemX, itemY))
                    wList.append((itemY, itemX))
              
    def GetUniqueList(self, xList):
        temp = []
        v = 0
        for item in xList:
            if item not in temp:
                temp.append(item)
            
   
        return temp
    
    def IsUserSame(self, strX, strY, xList, yList):
        
        if strX == strY:
            return True
        else:
            for item in yList:
                if strX == item:
                    return True
        
            for item in xList:
                if strY == item:
                    return True
        
            for itemX in xList:
                for itemY in yList:
                    if itemX == itemY:
                        return True
            return False
    
    def IsUserSameX(self, strValue, xList):
        
        for item in xList:
            if strValue == item:
                return True
        return False      
    
    def IsItemSame(self, xList, yList):
        
        for itemX in xList:
            for itemY in yList:
                if itemX == itemY:
                    return True
        return False   
    
    def IsTagSame(self, xList, yList, className):     
        
        first = []
        second = []
        for itemX in xList:
            first.append(itemX)
        for itemY in yList:
            second.append(itemY)
        first.remove(className)
        second.remove(className)
        if len(first)==0 or len(second)==0:
            return False
        else:
            if set(first)&set(second):
                return True
            else:
                return False
    
    def GetCombineList(self, xList, yList):
        first_list = []
        second_list = []
        
        for itemX in xList:
            first_list.append(itemX)
            
        for itemY in yList:
            second_list.append(itemY)

        in_first = set(first_list)
        in_second = set(second_list)

        in_second_but_not_in_first = in_second - in_first

        result = first_list + list(in_second_but_not_in_first)
        
        return result

    def GetWeighted(self, xList, yList):    
        listEdges = yList
        dictMapEdgeWeight = {}
        i = 0
        for itemKey in listEdges:
            if dictMapEdgeWeight.has_key(itemKey):
                dictMapEdgeWeight[itemKey] += 1 
            else:      
                dictMapEdgeWeight[itemKey] = 1
            i = i + 1
        dictlist = []
        
        for key, value in dictMapEdgeWeight.iteritems():
            #temp = [key,value]
            dictlist.append(value)
        
        return dictlist      
    
    def GetIndexOfTopData(self, xList):
        temp = []
        for item in xList:
            temp.append(item)
        p = 0
        
        indexOfTop= []
        while p < 10:
            m = max(temp)
            for i in range(0, len(temp)):      
                if temp[i] == m:
                    indexOfTop.append(temp.index(temp[i]))
                    p = p + 1
                    temp[i] = 0
        return indexOfTop
    
    def GetIndexOfBottomData(self, xList):
        temp = []
        for item in xList:
            temp.append(item)
        p = 0
        
        indexOfBottom= []
        while p < 10:
            m = min(temp)
            for i in range(0, len(temp)):      
                if temp[i] == m:
                    indexOfBottom.append(temp.index(temp[i]))
                    p = p + 1
                    temp[i] = 10000
        return indexOfBottom 
    
    #Getting the degree of graph
    def GetDegree(self, graph):
        deList = graph.degree()

        return deList
    
    #Getting the Page Rank value of graph for each vertex
    def GetPageRank(self, graph):
        prList = graph.pagerank()
        
        return prList
    
    #Getting the Page Rank value of graph with weighted value for each vertex
    def GetPageRankW(self, graph, wList):
        prList = graph.pagerank(weights = wList)
        
        return prList
    
    def GetTagGraph(self, veList, edList, wList):
        g = Graph()
        g.add_vertices(veList)
        g.add_edges(edList)
        
        print "/// Top 10 Degree - PageRank - PageRank(Weighted): ///"
        self.PrintDegreeInfor(g, veList, wList)
        
        print "/// Top 10 PageRank - PageRank(Weighted) - Degree: ///" 
        self.PrintPageRankInfor(g, veList, wList)
        
        print "/// Top 10 PageRank(Weighted) - PageRank - Degree: ///"
        self.PrintPageRankWeightedInfor(g, veList, wList)
        
        print "/// Bottom 10 PageRank - PageRank(Weighted) - Degree: ///"
        self.PrintPageRankBottomInfor(g, veList, wList)
        
        print "/// Bottom 10 PageRank(Weighted) - PageRank - Degree: ///"
        self.PrintPageRankWeightedBottomInfor(g, veList, wList)
    
    def GetUserGraph(self, veList, edList, wList):
        g = Graph()
        g.add_vertices(veList)
        g.add_edges(edList)
        
        print "/// Top 10 Degree - PageRank - PageRank(Weighted): ///"
        self.PrintDegreeInfor(g, veList, wList)
        
        print "/// Top 10 PageRank - PageRank(Weighted) - Degree: ///" 
        self.PrintPageRankInfor(g, veList, wList)
        
        print "/// Top 10 PageRank(Weighted) - PageRank - Degree: ///"
        self.PrintPageRankWeightedInfor(g, veList, wList)
        
        print "/// Bottom 10 PageRank - PageRank(Weighted) - Degree: ///"
        self.PrintPageRankBottomInfor(g, veList, wList)
        
        print "/// Bottom 10 PageRank(Weighted) - PageRank - Degree: ///"
        self.PrintPageRankWeightedBottomInfor(g, veList, wList)
        
        print "/// Top Degree Accepted User: ///"
        self.GetAUserInfor(g, wList)
        print "/// Top Degree Question User: ///"
        self.GetQUserInfor(g, wList)
        
    def Output(self):
        
        "/// Based tag /// "
        self.GetTagGraph(self.tagVeList, self.tagEdList, self.tagEdListW)
        print '\n'
        
        print "/// Advanced tag /// "
        self.GetTagGraph(self.tagVeList, self.tagEdListX, self.tagEdListXW)
        print '\n'
        
        print "/// Based user /// "
        self.GetUserGraph(self.userVeList, self.userEdList, self.userEdListW) 
        print '\n'
        
        print "/// Advanced user /// "
        self.GetUserGraph(self.userVeList, self.userEdListX, self.userEdListXW)
        
    
    def PrintDegreeInfor(self, graph, veList, weList):
        deList = graph.degree()
        prList = graph.pagerank()
        pwList = graph.pagerank(weights = weList)
        
        indexOfTopData =self.GetIndexOfTopData(graph.degree())
        
        vList = []
        dList = []
        pList = []
        wList = []
        
        for item in indexOfTopData:
            vList.append(veList[item])
            dList.append(deList[item])
            pList.append(prList[item])
            wList.append(pwList[item]) 
        
        print "### Vertices: ###"
        print vList
        print "### Degree: ###"
        print dList
        print "### PageRank: ###"
        print pList
        print "### PageRank(weighted): ###"
        print wList
    
    def PrintPageRankInfor(self, graph, veList, weList):
        prList = graph.pagerank()
        indexOfTopData = self.GetIndexOfTopData(prList)
        deList = graph.degree()
        pwList = graph.pagerank(weights = weList)
        vList = []
        pList = []
        wList = []
        dList = []
        
        for item in indexOfTopData:
            vList.append(veList[item])
            pList.append(prList[item])
            wList.append(pwList[item])
            dList.append(deList[item]) 
        
        print "### Vertices: ###"
        print vList
        print "### PageRank: ###"
        print pList
        print "### PageRank(weighted): ###"
        print wList
        print "### Degree: ###"
        print dList
    
    def PrintPageRankWeightedInfor(self, graph, veList, weList):
        prList = graph.pagerank()
        temp = graph.pagerank(weights = weList)
        indexOfTopData = self.GetIndexOfTopData(temp)
        deList = graph.degree()
        
        vList = []
        wList = []
        pList = []
        dList = []
        
        for item in indexOfTopData:
            vList.append(veList[item])
            wList.append(temp[item])
            pList.append(prList[item])
            dList.append(deList[item]) 
        
        print "### Vertices: ###"
        print vList
        print "### PageRank(weighted): ###"
        print wList
        print "### PageRank: ###"
        print pList
        print "### Degree: ###"
        print dList
        
    def PrintPageRankBottomInfor(self, graph, veList, weList):
        prList = graph.pagerank()
        indexOfTopData = self.GetIndexOfBottomData(prList)
        deList = graph.degree()
        pwList = graph.pagerank(weights = weList)
        
        vList = []
        pList = []
        wList = []
        dList = []
        
        for item in indexOfTopData:
            vList.append(veList[item])
            pList.append(prList[item]) 
            wList.append(pwList[item])
            dList.append(deList[item])
            
        print "### Vertices: ###"
        print vList
        print "### PageRank: ###"
        print pList
        print "### PageRank(weighted): ###"
        print wList
        print "### Degree: ###"
        print dList
    
    def PrintPageRankWeightedBottomInfor(self, graph, veList, weList):
        temp = graph.pagerank(weights = weList)
        indexOfTopData = self.GetIndexOfBottomData(temp)
        prList = graph.pagerank()
        deList = graph.degree()
        
        vList = []
        wList = []
        pList = []
        dList = []
        
        for item in indexOfTopData:
            vList.append(veList[item])
            wList.append(temp[item]) 
            pList.append(prList[item])
            dList.append(deList[item])
            
        print "### Vertices: ###"
        print vList
        print "### PageRank(weighted): ###"
        print wList
        print "### PageRank: ###"
        print pList
        print "### Degree: ###"
        print dList
        
    def GetAUserInfor(self, graph, weList):
        deList = graph.degree()
        temp = []
        tempA = self.aUserList
        aUser = list(set(tempA))
        pListTemp = graph.pagerank()
        wListTemp = graph.pagerank(weights = weList)
        
        prList = []
        wList = []
        
        for i in range(0, len(aUser)):
            index = self.userVeList.index(aUser[i])
            temp.append(deList[index])
            prList.append(pListTemp[index])
            wList.append(wListTemp[index])
                
        topIndex = self.GetIndexOfTopData(temp)
        
        vList = []
        dList = []
        pList = []
        w = []
        
        for item in topIndex:
            vList.append(aUser[item])
            dList.append(temp[item]) 
            pList.append(prList[item])
            w.append(wList[item])
            
        print "### Vertices: ###"
        print vList
        print "### Degree: ###"
        print dList
        print "### PageRank: ###"
        print pList
        print "### PageRank(weighted): ###"
        print w
        
    def GetQUserInfor(self, graph, weList):
        deList = graph.degree()
        temp = []
        
        tempA = self.qUserList
        qUser = list(set(tempA))
        
        pListTemp = graph.pagerank()
        wListTemp = graph.pagerank(weights = weList)
        
        prList = []
        wList = []
        
        for i in range(0, len(qUser)):
            index = self.userVeList.index(qUser[i])
            temp.append(deList[index])
            prList.append(pListTemp[index])
            wList.append(wListTemp[index])
            
        topIndex = self.GetIndexOfTopData(temp)
        
        vList = []
        dList = []
        pList = []
        w = []

        for item in topIndex:
            vList.append(qUser[item])
            dList.append(temp[item]) 
            pList.append(prList[item])
            w.append(wList[item])
            
        print "### Vertices: ###"
        print vList
        print "### Degree: ###"
        print dList
        print "### PageRank: ###"
        print pList
        print "### PageRank(weighted): ###"
        print w