# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 09:58:55 2018

@author: Guillaume
"""

import regtrees2 as tr
from learn_tree_funcs import transform_data, read_file, write_file
import copy
from BaP_Node import obtain_depth2
from nodes_external_management import obtain_depth, init_rand_hash
from cplex_problems_master import obtain_TARGETS
from cplex_problems_master2 import obtain_TARGETS2

def create_instance(inputfile):
    
    read_file(inputfile)
   
    transform_data()

    write_file(inputfile+".transformed")
   
    tr.df = tr.get_data(inputfile+".transformed")
    
def create_first_solution(inputdepth):
    
    a=tr.learnTrees_and_return_segments(inputdepth)
    
    tr.get_code()
    
    return a

def create_complete_tree(segments_set,inputdepth):
    
    while len(segments_set)!=2**inputdepth:
        
        print(len(segments_set[-1][0])/2)
        
        L1, L2 = copy.copy(segments_set[-1][0][0:(len(segments_set[-1][0])/2)]), copy.copy(segments_set[-1][0][len(segments_set[-1][0])/2:])
        
        segments_set[-1]=[L1]
        
        segments_set.append([L2])
        
def initialize_global_values(TARGETS,inputdepth):
    
    obtain_TARGETS(TARGETS) #give TARGETS to the cplex_problems_master module
    obtain_TARGETS2(TARGETS) #give TARGETS to the cplex_problems_master2 module
    obtain_depth(inputdepth) #give depth to the nodes_external_management module
    obtain_depth2(inputdepth) #give depth to the BaP_Node module
    init_rand_hash() #initialize the hash table