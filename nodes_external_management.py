# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 11:27:19 2018

@author: Guillaume
"""

from learn_tree_funcs import get_data_size
from cplex_problems_CG import construct_pricing_problem, contruct_pricing_problem_all_at_once
from random import shuffle
import matplotlib.pyplot as plt
import random

"""HASH FUNCTIONS"""


def init_rand_hash():
    random.seed(0)
    global rand_hash
    rand_hash = [random.random() for r in range(get_data_size())]

def hash_seg(seg):
        
    return sum([rand_hash[r] for r in seg])



"""TOOL FUNCTIONS"""



def color_leaf(l):
    
    if l==0:
        
        return 'b'
    
    else:
    
        return 'r'

def obtain_depth(d):
    global depth
    depth=d
    
    
    
def check_unicity(segments_set):
    
    check=True
    
    for l in range(len(segments_set)):
        
        for s1 in range(len(segments_set[l])):
            
            for s2 in range(s1,len(segments_set[l])):
                
                if s1!=s2 and segments_set[l][s1]==segments_set[l][s2]:
                
                    check=False
                    
        print(check)
        
        if not check:
            
            input()
         
            
            
"""EXTRACTING ROWS FROM THE SOLUTION AND THE SOLUTION TYPE"""
    


def extract_rows_pricing(pricing_prob): #return the segment given by the pricing pb
    
    seg, sol = [], pricing_prob.solution.get_values()
    
    for r in range(get_data_size()):
        
        if sol[r] == 1:
            
            seg.append(r)
    
    return seg

def extract_rows_pricing_all_at_once(pricing_prob_all_at_once,num_leafs):
    
    seg, sol, datasize = [[] for l in range(num_leafs)], pricing_prob_all_at_once.solution.get_values(), get_data_size()
    
    for l in range(num_leafs):
    
        for r in range(datasize):
            
            if sol[l*datasize + r] == 1:
                
                seg[l].append(r)
    
    return seg

def give_solution_type(prob): #return a string saying if the solution is integral, continuous or infeasible
    
    if "infeasible" in prob.solution.status[prob.solution.get_status()]:

        return "infeasible"
    
    else:
        
        for i in prob.solution.get_values():
            
            if (float(i) <= round(i) - 0.01) or (float(i) >= round(i) + 0.01):
                
                return "continuous"
            
        return "integer"
    
    
    
"""BRANCHING FUNCTION"""
    


def adapt_segments_set(segments_set,row,leaf,branching): #TODO ; update hash table. This function adapts the segments_set according to the branching rule
    
    new_segments_set=[[] for l in range(len(segments_set))]
    
    if branching==1:
        
        for l in range(len(segments_set)):
            
            for s in segments_set[l]:
            
                if l==leaf and row in s:
                    
                    new_segments_set[l].append(s)
                    
                elif l!=leaf and row not in s:
                    
                    new_segments_set[l].append(s)
                    
    else:
        
        for l in range(len(segments_set)):
            
            for s in segments_set[l]:
            
                if l==leaf and row not in s:
                    
                    new_segments_set[l].append(s)
                    
                elif l!=leaf and row in s:
                    
                    new_segments_set[l].append(s)    
    
    return new_segments_set



"""SOLVE PRICING MANAGEMENT"""



def solve_pricing_given_leaf(prob,leaf,branched_rows,branched_leaves,ID,existing_segments,add_rows_excl=[]): #return a tuple (segments, obj_value).
    
    rows_to_be_excluded, rows_to_be_included = add_rows_excl, []
    
    for l in range(len(branched_leaves)):
        
        if branched_leaves[l] == leaf:
            
            if ID[l] == 1:
                
                rows_to_be_included.append(branched_rows[l])
                
            else:
                
                rows_to_be_excluded.append(branched_rows[l])
                
    pricing_prob = construct_pricing_problem(depth,prob,rows_to_be_excluded,rows_to_be_included,leaf,existing_segments)
        
    pricing_prob.solve()
        
    obj_value = pricing_prob.solution.get_objective_value()
    
    from cplex_problems_CG import constraint_indicators
    
    obj_value = obj_value + prob.solution.get_dual_values()[constraint_indicators[3] + leaf]
    
    #print("Bheta "+str(leaf)+" :"+str(prob.solution.get_dual_values()[constraint_indicators[3] + leaf]))
    
    segment = extract_rows_pricing(pricing_prob)
        
    return segment, obj_value

def solve_pricing_all_at_once(prob,branched_rows,branched_leaves,ID,segments_set):
    
    pricing_prob_all_at_once = contruct_pricing_problem_all_at_once(depth,prob,branched_rows,branched_leaves,ID,segments_set)
        
    pricing_prob_all_at_once.solve()
        
    obj_value = pricing_prob_all_at_once.solution.get_objective_value()
    
    from cplex_problems_CG import constraint_indicators
    
    obj_value = obj_value + sum([prob.solution.get_dual_values()[constraint_indicators[3] + leaf] for leaf in range(len(segments_set))])
            
    segment = extract_rows_pricing_all_at_once(pricing_prob_all_at_once,len(segments_set))
        
    return segment, obj_value

def solve_pricing(prob,segments_set,branched_rows,branched_leaves,ID,pricing_method): #return a tuple (segments_to_be_added, convergence)
    
    from BaP_Node import count_iter
    
    num_leafs = len(segments_set)
        
    segments_to_be_added, obj_values, segments_to_be_added_ordered = [], [], []
    
    if pricing_method==1:
    
        for l in range(num_leafs): # TODO ; implement new pricing_method
            
            segments, value = solve_pricing_given_leaf(prob,l,branched_rows,branched_leaves,ID,segments_set[l])
            
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
                
                segment, value = solve_pricing_given_leaf(prob,true_l,branched_rows,branched_leaves,ID,segments_set[true_l],excl_rows)
            
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
        
        segments, value = solve_pricing_all_at_once(prob,branched_rows,branched_leaves,ID,segments_set)
            
        segments_to_be_added_ordered = segments
        
        obj_values.append(value)
        
        plt.scatter(count_iter,value,color='k')
        
        plt.pause(0.01)
        
        #print(segments)
                    
        print("Reduced cost for partition : ",str(value))
                                
    return segments_to_be_added_ordered, ((min(obj_values) - int(pricing_method>=2)) > -0.01)