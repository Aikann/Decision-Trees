# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:12:37 2018

@author: Guillaume
"""

from RMPSolver import create_new_master, display_RMP_solution_primal, create_new_master2, display_prob_lite
from BaP_Node import BaP_Node
import time
from nodes_external_management import hash_seg
import copy
from learn_tree_funcs import get_num_features, get_data_size, get_num_targets
import matplotlib.pyplot as plt

chosen_method = "DEPTH_FIRST"

def BBSolver(TARGETS,segments_set,best_solution_value,inputdepth):
    
    prob=create_new_master2(inputdepth,segments_set)
    
    H = [[0] for l in range(len(segments_set))]
    
    for l in range(len(segments_set)):
        
        for s in range(len(segments_set[l])):
        
            H[l].append(hash_seg(segments_set[l][s]))
                
    root_node=BaP_Node(segments_set,prob,"",None,H,[],[]) #construct root node
    
    best_ID = 'Solution provided by warm start'
    
    a=time.time()
    
    root_node.explore()
    
    print("Full time : ",time.time()-a)
    
    print("Lower bound at root node : ",root_node.prob.solution.get_objective_value())
    
    #display_RMP_solution_primal(inputdepth,root_node.prob,0,root_node.segments_set)
    
    #return root_node
    
    if root_node.solution_type == 'integer':
        
        return root_node
    
    else:
                                
        var, index = select_var_to_branch(root_node, inputdepth)
                
        root_node.create_children_by_branching(var,index)
        
        #return root_node
    
    queue = ["0", "1"]
    
    while queue != []: #TODO ; update LB
        
        plt.close()
        
        current_node = get_node(queue[0],root_node)
        
        print("Solving at ID: ",queue[0])
        
        print("Branching on "+str(queue[0][-1])+" : "+str(var)+" "+str(index))
                
        print(current_node.segments_set)
        
        #input()
        
        current_node.explore()
        
        sol_type = current_node.solution_type
        
        print("My ID: "+queue[0]," --- Solution type: ",sol_type," --- Value: ",current_node.solution_value)
                
        if sol_type != 'infeasible':
            
            print(display_prob_lite(current_node.prob,"primal"))
                        
            if sol_type == 'integer':
                
                best_ID, best_solution_value = update_UB(best_solution_value,current_node,best_ID)
                
            elif current_node.solution_value < best_solution_value:
                                
                var, index = select_var_to_branch(current_node, inputdepth)
                
                current_node.create_children_by_branching(var,index)
                
                ID = current_node.ID
                
                queue.extend([ID+"0",ID+"1"])
        
        del queue[0]
        
        arrange_queue(queue,chosen_method)
        
    print("Best solution: ",best_solution_value)
    
    print("Best_ID: ",best_ID)
    
    print("Total time :"+str(time.time() - a))
        
    return root_node
        
        
def get_node(ID,root_node):
    
    node = root_node
    
    for i in ID:
        
        if i == "0":
            
            node = node.child0
            
        else:
            
            node = node.child1
    
    return node
        
        
def update_UB(best_value,current_node,prev_ID):
    
    val = current_node.prob.solution.get_objective_value()
    
    if val < best_value:
        
        best_ID = current_node.ID
                
        return best_ID, val
    
    else:
        
        return prev_ID, val
    
def arrange_queue(queue,chosen_method):
    
    if chosen_method == "HORIZONTAL_SEARCH":
        
        return
    
    elif chosen_method == "DEPTH_FIRST":
        
        queue.sort()
        
        return
        
def select_var_to_branch(node,depth): # TO DO ; proprely
    
    data_size = get_data_size()
    
    num_features = get_num_features()

    num_leafs = 2**depth

    num_nodes = num_leafs-1
    
    for l in range(num_leafs):
        
        for t in range(get_num_targets()):
            
            if not already_branch(node,'p',(l,t)):
                
                return 'p', (l,t)
    
    for i in range(num_features):
        
        for j in range(num_nodes):
            
            if not already_branch(node,'f',(i,j)):
                
                return 'f', (i, j)
            
    input("CAREFUL, THIS PART IS NOT CORRECT, MASTER WILL BE RE-BUILT")
            
    for r in range(data_size):
        
        for l in range(num_leafs):
            
            if not already_branch(node,'row_leaf',(r,l)):
                
                return 'row_leaf', (r, l)
            
            
    
def already_branch(node,var,index):
    
    for i in range(len(node.branch_index)):
        
        if node.branch_index[i] == index and var == node.branch_var[i]:
            
            return True
        
    return False
    
            