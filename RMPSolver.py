# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:25:53 2018

@author: Guillaume
"""

from cplex_problems_CG import construct_master_problem, add_variable_to_master_and_rebuild

def create_new_master(inputdepth,segments_set):
    
    return construct_master_problem(inputdepth,segments_set)

def solveRMP(prob):
    
    prob.solve()
    
def add_column(prob,inputdepth,segments_set,segment_to_add,leaf):
    
    return add_variable_to_master_and_rebuild(prob,inputdepth,segments_set,segment_to_add,leaf)

def display_RMP_solution(depth,prob):
    from learn_tree_funcs import get_num_features,get_left_leafs
    
    num_leafs = 2**depth 
    
    num_nodes = num_leafs-1
    
    num_features = get_num_features()
  
    for i in range(num_features): #constraint (15), indicator 0

        for j in range(num_nodes):
            
            left_leaves = get_left_leafs(j, num_nodes)
            
            for l in left_leaves:

                print("Pi("+i+"_"+j+"_"+l+")*= "+"%.2f" % round(prob.solution.get_dual_values(i*len(num_nodes)+j*len(left_leaves)+l),2))
