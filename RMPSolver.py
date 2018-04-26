# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:25:53 2018

@author: Guillaume
"""

from cplex_problems_master import construct_master_problem, add_variable_to_master_and_rebuild, add_f_constraint
from cplex_problems_master2 import construct_master_problem2, add_variable_to_master_and_rebuild2
from learn_tree_funcs import get_num_features,get_left_leafs,get_right_leafs,get_data_size, get_num_targets

def create_new_master(inputdepth,segments_set):
    
    return construct_master_problem(inputdepth,segments_set)

def create_new_master2(inputdepth,segments_set):
    
    return construct_master_problem2(inputdepth,segments_set)

def solveRMP(prob):
    
    prob.solve()
    
def add_column(depth,prob,inputdepth,segments_set,segment_to_add,leaf):
    
    return add_variable_to_master_and_rebuild(depth,prob,inputdepth,segments_set,segment_to_add,leaf)

def add_column2(depth,prob,inputdepth,segments_set,segment_to_add,leaf):
    
    return add_variable_to_master_and_rebuild2(depth,prob,inputdepth,segments_set,segment_to_add,leaf)

def RMP_add_f_constraint(prob,i,j,right_side):
    
    return add_f_constraint(prob,i,j,right_side)

def display_RMP_solution_dual(depth,prob,CGiter):
        
    print("--------------------- RMP("+str(CGiter)+") Solution ---------------------");
    
    num_leafs = 2**depth 
    
    num_nodes = num_leafs-1
    
    num_features = get_num_features()
      
    for i in range(num_features): #constraint (15),

        for j in range(num_nodes):
            
            left_leaves = get_left_leafs(j, num_nodes)
            
            for l in left_leaves:
                
                print("Pi("+str(i)+"_"+str(j)+"_"+str(l)+"-15-)*= "+"%.2f" % round(-prob.solution.get_dual_values("constraint_15_"+str(i)+"_"+str(j)+"_"+str(l)),2))

    for i in range(num_features): #constraint (16),

        for j in range(num_nodes):
            
            right_leaves = get_right_leafs(j, num_nodes)
            
            for l in right_leaves:
                
                print("Pi("+str(i)+"_"+str(j)+"_"+str(l)+"-16-)*= "+"%.2f" % round(-prob.solution.get_dual_values("constraint_16_"+str(i)+"_"+str(j)+"_"+str(l)),2))
 
    data_size = get_data_size()
    
    for r in range(data_size): #constraint (17),
        
            print("Th_"+str(r)+"*= "+"%.2f" % round(-prob.solution.get_dual_values("constraint_17_"+str(r)),2))
        
    for l in range(num_leafs): #constraint (18),
        
         print("Be_"+str(l)+"*= "+"%.2f" % round(-prob.solution.get_dual_values("constraint_18_"+str(l)),2))
         
    for r in range(data_size): #constraint (19),
        
        for l in range(num_leafs):
    
            print("Gm_"+str(r)+"_"+str(l)+"*= "+"%.2f" % round(-prob.solution.get_dual_values("constraint_19_"+str(r)+"_"+str(l)),2))
            
    print("--------------------- RMP("+str(CGiter)+") Solution ---------------------");
    
def display_RMP_solution_primal(depth,prob,CGiter,segments_set):
        
    print("--------------------- RMP("+str(CGiter)+") Solution ---------------------");
    
    num_leafs = 2**depth 
    
    num_nodes = num_leafs-1
    
    num_features = get_num_features()
    
    data_size = get_data_size()
        
    # node n had a boolean test on feature f, boolean. On the paper: f_{i,j}

    for j in range(num_nodes):

        for i in range(num_features):
            
            print("f_"+str(i)+"_"+str(j)+"*= "+"%.2f" % round(prob.solution.get_values("node_feature_" + str(j) + "_" + str(i)),2))
            
    # value used in the boolean test in node n, integer. On the paper: c_{j}

    for j in range(num_nodes):
        
        print("c_"+str(j)+"*= "+"%.2f" % round(prob.solution.get_values("node_constant_" + str(j)),2))
        
    # leaf l predicts type t, boolean. On the paper: p_{l,t}
    
    for l in range(num_leafs):

        for t in range(get_num_targets()):
            
            print("p_"+str(l)+"_"+str(t)+"*= "+"%.2f" % round(prob.solution.get_values("prediction_type_" + str(t) + "_" + str(l)),2))
                        
    # row error, variables to minimize. On the paper: e_{r}

    for r in range(data_size):
        
        print("e_"+str(r)+"*= "+"%.2f" % round(prob.solution.get_values("row_error_" + str(r)),2))
                
    for l in range(num_leafs): # x_{l,s}
    
        for s in range(len(segments_set[l])): 
            
            print("x_"+str(l)+"_"+str(s)+"*= "+"%.2f" % round(prob.solution.get_values("segment_leaf_" + str(s) + "_" + str(l)),2))
                        
    print("Objective value :",round(prob.solution.get_objective_value(),2))

    print("--------------------- RMP("+str(CGiter)+") Solution ---------------------");
    
def display_prob_lite(prob,side):
    
    if side == "primal":
        
        for i in prob.variables.get_names():
            
            print(i, prob.solution.get_values(i))
            
    else:
        
        for i in prob.linear_constraints.get_names():
            
            print(i, prob.solution.get_dual_values(i))