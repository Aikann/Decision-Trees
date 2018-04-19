# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 11:08:04 2018

@author: Guillaume
"""

from cplex_problems_CG import construct_pricing_problem, contruct_pricing_problem_all_at_once
from nodes_external_management import extract_rows_pricing, extract_rows_pricing_all_at_once, color_leaf
import matplotlib.pyplot as plt
from random import shuffle
from learn_tree_funcs import get_data_size



def solve_pricing_given_leaf(depth,prob,leaf,branched_rows,branched_leaves,ID,existing_segments,add_rows_excl=[]): #return a tuple (segments, obj_value).
    
    rows_to_be_excluded, rows_to_be_included = add_rows_excl, []
    
    for l in range(len(branched_leaves)):
        
        if branched_leaves[l] == leaf:
            
            if ID[l] == 1:
                
                rows_to_be_included.append(branched_rows[l])
                
            else:
                
                rows_to_be_excluded.append(branched_rows[l])
                
    #input()
                
    pricing_prob = construct_pricing_problem(depth,prob,rows_to_be_excluded,rows_to_be_included,leaf,existing_segments)
            
    pricing_prob.solve()
        
    obj_value = pricing_prob.solution.get_objective_value()
    
    from cplex_problems_CG import constraint_indicators
    
    obj_value = obj_value + prob.solution.get_dual_values()[constraint_indicators[3] + leaf]
    
    #print("Bheta "+str(leaf)+" :"+str(prob.solution.get_dual_values()[constraint_indicators[3] + leaf]))
    
    segment = extract_rows_pricing(pricing_prob)
        
    return segment, obj_value




def solve_pricing_all_at_once(depth,prob,branched_rows,branched_leaves,ID,segments_set):
    
    pricing_prob_all_at_once = contruct_pricing_problem_all_at_once(depth,prob,branched_rows,branched_leaves,ID,segments_set)
        
    pricing_prob_all_at_once.solve()
        
    obj_value = pricing_prob_all_at_once.solution.get_objective_value()
    
    from cplex_problems_CG import constraint_indicators
    
    obj_value = obj_value + sum([prob.solution.get_dual_values()[constraint_indicators[3] + leaf] for leaf in range(len(segments_set))])
            
    segment = extract_rows_pricing_all_at_once(pricing_prob_all_at_once,len(segments_set))
        
    return segment, obj_value





def solve_pricing(depth,prob,segments_set,branched_rows,branched_leaves,ID,pricing_method): #return a tuple (segments_to_be_added, convergence)
    
    from BaP_Node import count_iter
    
    num_leafs = len(segments_set)
        
    segments_to_be_added, obj_values, segments_to_be_added_ordered = [], [], []
    
    if pricing_method==1:
    
        for l in range(num_leafs): # TODO ; implement new pricing_method
            
            segments, value = solve_pricing_given_leaf(depth,prob,l,branched_rows,branched_leaves,ID,segments_set[l])
            
            segments_to_be_added_ordered.append(segments)
            
            obj_values.append(value)
            
            plt.scatter(count_iter,value,color=color_leaf(l))
            
            plt.pause(0.01)
                        
            print("Reduced cost for leaf "+str(l)+" :",str(value))
            
    elif pricing_method==2:
                
        excl_rows, remember_order = [], []
        
        shuffle_leaves=range(num_leafs)
        
        shuffle(shuffle_leaves)
        
        for l in range(num_leafs):
            
            true_l=shuffle_leaves[l]
            
            if l!=num_leafs-1:
                
                segment, value = solve_pricing_given_leaf(depth,prob,true_l,branched_rows,branched_leaves,ID,segments_set[true_l],excl_rows)
            
                segments_to_be_added.append(segment) 
                
                excl_rows.extend(segment)
                
                obj_values.append(value)
                
                #print(segment)
                
                plt.scatter(count_iter,value,color=color_leaf(true_l))
                
                plt.pause(0.01)
                
                #print(segment)
                            
                print("Reduced cost for leaf "+str(true_l)+" :",str(value))
                
            else:
                
                segment = [i for i in range(get_data_size()) if i not in excl_rows]
                
                segments_to_be_added.append(segment)
                
                #print(segment)
                
            remember_order.append(true_l)
                
        segments_to_be_added_ordered = [x for _,x in sorted(zip(remember_order,segments_to_be_added))]
        
    elif pricing_method==3:
        
        segments, value = solve_pricing_all_at_once(depth,prob,branched_rows,branched_leaves,ID,segments_set)
            
        segments_to_be_added_ordered = segments
        
        obj_values.append(value)
        
        plt.scatter(count_iter,value,color='k')
        
        plt.pause(0.01)
        
        print(segments)
                    
        print("Reduced cost for partition : ",str(value))
                                
    return segments_to_be_added_ordered, ((min(obj_values) - int(pricing_method>=2)) > -0.01)