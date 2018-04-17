# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:09:31 2018

@author: Guillaume
"""

from BaP_Node import BaP_Node, obtain_depth2
from nodes_external_management import obtain_depth, init_rand_hash
import getopt
import sys
import regtrees2 as tr
from learn_tree_funcs import transform_data, read_file, write_file
from cplex_problems_CG import construct_master_problem, obtain_TARGETS


def main(argv):
    
    global TARGETS
    global segments_set
    global VARS
    
    inputfile = ''

    try:
       
        opts, args = getopt.getopt(argv,"f:d:",["ifile=","depth="])

    except getopt.GetoptError:
       
        sys.exit(2)
      
    for opt, arg in opts:

        if opt in ("-f", "--ifile"):

            inputfile = arg
        
        elif opt in ("-d", "--depth"):

            inputdepth = int(arg)
            
    read_file(inputfile)
   
    transform_data()

    write_file(inputfile+".transformed")
   
    tr.df = tr.get_data(inputfile+".transformed")
                   
    TARGETS, segments_set, best_solution_value=tr.learnTrees_and_return_segments(inputdepth)
    
    obtain_TARGETS(TARGETS) #give TARGETS to the cplex_problems_CG module
    
    obtain_depth(inputdepth) #give depth to the BaP_Node module
    obtain_depth2(inputdepth) #give depth to the BaP_Node module
    init_rand_hash() #initialize the hash table
    
    tr.get_code()
            
    prob=construct_master_problem(inputdepth,segments_set)
    
    #from cplex_problems_CG import VARS #so VARS is accessible from this module
            
    root_node=BaP_Node(segments_set,prob,"",[],[],[],[[] for l in range(len(segments_set))])
    
    #root_node.prob.solve()
            
    root_node.solve_relaxation()
    
    return root_node
    
r=main(["-fIndiansDiabetes30rows.csv","-d 1"])