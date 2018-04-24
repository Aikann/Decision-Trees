# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:12:37 2018

@author: Guillaume
"""

from RMPSolver import create_new_master, display_RMP_solution_primal
from BaP_Node import BaP_Node
import time
from nodes_external_management import hash_seg
import copy
from learn_tree_funcs import get_num_features

chosen_method = "DEPTH_FIRST"

def BBSolver(TARGETS,segments_set,best_solution_value,inputdepth):
    
    prob=create_new_master(inputdepth,segments_set)
                
    root_node=BaP_Node(segments_set,prob,"",[],[],[],[[hash_seg(segments_set[l][0])] for l in range(len(segments_set))],[]) #construct root node
    
    best_node = root_node
    
    a=time.time()
    
    root_node.explore()
    
    print("Full time : ",time.time()-a)
    
    print("Lower bound at root node : ",root_node.prob.solution.get_objective_value())
    
    #display_RMP_solution_primal(inputdepth,root_node.prob,0,root_node.segments_set)
    
    return root_node
    
    if root_node.solution_type == 'integer':
        
        return root_node
    
    else:
        
        i, j = select_f_to_branch(root_node, inputdepth)
                
        root_node.create_children_by_branching_on_f(i,j) #TODO ;
        
        #return root_node
    
    queue = ["0", "1"]
    
    while queue != []: #TODO ; update LB
        
        current_node = get_node(queue[0],root_node)
        
        print("Solving at ID: ",queue[0])
        
        current_node.explore()
        
        sol_type = current_node.solution_type
        
        print("My ID: "+queue[0]," --- Solution type: ",sol_type," --- Value: ",current_node.solution_value)
        
        input()
        
        if sol_type != 'infeasible':
                        
            if sol_type == 'integer':
                
                best_node, best_solution_value = update_UB(best_solution_value,current_node)
                
            elif current_node.solution_value < best_solution_value:
                                
                i, j = select_f_to_branch(current_node,inputdepth)
                                                
                current_node.create_children_by_branching_on_f(i,j) #TODO ;
                
                ID = current_node.ID
                
                queue.extend([ID+"0",ID+"1"])
        
        del queue[0]
        
        arrange_queue(queue,chosen_method)
        
    print("Best solution: ",best_solution_value)
        
    return root_node
        
        
def get_node(ID,root_node):
    
    node = root_node
    
    for i in ID:
        
        if i == "0":
            
            node = node.child0
            
        else:
            
            node = node.child1
    
    return node
        
        
def update_UB(best_value,current_node):
    
    val = current_node.prob.solution.get_objective_value()
    
    if val < best_value:
        
        best_segments_set = copy.deepcopy(current_node.segments_set)
        best_prob = copy.deepcopy(current_node.prob)
        best_ID = copy.deepcopy(current_node.ID)
        
        best_node = BaP_Node(best_segments_set,best_prob,best_ID,None,[],[],[])
        
        return best_node, val
    
    else:
        
        return current_node, val
    
def arrange_queue(queue,chosen_method):
    
    if chosen_method == "HORIZONTAL_SEARCH":
        
        return
    
    elif chosen_method == "DEPTH_FIRST":
        
        queue.sort()
        
        return
        
def select_f_to_branch(node,depth): # TO DO ; proprely
    
    num_features = get_num_features()

    num_leafs = 2**depth

    num_nodes = num_leafs-1
    
    for i in range(num_features):
        
        for j in range(num_nodes):
            
            if (i,j) not in node.branched_f:
                
                return i, j