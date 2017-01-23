import numpy as np
import scipy as sp
import os
import copy
import psycopg2

'''
This is the first step of this project
Strategy: 
1: Identify the tags: currently use the example tages and the example groups
   (1) 4 tags:   HTML, CSS, Lisp and Haskell
   (2) 2 Groups: Web Development(HTML, CSS), and Functional Programming(Lisp, Haskell) 
2: Load Data into Memory 
3: Save 300 questions for each of tag. For each question, we need to record their: 
   (1) Answers. For each answer: 
       a)Users  
   (2) All of other tags 
   (3) Users
NOTICE: 
a) posts include both question and answer (basaed on the value of post_type_id)
b) not all of question are valid: 
   1) Maybe there is no answer  
c) not all of answer are valid
   1) Maybe some answers are submitted by anonymous
'''

#1: Identify the tags 
listTag =  ['HTML', 'CSS', 'LISP', 'HASKELL'] 
listGroup = ["Web_Development", "Functional_Programming"] 

#2: class identification
class Answer: 
    id = -1
    userID = -1
    def __init__(self):
        {}
        
class Question:
    listTag = []
    listAnswerUser = []
    acceptAnswerID = -1
    acceptAnswerUserID = -1
    userID = -1
    def __init__(self):
        {}
        
class Category:
    tagName = ""
    groupName = ""
    def __init__(self, tagName, groupName):
        self.tagName = tagName
        self.groupName = groupName  
                    
def SetValueForTypeItem(curTypeQuestion, itemUserID, itemAcceptAnswerID, itemAcceptAnswerUserID, itemAnswerUserList, itemTags):
    #Set Tag list and answer ID and UserID                
    curQuestion = Question()
    curQuestion.userID = itemUserID                    
    curQuestion.acceptAnswerID = itemAcceptAnswerID
    curQuestion.acceptAnswerUserID = itemAcceptAnswerUserID
    curQuestion.listTag = itemTags      
    curQuestion.listAnswerUser = itemAnswerUserList                                                                                             
    curTypeQuestion.append(curQuestion)                                              
        
