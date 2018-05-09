# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 09:58:57 2018

@author: Guillaume
"""

from learn_tree_funcs import get_left_leafs, get_right_leafs, get_num_targets, get_target, get_depth
from learn_tree_funcs import get_num_features, get_data_size, get_feature_value, get_max_value, get_min_value
import cplex

DEPTH_CONSTRAINTS = 0

def obtain_TARGETS4(t):
    global TARGETS
    TARGETS=t

def compute_C(depth,r,l,master_prob):
    
    num_leafs = 2**depth

    num_nodes = num_leafs-1
            
    C = master_prob.solution.get_dual_values("constraint_5_" + str(r)) #theta
    
    if not DEPTH_CONSTRAINTS:
    
        for i in range(get_num_features()):
        
            for j in range(num_nodes):
                
                if l in get_left_leafs(j,num_nodes):
                
                    C = C + master_prob.solution.get_dual_values("constraint_2_" + str(i) + "_" + str(j) + "_" +str(r))
                    
                elif l in get_right_leafs(j,num_nodes):
                    
                    C = C + master_prob.solution.get_dual_values("constraint_3_" + str(i) + "_" + str(j) + "_" +str(r))
                    
    else:
        
        C = C + master_prob.solution.get_dual_values("constraint_depth_leaf_"+str(l)+"_"+str(r))
        
        for j in range(num_nodes):
            
            if get_depth(j,num_nodes) != 1:
            
                C = C + master_prob.solution.get_dual_values("constraint_depth_node_"+str(j)+"_"+str(r))
                                                            
    for t in range(get_num_targets()):
        
        if TARGETS[t] != get_target(r):
        
            C = C + master_prob.solution.get_dual_values("constraint_4_" + str(l) + "_" +str(t)) # gamma leaf
            
    C = C + master_prob.solution.get_dual_values("constraint_4bis_" + str(r) + "_" +str(l)) # gamma row
                
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
            
            
def create_rows_pricing_all_at_once(depth,exc_rows,incl_rows,existing_segments):
    
    row_value = 0

    row_names = []

    row_values = []

    row_right_sides = []

    row_senses = ""
    
    data_size = get_data_size()
    
    num_leafs = 2**depth
    
    # at least one row per leaf constraint
    
    for l in range(num_leafs):
        
        col_names = ["row_" + str(l) + "_" + str(r) for r in range(data_size)]
        
        col_values = [-1 for r in range(data_size)]
        
        row_names.append("constraint_atleastonerow_"+str(l))
    
        row_values.append([col_names,col_values])

        row_right_sides.append(-1)

        row_senses = row_senses + "L"

        row_value = row_value + 1
    
    #partition constraint
    
    for r in range(data_size): #new contraint for "all at once" pricing problem
        
        col_names = ["row_" + str(l) + "_" + str(r) for l in range(num_leafs)]
        
        col_values = [1 for l in range(num_leafs)]
        
        row_names.append("constraint_partition_"+str(r))
    
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
    
    # constraint to prevent the pricing from giving existing segments as output
    
    for l in range(num_leafs):
    
        for s in range(len(existing_segments[l])):
            
            col_names, col_values = [], []
            
            for r in range(data_size):
                
                if r in existing_segments[l][s]:
            
                    col_names.extend(["row_"+str(l)+"_"+str(r)])
            
                    col_values.extend([1])
                    
                else:
                    
                    col_names.extend(["row_"+str(l)+"_"+str(r)])
            
                    col_values.extend([-1])               
                        
            row_names.append("constraint_segment_"+str(s)+"_"+str(l))
        
            row_values.append([col_names,col_values])
        
            row_right_sides.append(len(existing_segments[l][s]) - 1)
        
            row_senses = row_senses + "L"
        
            row_value = row_value + 1
            
    for l in range(num_leafs):
            
        #branching constraint (0)
        
        if len(exc_rows[l]) > 0:
            
            col_names = ["row_"+str(l)+"_"+str(r) for r in exc_rows[l]]
            
            col_values = [1 for r in exc_rows[l]]
            
            row_names.append("constraint_branching_0_leaf"+str(l))
        
            row_values.append([col_names,col_values])
        
            row_right_sides.append(0)
        
            row_senses = row_senses + "L"
        
            row_value = row_value + 1
        
        #branching constraint (1)
        
        if len(incl_rows[l]) > 0:
        
            col_names = ["row_"+str(l)+"_"+str(r) for r in incl_rows[l]]
            
            col_values = [-1 for r in incl_rows[l]]
            
            row_names.append("constraint_branching_1_leaf"+str(l))
        
            row_values.append([col_names,col_values])
        
            row_right_sides.append(-len(incl_rows[l]))
        
            row_senses = row_senses + "L"
        
            row_value = row_value + 1
        
    return row_names, row_values, row_right_sides, row_senses
    

def contruct_pricing_problem_all_at_once2(depth,master_prob,exc_rows,incl_rows,existing_segments):
    
    global TARGETS
    
    prob = cplex.Cplex()
    
    prob.objective.set_sense(prob.objective.sense.maximize)

    var_names, var_types, var_lb, var_ub, var_obj = create_variables_pricing_all_at_once(depth,master_prob)
                    
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, names = var_names)
    
    row_names, row_values, row_right_sides, row_senses = create_rows_pricing_all_at_once(depth,exc_rows,incl_rows,existing_segments)
    
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