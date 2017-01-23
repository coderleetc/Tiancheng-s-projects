'''
Created on Dec 5, 2015

Test.py is a test used for output the data and graph of four class 

'''

from GraphGenerator import *

def main():
    
    print "////////// html //////////"
    g11 = GraphGenerator("type11", "HTML")
    g11.Output()
    
    
    print "////////// css //////////"
    g12 = GraphGenerator("type12", "CSS")
    g12.Output()
    
    print "////////// lisp //////////"
    g21 = GraphGenerator("type21", "LISP")
    g21.Output()
    
    print "////////// haskell //////////"
    g22 = GraphGenerator("type22", "HASKELL")
    g22.Output()
    
if __name__ == "__main__":
    main()