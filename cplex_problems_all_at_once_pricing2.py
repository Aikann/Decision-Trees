# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 09:58:57 2018

@author: Guillaume
"""

from learn_tree_funcs import get_left_leafs, get_right_leafs
from learn_tree_funcs import get_num_features, get_data_size, get_feature_value, get_max_value, get_min_value
import cplex

def compute_C(depth,r,l,master_prob):
    
    num_features = get_num_features()

    num_leafs = 2**depth

    num_nodes = num_leafs-1
    
    big_M = get_max_value() - get_min_value()
    
    C=0
    
    for i in range(num_features):
    
        for j in range(num_nodes):
            
            if l in get_left_leafs(j,num_nodes):
                
                C = C + abs(master_prob.solution.get_dual_values("constraint_15_" + str(i) + "_" + str(j) + "_" +str(r)))
                
            elif l in get_right_leafs(j,num_nodes):
                
                C = C + abs(master_prob.solution.get_dual_values("constraint_16_" + str(i) + "_" + str(j) + "_" +str(r)))
                
    C = -big_M*C
    
    C = C + master_prob.solution.get_dual_values("constraint_17_" + str(r))
    
    C = C - abs(master_prob.solution.get_dual_values("constraint_19_" + str(r) + "_" +str(l)))
    
    return C

def create_variables_pricing_all_at_once(depth,master_prob):
    
    var_value = 0

    var_names = []

    var_types = ""

    var_lb = []

    var_ub = []

    var_obj = []

    data_size = get_data_size()
    
    num_leafs = 2**depth
        
    # z_{r,l}, main decision variables
    
    for l in range(num_leafs):

        for r in range(data_size):
    
            var_names.append("row_" + str(l) + "_" + str(r))
    
            var_types = var_types + "B"
    
            var_lb.append(0)
    
            var_ub.append(1)
                    
            var_obj.append(compute_C(depth,r,l,master_prob))
    
            var_value = var_value + 1
            
    return var_names, var_types, var_lb, var_ub, var_obj
            
            
def create_rows_pricing_all_at_once(depth,branched_rows,branched_f,ID,existing_segments):
    
    row_value = 0

    row_names = []

    row_values = []

    row_right_sides = []

    row_senses = ""
    
    data_size = get_data_size()
    
    num_leafs = 2**depth
    
    #partition constraint
    
    for r in range(data_size): #new contraint for "all at once" pricing problem
        
        col_names = ["row_" + str(l) + "_" + str(r) for l in range(num_leafs)]
        
        col_values = [1 for l in range(num_leafs)]
        
        row_names.append("constraint_partition_"+str(r))
    
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
    
    #branching constraints
    
    for k in range(len(branched_rows)):
        
        r, l = branched_rows[k][0], branched_rows[k][1]
        
        col_names = ["row_" + str(l) + "_" + str(r)]
        
        col_values = [1]
        
        row_names.append("constraint_branching_row"+str(r)+"_"+str(l))
    
        row_values.append([col_names,col_values])
        
        if ID[k]=="0":
    
            row_right_sides.append(0)
            
        else:
            
            row_right_sides.append(1)
    
        row_senses = row_senses + "E"
    
        row_value = row_value + 1
        
    return row_names, row_values, row_right_sides, row_senses
    

def contruct_pricing_problem_all_at_once2(depth,master_prob,branched_rows,branched_f,ID,existing_segments):
    
    global TARGETS
    
    prob = cplex.Cplex()
    
    prob.objective.set_sense(prob.objective.sense.minimize)

    var_names, var_types, var_lb, var_ub, var_obj = create_variables_pricing_all_at_once(depth,master_prob)
                    
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, names = var_names)
    
    row_names, row_values, row_right_sides, row_senses = create_rows_pricing_all_at_once(depth,branched_rows,branched_f,ID,existing_segments)
    
    prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
    
    prob.parameters.emphasis.mip.set(1)

    #prob.parameters.advance.set(2)
    
    #prob.parameters.mip.strategy.branch.set(1)
    #prob.parameters.mip.strategy.backtrack.set(1.0)
    #prob.parameters.mip.strategy.nodeselect.set(2)
    prob.parameters.mip.strategy.variableselect.set(-1)
    #prob.parameters.mip.strategy.bbinterval.set(0)
    #prob.parameters.mip.strategy.rinsheur.set(50)
    #prob.parameters.mip.strategy.lbheur.set(1)
    #prob.parameters.mip.strategy.probe.set(3)

    #prob.parameters.preprocessing.presolve.set(1)
                    
    prob.set_log_stream(None)
    prob.set_error_stream(None)
    prob.set_warning_stream(None)
    prob.set_results_stream(None)
    
    return prob