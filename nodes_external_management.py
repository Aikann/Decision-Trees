# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 11:27:19 2018

@author: Guillaume
"""

from learn_tree_funcs import get_data_size
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
    
    elif l==1:
    
        return 'r'
    
    elif l==2:
    
        return 'y'
    
    else:
        
        return 'm'

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
            
            if 0.99 <= sol[l*datasize + r] <= 1.01:
                
                seg[l].append(r)
    
    return seg[::-1]

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