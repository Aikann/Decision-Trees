# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 11:08:04 2018

@author: Guillaume
"""

from cplex_problems_indiv_pricing import construct_pricing_problem
from cplex_problems_all_at_once_pricing import contruct_pricing_problem_all_at_once
from cplex_problems_all_at_once_pricing2 import contruct_pricing_problem_all_at_once2
from cplex_problems_indiv_pricing2 import construct_pricing_problem2
from nodes_external_management import extract_rows_pricing, extract_rows_pricing_all_at_once, color_leaf
import matplotlib.pyplot as plt
from random import shuffle
from learn_tree_funcs import get_data_size, get_num_features, get_feature_value
from RMPSolver import display_prob_lite



def solve_pricing_given_leaf(depth,prob,leaf,branch_var,branch_index,ID,existing_segments):#return a tuple (segments, obj_value).
    
    rows_to_be_excluded, rows_to_be_included, segs_excluded = [], [], []
        
    for v in range(len(branch_var)):
        
        if branch_var[v] == 'row_leaf':
        
            if branch_index[v][1] == leaf:
                
                if ID[v] == '1':
                    
                    rows_to_be_included.append(branch_index[v][0])
                    
                else:
                    
                    rows_to_be_excluded.append(branch_index[v][0])
                
    #input()
    
    for s in range(len(existing_segments)):
        
        if float(prob.solution.get_reduced_costs("segment_leaf_"+str(s)+"_"+str(leaf))) >= 0.01 or float(prob.solution.get_reduced_costs("segment_leaf_"+str(s)+"_"+str(leaf))) <= -0.01:
            
            segs_excluded.append(existing_segments[s])
            
            #print('Segment '+str(s)+' forbidden, red_cost = '+str(prob.solution.get_reduced_costs("segment_leaf_"+str(s)+"_"+str(leaf))))
            
            #print(existing_segments[s])
            
        else:
            
            m=0
            
            #print('Not excluded',existing_segments[s],float(prob.solution.get_reduced_costs("segment_leaf_"+str(s)+"_"+str(leaf))))
                        
    pricing_prob = construct_pricing_problem2(depth,prob,rows_to_be_excluded,rows_to_be_included,leaf,[])
                
    pricing_prob.solve()
    
    try:
            
        obj_value = pricing_prob.solution.get_objective_value()
            
        obj_value = obj_value + prob.solution.get_dual_values("constraint_6_" + str(leaf))
        
        #obj_value = obj_value + sum([prob.solution.get_dual_values("branch_f_"+str(i)+"_"+str(j)) for (i,j) in branched_f])
        
        #print("Bheta "+str(leaf)+" :"+str(prob.solution.get_dual_values()[constraint_indicators[3] + leaf]))
        
        segment = extract_rows_pricing(pricing_prob)
        
    except:
            
        segment, obj_value = [], float('-inf')
        
    return segment, obj_value




def solve_pricing_all_at_once(depth,prob,branch_var,branch_index,ID,existing_segments):
    
    rows_to_be_excluded, rows_to_be_included, segs_excluded = [[] for l in range(len(existing_segments))], [[] for l in range(len(existing_segments))], [[] for l in range(len(existing_segments))]
        
    for v in range(len(branch_var)):
        
        if branch_var[v] == 'row_leaf':
        
            leaf = branch_index[v][1]
                
            if ID[v] == '1':
                
                rows_to_be_included[leaf].append(branch_index[v][0])
                
            else:
                
                rows_to_be_excluded[leaf].append(branch_index[v][0])
                
    #input()
    
    for l in range(len(existing_segments)):
    
        for s in range(len(existing_segments[l])):
            
            if float(prob.solution.get_reduced_costs("segment_leaf_"+str(s)+"_"+str(l))) >= 0.01 or float(prob.solution.get_reduced_costs("segment_leaf_"+str(s)+"_"+str(l))) <= -0.01:
                
                segs_excluded[l].append(existing_segments[l][s])
                
                #print('Segment '+str(s)+' forbidden, red_cost = '+str(prob.solution.get_reduced_costs("segment_leaf_"+str(s)+"_"+str(leaf))))
    
    #try:
    
    pricing_prob_all_at_once = contruct_pricing_problem_all_at_once2(depth,prob,rows_to_be_excluded,rows_to_be_included,segs_excluded)
        
    pricing_prob_all_at_once.solve()
            
    obj_value = pricing_prob_all_at_once.solution.get_objective_value()
    
    #print('obj',obj_value)
    
    obj_value = obj_value + sum([prob.solution.get_dual_values("constraint_6_"+str(l)) for l in range(len(existing_segments))])
                
    #print("SUM BHETA ",sum([prob.solution.get_dual_values()[constraint_indicators[3] + leaf] for leaf in range(len(segments_set))]))
            
    segment = extract_rows_pricing_all_at_once(pricing_prob_all_at_once,len(existing_segments))
    
    #display_pricing_all_at_once(depth,pricing_prob_all_at_once)
        
    #except:
        
        #segment, obj_value = [[] for l in range(len(existing_segments))], float('inf')
        
    return segment, obj_value





def solve_pricing(depth,prob,segments_set,branch_var,branch_index,ID,pricing_method): #return a triple (segments_to_be_added, convergence, min(red_cost))
    
    from BaP_Node import count_iter
    
    num_leafs = len(segments_set)
        
    segments_to_be_added, obj_values, segments_to_be_added_ordered = [], [], []
    
    if pricing_method==1:
    
        for l in range(num_leafs): # TODO ; implement new pricing_method
            
            segments, value = solve_pricing_given_leaf(depth,prob,l,branch_var,branch_index,ID,segments_set[l])
            
            segments_to_be_added_ordered.append(segments)
            
            obj_values.append(value)
            
            if value < 500:
            
                plt.scatter(count_iter,value,color=color_leaf(l))
            
                plt.pause(0.01)
                        
            print("Reduced cost for leaf "+str(l)+" :",str(value))
            
            #print(segments)
            
    elif pricing_method==2:
                
        excl_rows, remember_order = [], []
        
        shuffle_leaves=range(num_leafs)
        
        shuffle(shuffle_leaves)
        
        for l in range(num_leafs):
            
            true_l=shuffle_leaves[l]
            
            if l!=num_leafs-1:
                
                segment, value = solve_pricing_given_leaf(depth,prob,l,branch_var,branch_index,ID,segments_set[l])
            
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
        
        segments, value = solve_pricing_all_at_once(depth,prob,branch_var,branch_index,ID,segments_set)
            
        segments_to_be_added_ordered = segments
        
        obj_values.append(value)
        
        plt.scatter(count_iter,value,color='k')
        
        plt.pause(0.01)
        
        #print(prob.solution.get_dual_values(),segments)
                    
        print("Reduced cost for partition : ",str(value))
        
    elif pricing_method==4:
        
        l = 1
                
        segments, value = solve_pricing_given_leaf(depth,prob,l,branch_var,branch_index,ID,segments_set[l])
        
        segments_to_be_added_ordered.append(segments)
        
        obj_values.append(value)
        
        if value > -200:
        
            plt.scatter(count_iter,value,color=color_leaf(l))
        
            plt.pause(0.01)
                    
        print("Reduced cost for leaf "+str(l)+" :",str(value))
        
        segments_to_be_added_ordered.append([])
        
        #print(segments)
                                
    return segments_to_be_added_ordered, ((max(obj_values) < 0.01) and (pricing_method==1)), max(obj_values)

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