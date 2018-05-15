# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:12:37 2018

@author: Guillaume
"""

from RMPSolver import create_new_master, display_RMP_solution_primal, create_new_master2, display_prob_lite
from BaP_Node import BaP_Node
import time
from nodes_external_management import hash_seg
from learn_tree_funcs import get_num_features, get_data_size, get_num_targets
import matplotlib.pyplot as plt

chosen_method = "HORIZONTAL_SEARCH"

def BBSolver(TARGETS,segments_set,best_solution_value,inputdepth):
    
    prob=create_new_master2(inputdepth,segments_set)
    
    H = [[0] for l in range(len(segments_set))]
    
    for l in range(len(segments_set)):
        
        for s in range(len(segments_set[l])):
        
            H[l].append(hash_seg(segments_set[l][s]))
                
    root_node=BaP_Node(segments_set,prob,"",None,H,[],[]) #construct root node
    
    best_ID = 'Solution provided by warm start'
    
    #best_solution_value = 3000
    
    a=time.time()
    
    root_node.explore(0)
    
    print("Full time : ",time.time()-a)
    
    print("Lower bound at root node : ",root_node.prob.solution.get_objective_value())
    
    LB = root_node.prob.solution.get_objective_value()
    
    if round(LB) - 1e-5 <= LB <= round(LB) + 1e-5:
        
        LB = int(round(LB))
        
    else:
        
        LB = int(LB) + 1
        
    LB_level = [[] for i in range(3000)]
    
    LB_level[0].append(LB)
    
    #display_RMP_solution_primal(inputdepth,root_node.prob,0,root_node.segments_set)
    
    #return root_node
    
    if root_node.solution_type == 'integer' or (LB==best_solution_value):
        
        print("Best solution: ",best_solution_value)
    
        print("Best_ID: ",best_ID)
    
        print("Total time :"+str(time.time() - a))
        
        return root_node
    
    else:
                                
        var, index = select_var_to_branch(root_node, inputdepth)
                
        root_node.create_children_by_branching(var,index)
        
        #return root_node
    
    queue = ["0", "1"]
    
    arrange_queue(queue,chosen_method)
    
    while queue != []:
        
        plt.close()
        
        current_node = get_node(queue[0],root_node)
        
        print("Solving at ID: ",queue[0])
        
        #input()
        
        print("Branching on "+str(queue[0][-1])+" : "+str(var)+" "+str(index))
                
        #print(current_node.segments_set)
        
        #input()
        
        current_node.explore(LB)
        
        sol_type = current_node.solution_type
        
        print("My ID: "+queue[0]," --- Solution type: ",sol_type," --- Value: ",current_node.solution_value)
                
        if sol_type != 'infeasible':
                        
            #print(display_prob_lite(current_node.prob,"primal"))
                                    
            if sol_type == 'integer':
                
                best_ID, best_solution_value = update_UB(best_solution_value,current_node,best_ID)
                
            elif current_node.solution_value < best_solution_value:
                                
                var, index = select_var_to_branch(current_node, inputdepth)
                
                current_node.create_children_by_branching(var,index)
                
                ID = current_node.ID
                
                queue.extend([ID+"0",ID+"1"])
                
        del queue[0]
        
        LB = update_LB(LB_level,current_node,queue,LB)
        
        print('LB_level',LB_level[0:20])
        
        print('LB',LB)
        
        print('queue',queue)
        
        #if len(current_node.ID) < len(queue[0]):
        
           # input()
                
        if LB==best_solution_value: #check optimality
            
            queue=[]
        
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


def update_LB(LB_level,current_node,queue,LB):
    
    level = len(current_node.ID)
    
    LB_level[level].append(current_node.solution_value)
    
    queue.sort(key=lambda x:len(x))
    
    if queue==[] or len(queue[0]) > level:
                
        new_LB = min(LB_level[level])
        
        if round(new_LB) - 1e-5 <= new_LB <= round(new_LB) + 1e-5:
        
            new_LB = int(round(new_LB))
        
        else:
        
            new_LB = int(new_LB) + 1
        
        return new_LB
    
    else:
    
        return LB
        
        
def update_UB(best_value,current_node,prev_ID):
    
    val = current_node.prob.solution.get_objective_value()
    
    if val < best_value:
        
        best_ID = current_node.ID
                
        return best_ID, val
    
    else:
        
        return prev_ID, best_value
    
def arrange_queue(queue,chosen_method): #in place, return None
    
    if chosen_method == "HORIZONTAL_SEARCH":
        
        return
    
    elif chosen_method == "DEPTH_FIRST_0":
        
        queue.sort()
        
        return
        
    elif chosen_method == "DEPTH_FIRST_1":
        
        for q in range(len(queue)):
            
            queue[q] = invert_ID(queue[q])
            
        queue.sort()
        
        for q in range(len(queue)):
            
            queue[q] = invert_ID(queue[q])
            
        return
       
def invert_ID(ID):    
    
    new_ID=""
    
    for i in ID:
                    
        new_ID = new_ID + str(1-int(i))
        
    return new_ID
            
    
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
    
            