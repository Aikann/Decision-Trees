# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 11:08:04 2018

@author: Guillaume
"""

from cplex_problems_indiv_pricing import construct_pricing_problem
from cplex_problems_all_at_once_pricing import contruct_pricing_problem_all_at_once
from nodes_external_management import extract_rows_pricing, extract_rows_pricing_all_at_once, color_leaf
import matplotlib.pyplot as plt
from random import shuffle
from learn_tree_funcs import get_data_size, get_num_features, get_feature_value



def solve_pricing_given_leaf(depth,prob,leaf,branched_rows,branched_f,ID,existing_segments,add_rows_excl=[]): #return a tuple (segments, obj_value).
    
    rows_to_be_excluded, rows_to_be_included = add_rows_excl, []
    
    for l in range(len(branched_rows)):
        
        if branched_rows[l][1] == leaf:
            
            if ID[l] == 1:
                
                rows_to_be_included.append(branched_rows[l][0])
                
            else:
                
                rows_to_be_excluded.append(branched_rows[l][0])
                
    #input()
                    
    pricing_prob = construct_pricing_problem(depth,prob,rows_to_be_excluded,rows_to_be_included,leaf,existing_segments)
            
    pricing_prob.solve()
        
    obj_value = pricing_prob.solution.get_objective_value()
        
    obj_value = obj_value - prob.solution.get_dual_values("constraint_18_"+str(leaf))
    
    #obj_value = obj_value + sum([prob.solution.get_dual_values("branch_f_"+str(i)+"_"+str(j)) for (i,j) in branched_f])
    
    #print("Bheta "+str(leaf)+" :"+str(prob.solution.get_dual_values()[constraint_indicators[3] + leaf]))
    
    segment = extract_rows_pricing(pricing_prob)
        
    return segment, obj_value




def solve_pricing_all_at_once(depth,prob,branched_rows,branched_f,ID,segments_set):
    
    pricing_prob_all_at_once = contruct_pricing_problem_all_at_once(depth,prob,branched_rows,branched_f,ID,segments_set)
        
    pricing_prob_all_at_once.solve()
            
    obj_value = pricing_prob_all_at_once.solution.get_objective_value()
            
    """
    
    v=0
    
    for l in range(2**depth):
        
        for r in range(get_data_size()):
    
            print(r,l,pricing_prob_all_at_once.solution.get_values()[v],pricing_prob_all_at_once.objective.get_linear()[v])
            
            v=v+1
    
    print("OBJ VALUE ",obj_value)
    
    """
    
    obj_value = obj_value - sum([prob.solution.get_dual_values("constraint_18_"+str(leaf)) for leaf in range(len(segments_set))])
    
    #obj_value = obj_value + sum([prob.solution.get_dual_values("branch_f_"+str(i)+"_"+str(j)) for (i,j) in branched_f])
            
    #print("SUM BHETA ",sum([prob.solution.get_dual_values()[constraint_indicators[3] + leaf] for leaf in range(len(segments_set))]))
            
    segment = extract_rows_pricing_all_at_once(pricing_prob_all_at_once,len(segments_set))
    
    #display_pricing_all_at_once(depth,pricing_prob_all_at_once)
        
    return segment, obj_value





def solve_pricing(depth,prob,segments_set,branched_rows,branched_f,ID,pricing_method): #return a triple (segments_to_be_added, convergence, min(red_cost))
    
    from BaP_Node import count_iter
    
    num_leafs = len(segments_set)
        
    segments_to_be_added, obj_values, segments_to_be_added_ordered = [], [], []
    
    if pricing_method==1:
    
        for l in range(num_leafs): # TODO ; implement new pricing_method
            
            segments, value = solve_pricing_given_leaf(depth,prob,l,branched_rows,branched_f,ID,segments_set[l])
            
            segments_to_be_added_ordered.append(segments)
            
            obj_values.append(value)
            
            if value > -200:
            
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
                
                segment, value = solve_pricing_given_leaf(depth,prob,true_l,branched_rows,ID,segments_set[true_l],excl_rows)
            
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
        
        segments, value = solve_pricing_all_at_once(depth,prob,branched_rows,branched_f,ID,segments_set)
            
        segments_to_be_added_ordered = segments
        
        obj_values.append(value)
        
        plt.scatter(count_iter,value,color='k')
        
        plt.pause(0.01)
        
        #print(prob.solution.get_dual_values(),segments)
                    
        print("Reduced cost for partition : ",str(value))
                                
    return segments_to_be_added_ordered, ((min(obj_values) > -0.01) and (pricing_method==1)), min(obj_values)

def display_pricing_all_at_once(depth,prob):
    
    data_size=get_data_size()
    
    num_leafs=2**depth
    
    num_features = get_num_features()
    
    for leaf in range(num_leafs):
                    
        for r in range(data_size):
            
            print("z_"+str(r)+"_"+str(leaf)+"*= "+"%.2f" % round(prob.solution.get_values("row_" + str(leaf) + "_" + str(r)),2))
                                                                                                        
    # kappa_{i,r,l}, indicate the min feature of row r
    
    for leaf in range(num_leafs):
    
        for i in range(num_features):
            
            for r in range(data_size):
                
                if round(prob.solution.get_values("kappa_" +str(leaf) + "_" + str(r) + "_" + str(i)),2) == 1.0:
                
                    print("ka_"+str(i)+"_"+str(r)+"_"+str(leaf)+"*= "+"%.2f" % round(prob.solution.get_values("kappa_" +str(leaf) + "_" + str(r) + "_" + str(i)),2) + " feat value: "+str(get_feature_value(r,i)))
                                                                                    
    # omega_{i,r,l}, indicate the max feature of row r
    
    for leaf in range(num_leafs):
    
        for i in range(num_features):
            
            for r in range(data_size):
                
                if round(prob.solution.get_values("omega_" +str(leaf) + "_" + str(r) + "_" + str(i)),2) == 1.0:
                
                    print("om_"+str(i)+"_"+str(r)+"_"+str(leaf)+"*= "+"%.2f" % round(prob.solution.get_values("omega_" +str(leaf) + "_" + str(r) + "_" + str(i)),2) + " feat value: "+str(get_feature_value(r,i)))
                    
    print("Objective value :",round(prob.solution.get_objective_value(),2))