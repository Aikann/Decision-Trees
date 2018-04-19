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

def display_RMP_solution(depth,prob,CGiter):
    
    from learn_tree_funcs import get_num_features,get_left_leafs,get_right_leafs,get_data_size
    from cplex_problems_CG import constraint_indicators
    
    
    print("--------------------- RMP("+CGiter+") Solution ---------------------");
    
    num_leafs = 2**depth 
    
    num_nodes = num_leafs-1
    
    num_features = get_num_features()
    
    start_index = constraint_indicators(0)
  
    for i in range(num_features): #constraint (15),

        for j in range(num_nodes):
            
            left_leaves = get_left_leafs(j, num_nodes)
            
            for l in left_leaves:

                print("Pi("+i+"_"+j+"_"+l+"-15-)*= "+"%.2f" % round(prob.solution.get_dual_values(start_index+i*len(num_nodes)+j*len(left_leaves)+l),2))

    start_index = constraint_indicators(1)

    for i in range(num_features): #constraint (16),

        for j in range(num_nodes):
            
            right_leaves = get_right_leafs(j, num_nodes)
            
            for l in right_leaves:

                print("Pi("+i+"_"+j+"_"+l+"-16-)*= "+"%.2f" % round(prob.solution.get_dual_values(start_index+i*len(num_nodes)+j*len(right_leaves)+l),2))
 
    
    start_index = constraint_indicators(2)
    data_size = get_data_size()
    
    for r in range(data_size): #constraint (17),
        
            print("Th_"+r+"*= "+"%.2f" % round(prob.solution.get_dual_values(start_index+r),2))
    
    
    start_index = constraint_indicators(3)
    
    for l in range(num_leafs): #constraint (18),
        
         print("Be_"+l+"*= "+"%.2f" % round(prob.solution.get_dual_values(start_index+l),2))
         
         
    start_index = constraint_indicators(4)
     
    for r in range(data_size): #constraint (19),
        
        for l in range(num_leafs):
    
            print("Gm_"+r+"_"+l+"*= "+"%.2f" % round(prob.solution.get_dual_values(start_index+r*len(num_leafs)+l),2))
            
            
    print("--------------------- RMP("+CGiter+") Solution ---------------------");