def LoadData(type11Question, type12Question, type21Question, type22Question): #(type11, type12, type21, type22):               
    conn = psycopg2.connect(database="testdb", user="ponza", password="lxwg", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    #Collect all of Answers and build the map with key: Question ID, Value User List. -->    
    cur.execute("SELECT parent_id, owner_user_id FROM posts where post_type_id = 2 and id <= 1800000 and owner_user_id is not null and parent_id is not null;") # body
    rows = cur.fetchall()        # all rows in table
    dictMapAnwerUser = {}
    for rowItem in rows:
        if rowItem == None: #skip the invalid items            
            continue;
        if dictMapAnwerUser.has_key(rowItem[0]):
            dictMapAnwerUser[rowItem[0]].append(str(rowItem[1]))
        else:
            dictMapAnwerUser[rowItem[0]] = []
            dictMapAnwerUser[rowItem[0]].append(str(rowItem[1]))                
    #<--- 
    cur.execute("SELECT id, tags,owner_user_id,accepted_answer_id FROM posts where post_type_id = 1 and id >= 0 and id <=1800000;") # body
    rows = cur.fetchall()        # all rows in table
    iCountType11 = 0
    iCountType12 = 0
    iCountType21 = 0
    iCountType22 = 0 
    bType11Full = False
    bType12Full = False
    bType21Full = False
    bType22Full = False
    
    for items in rows:
        if items == None: #skip the invalid items            
            continue;
        itemID = items[0]
        itemTags = items[1].upper()        
        itemUserID = items[2]
        itemAcceptAnswerID = items[3]
        itemAnswerUserList = []
        
        if itemAcceptAnswerID == None:
            continue
        itemAcceptAnswerUserID = None
        cur.execute("SELECT owner_user_id FROM posts where id = %s and post_type_id = %s and owner_user_id is not null" %(itemAcceptAnswerID, 2))
        tempRow = cur.fetchall() # the type of tempRow is list    
        if len(tempRow) > 0:         
            # Get the Accept answer user ID    
            itemAcceptAnswerUserID = tempRow[0][0]   
            if dictMapAnwerUser.has_key(itemID):
                itemAnswerUserList = dictMapAnwerUser[itemID]
                if str(itemAcceptAnswerUserID) not in itemAnswerUserList:
                    itemAnswerUserList.append(str(itemAcceptAnswerUserID))
            else:
                itemAnswerUserList.append(str(itemAcceptAnswerUserID))                            
        # all of the features should be set real value
        if itemTags != None and itemUserID != None and itemAcceptAnswerID != None and itemAcceptAnswerUserID != None and len(itemAnswerUserList) > 0:                                        
            itemTags = itemTags.replace('<', '')            
            itemTags = itemTags[0:-1]       
            itemTags = itemTags.split('>')   
            if len(itemTags) <= 1:
                continue;                                                
            # this item is for HTML --> type11
            if listTag[0] in itemTags: 
                if bType11Full == False:
                    SetValueForTypeItem(type11Question, itemUserID, itemAcceptAnswerID, itemAcceptAnswerUserID, itemAnswerUserList, itemTags)                                            
                    iCountType11 += 1                                                                    
                    if iCountType11 >= 300:
                        bType11Full = True                                                        
            # this item is for CSS --> type12     
            if listTag[1] in itemTags: 
                if bType12Full == False:
                    SetValueForTypeItem(type12Question, itemUserID, itemAcceptAnswerID, itemAcceptAnswerUserID, itemAnswerUserList, itemTags)                                              
                    iCountType12 += 1
                    if iCountType12 >= 300:
                        bType12Full = True                                           
            # this item is for lisp --> type21 
            if listTag[2] in itemTags: 
                if bType21Full == False:
                    SetValueForTypeItem(type21Question, itemUserID, itemAcceptAnswerID, itemAcceptAnswerUserID, itemAnswerUserList, itemTags) 
                    iCountType21 += 1
                    if iCountType21 >= 300:
                        bType21Full = True                    
            # this item is for Haskell --> type22
            if listTag[3] in itemTags: 
                if bType22Full == False:
                    SetValueForTypeItem(type22Question, itemUserID, itemAcceptAnswerID, itemAcceptAnswerUserID, itemAnswerUserList, itemTags) 
                    iCountType22 += 1
                    if iCountType22 >= 300:
                        bType22Full = True             
            if bType22Full and bType21Full and bType12Full and bType11Full:
                break
                    
    print listTag[0] + " Count: " + str(len(type11Question)) + " --> Iterator Time: " + str(iCountType11) 
    print listTag[1] + " Count: " + str(len(type12Question)) + " --> Iterator Time: " + str(iCountType12)
    print listTag[2] + " Count: " + str(len(type21Question)) + " --> Iterator Time: " + str(iCountType21)
    print listTag[3] + " Count: " + str(len(type22Question)) + " --> Iterator Time: " + str(iCountType22)
        
    conn.commit()
    cur.close()
    conn.close()
    
def SaveValidInfoIntoDB(type11, type12, type21, type22, type11Question, type12Question, type21Question, type22Question):
    '''
    1: Link the database: 
       a) name: graphanalysisdb
       b) user: ponza
       c)password: lxwg
    2: insert data into DB 
    3: create dump file 
    4: Close DB 
    '''
    #Link DB 
    conn = psycopg2.connect(database="graphanalysisdb", user="ponza", password="lxwg", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    
    #For Type 11
    cur.execute("delete from type11 where 1=1")
    for item in type11Question:
        strTagList = ",".join(item.listTag)   
        strAnswerUserList = ",".join(item.listAnswerUser) 
        cur.execute("INSERT INTO type11 VALUES('%s', '%s', '%s', %s, %s, %s, '%s')" %(type11.tagName, type11.groupName, 
                                                                                strTagList, item.userID, item.acceptAnswerID, item.acceptAnswerUserID, strAnswerUserList))        
    #For Type 12
    cur.execute("delete from type12 where 1=1")
    for item in type12Question:
        strTagList = ",".join(item.listTag)  
        strAnswerUserList = ",".join(item.listAnswerUser)      
        cur.execute("INSERT INTO type12 VALUES('%s', '%s', '%s', %s, %s, %s, '%s')" %(type12.tagName, type12.groupName, 
                                                                                strTagList, item.userID, item.acceptAnswerID, item.acceptAnswerUserID, strAnswerUserList))        
    #For Type 21
    cur.execute("delete from type21 where 1=1")
    for item in type21Question:
        strTagList = ",".join(item.listTag)  
        strAnswerUserList = ",".join(item.listAnswerUser)      
        cur.execute("INSERT INTO type21 VALUES('%s', '%s', '%s', %s, %s, %s, '%s')" %(type21.tagName, type21.groupName, 
                                                                                strTagList, item.userID, item.acceptAnswerID, item.acceptAnswerUserID, strAnswerUserList))
    #For Type 22
    cur.execute("delete from type22 where 1=1")
    for item in type22Question:
        strTagList = ",".join(item.listTag)    
        strAnswerUserList = ",".join(item.listAnswerUser)    
        cur.execute("INSERT INTO type22 VALUES('%s', '%s', '%s', %s, %s, %s, '%s')" %(type22.tagName, type22.groupName, 
                                                                                strTagList, item.userID, item.acceptAnswerID, item.acceptAnswerUserID, strAnswerUserList))
    #Commit data to databse 
    conn.commit()    
    #Close DB    
    cur.close()
    conn.close()
    
    #Save DumpFile
    '''
    pg_dumpPath = "C:\Program Files\PostgreSQL\9.4\bin\pg_dump"
    dumpFileOutputPath = "D:\lxwg\From_Ubuntu\Data\PostqresqlTest\graphanalysisdb.dump"
    dbUserName = "ponza"
    dbName = "graphanalysisdb"
    strCmd = pg_dumpPath + " -Fc " + " -U " +  dbUserName + " -d " +  dbName + " > " + dumpFileOutputPath
    os.system(strCmd)
    '''
    
############################################################
#Main Function
type11 = Category(listTag[0], listGroup[0])         
type12 = Category(listTag[1], listGroup[0])
type21 = Category(listTag[2], listGroup[1])
type22 = Category(listTag[3], listGroup[1])
type11Question = []
type12Question = []
type21Question = []
type22Question = []
LoadData(type11Question, type12Question, type21Question, type22Question)
SaveValidInfoIntoDB(type11, type12, type21, type22, type11Question, type12Question, type21Question, type22Question)

                
        
    
        
         
    

                
    
    


