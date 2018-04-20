# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:12:37 2018

@author: Guillaume
"""

from RMPSolver import create_new_master
from BaP_Node import BaP_Node
import time
from nodes_external_management import hash_seg

def BBSolver(TARGETS,segments_set,best_solution_value,inputdepth):
    
    prob=create_new_master(inputdepth,segments_set)
                
    root_node=BaP_Node(segments_set,prob,"",[],[],[],[[hash_seg(segments_set[l][0])] for l in range(len(segments_set))]) #construct root node
    
    a=time.time()
    
    root_node.explore()
    
    print("Full time : ",time.time()-a)
    
    print("Lower bound at root node : ",root_node.prob.solution.get_objective_value())
    
    return root_node
    
    if root_node.solution_type == 'integer':
        
        return root_node
    
    else:
        
        root_node.create_children_by_branching() #TODO ;
    
    queue = ["0", "1"]
    
    while queue != []:
        
        current_node = get_node(Queue[0]) #TODO ;
        
        current_node.explore()
        
        sol_type = current_node.solution_type
        
        if sol_type != 'infeasible':
            
            if sol_type == 'integer':
                
                best_solution_value = update_UB(best_solution_value,current_node.prob.solution_value) #TODO ;
                
            elif current_node.prob.solution_value < best_solution_value:
                
                current_node.create_children_by_branching() #TODO ;
                
                ID = current_node.ID
                
                queue.extend([ID+"0",ID+"1"])
        
        del queue[0]
        
        arrange_queue(chosen_method) #TODO ;