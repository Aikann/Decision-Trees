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

def create_variables_pricing(depth,master_prob,leaf):
    
    var_value = 0

    var_names = []

    var_types = ""

    var_lb = []

    var_ub = []

    var_obj = []

    data_size = get_data_size()
        
    # z_{r}, main decision variables

    for r in range(data_size):

        var_names.append("row_" + str(r))

        var_types = var_types + "B"

        var_lb.append(0)

        var_ub.append(1)
                
        var_obj.append(compute_C(depth,r,leaf,master_prob))

        var_value = var_value + 1
            
    return var_names, var_types, var_lb, var_ub, var_obj
            
            
def create_rows_pricing(depth,exc_rows,incl_rows,existing_segments):
    
    row_value = 0

    row_names = []

    row_values = []

    row_right_sides = []

    row_senses = ""
    
    #branching constraint (0)
    
    if len(exc_rows) > 0:
        
        col_names = ["row_"  + str(r) for r in exc_rows]
        
        col_values = [1 for r in exc_rows]
        
        row_names.append("constraint_branching_0")
    
        row_values.append([col_names,col_values])
    
        row_right_sides.append(0)
    
        row_senses = row_senses + "L"
    
        row_value = row_value + 1
    
    #branching constraint (1)
    
    if len(incl_rows) > 0:
    
        col_names = ["row_"  + str(r) for r in incl_rows]
        
        col_values = [1 for r in exc_rows]
        
        row_names.append("constraint_branching_1")
    
        row_values.append([col_names,col_values])
    
        row_right_sides.append(len(incl_rows))
    
        row_senses = row_senses + "R"
    
        row_value = row_value + 1
        
    return row_names, row_values, row_right_sides, row_senses
    

def construct_pricing_problem2(depth,master_prob,exc_rows,incl_rows,leaf,existing_segments):
    
    global TARGETS
    
    prob = cplex.Cplex()
    
    prob.objective.set_sense(prob.objective.sense.minimize)

    var_names, var_types, var_lb, var_ub, var_obj = create_variables_pricing(depth,master_prob,leaf)
                    
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, names = var_names)
    
    row_names, row_values, row_right_sides, row_senses = create_rows_pricing(depth,exc_rows,incl_rows,existing_segments)
    
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