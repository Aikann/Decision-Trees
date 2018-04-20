# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:09:31 2018

@author: Guillaume
"""

from BBSolver import BBSolver
import getopt
import sys
from Instance import create_instance, create_first_solution, create_complete_tree, initialize_global_values


def main(argv):
    
    global TARGETS
    
    try:
       
        opts, args = getopt.getopt(argv,"f:d:",["ifile=","depth="])

    except getopt.GetoptError:
       
        sys.exit(2)
      
    for opt, arg in opts:

        if opt in ("-f", "--ifile"):

            inputfile = arg
        
        elif opt in ("-d", "--depth"):

            inputdepth = int(arg)
            
    create_instance(inputfile)
                   
    TARGETS, segments_set, best_solution_value=create_first_solution(inputdepth)
    
    create_complete_tree(segments_set,inputdepth)
    
    initialize_global_values(TARGETS,inputdepth)
        
    print(segments_set)
    
    return BBSolver(TARGETS, segments_set, best_solution_value, inputdepth)
    
root=main(["-fIndiansDiabetes80rows.csv","-d 1"])