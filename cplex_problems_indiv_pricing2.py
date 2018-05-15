# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 09:58:57 2018

@author: Guillaume
"""

from learn_tree_funcs import get_left_leafs, get_right_leafs, get_num_targets, get_data_size, get_target, get_path, get_num_features, get_depth
import cplex

DEPTH_CONSTRAINTS = 1

def obtain_TARGETS3(t):
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
    
    data_size=get_data_size()
    
    # constraint to prevent the generated segment from being emtpty
    
    col_names = ["row_"+str(r) for r in range(data_size)]
    
    col_values = [-1 for r in range(data_size)]
    
    row_names.append("constraint_entire_set")

    row_values.append([col_names,col_values])

    row_right_sides.append(-1)

    row_senses = row_senses + "L"

    row_value = row_value + 1
    
    # constraint to prevent the pricing from giving existing segments as output
    
    for s in range(len(existing_segments)):
        
        col_names, col_values = [], []
        
        for r in range(data_size):
            
            if r in existing_segments[s]:
        
                col_names.extend(["row_"+str(r)])
        
                col_values.extend([1])
                
            else:
                
                col_names.extend(["row_"+str(r)])
        
                col_values.extend([-1])               
                    
        row_names.append("constraint_segment_"+str(s))
    
        row_values.append([col_names,col_values])
    
        row_right_sides.append(len(existing_segments[s]) - 1)
    
        row_senses = row_senses + "L"
    
        row_value = row_value + 1
    
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
        
        col_values = [-1 for r in incl_rows]
        
        row_names.append("constraint_branching_1")
    
        row_values.append([col_names,col_values])
    
        row_right_sides.append(-len(incl_rows))
    
        row_senses = row_senses + "L"
    
        row_value = row_value + 1
        
    return row_names, row_values, row_right_sides, row_senses
    

def construct_pricing_problem2(depth,master_prob,exc_rows,incl_rows,leaf,existing_segments):
    
    global TARGETS
    
    prob = cplex.Cplex()
    
    prob.objective.set_sense(prob.objective.sense.maximize)

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