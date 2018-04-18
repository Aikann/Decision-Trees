# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:12:37 2018

@author: Guillaume
"""

from RMPSolver import construct_master_problem
from BaP_Node import BaP_Node

def BBSolver(TARGETS,segments_set,best_solution_value,inputdepth):
    
    prob=construct_master_problem(inputdepth,segments_set)
                
    root_node=BaP_Node(segments_set,prob,"",[],[],[],[[] for l in range(len(segments_set))]) #construct root node
    
    root_node.explore()
    
    print(root_node.prob.solution.get_objective_value())
    
    return
    
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