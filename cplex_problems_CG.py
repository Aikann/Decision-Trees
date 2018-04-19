# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 15:36:08 2018

@author: Guillaume
"""

from learn_tree_funcs import get_num_targets, get_left_leafs, get_right_leafs
from learn_tree_funcs import get_num_features, get_data_size, get_min_value, get_max_value, get_feature_value, get_target
import cplex
from cplex.exceptions import CplexError

def obtain_TARGETS(t):
    global TARGETS
    TARGETS=t
    
def add_variable_to_master_and_rebuild(prob,inputdepth,prev_segments_set,segments_to_add,segments_set):
    
    global VARS
            
    try:
        
        value=prob.variables.get_num()
        
        var_types, var_lb, var_ub, var_obj = "", [], [], []
        
        for leaf in range(len(prev_segments_set)):

            VARS["segment_leaf_" + str(len(prev_segments_set[leaf])) + "_" + str(leaf)] = value
        
            var_types += "C"
        
            var_lb.append(0)
        
            var_ub.append(1)
        
            var_obj.append(0)
            
            value=value+1
                        
        prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types)#, names = var_names)

        row_names, row_values, row_right_sides, row_senses = create_rows_CG(inputdepth,segments_set)
        
        prob.linear_constraints.delete()
        
        prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
        
        prob.set_problem_type(0)
                                        
    except CplexError, exc:

        print exc
        
        return []
    
    return prob

def create_variables_CG(depth,segments_set):
    
    global VARS

    VARS={}

    var_value = 0

    var_names = []

    var_types = ""

    var_lb = []

    var_ub = []

    var_obj = []

    num_features = get_num_features()

    data_size = get_data_size()

    num_leafs = 2**depth

    num_nodes = num_leafs-1

    # node n had a boolean test on feature f, boolean. On the paper: f_{i,j}

    for j in range(num_nodes):

        for i in range(num_features):

            VARS["node_feature_" + str(j) + "_" + str(i)] = var_value

            var_names.append("#" + str(var_value))

            var_types = var_types + "C"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1

    # value used in the boolean test in node n, integer. On the paper: c_{j}

    for j in range(num_nodes):

        VARS["node_constant_" + str(j)] = var_value

        var_names.append("#" + str(var_value))

        var_types = var_types + "C"

        var_lb.append(get_min_value())

        var_ub.append(get_max_value())

        var_obj.append(0)

        var_value = var_value + 1

    # leaf l predicts type t, boolean. On the paper: p_{l,t}
    
    for l in range(num_leafs):

        for t in range(get_num_targets()):

            VARS["prediction_type_" + str(t) + "_" + str(l)] = var_value

            var_names.append("#" + str(var_value))

            var_types = var_types + "C"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1
            
    # row error, variables to minimize. On the paper: e_{r}

    for r in range(data_size):

        VARS["row_error_" + str(r)] = var_value

        var_names.append("#" + str(var_value))

        var_types = var_types + "C"

        var_lb.append(0)

        var_ub.append(1)

        var_obj.append(1)

        var_value = var_value + 1
        
    for l in range(num_leafs): # x_{l,s}
    
        for s in range(len(segments_set[l])): 
        
            VARS["segment_leaf_" + str(s) + "_" + str(l)] = var_value

            var_names.append("#" + str(var_value))

            var_types = var_types + "C"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1

    return VARS, var_names, var_types, var_lb, var_ub, var_obj


def create_rows_CG(depth,segments_set):

    global VARS
    global TARGETS
    global constraint_indicators
    
    constraint_indicators=[]

    row_value = 0

    row_names = []

    row_values = []

    row_right_sides = []

    row_senses = ""

    num_features = get_num_features()

    data_size = get_data_size()

    num_leafs = 2**depth

    num_nodes = num_leafs-1
        
    big_M = get_max_value() - get_min_value()
    
    big_M=10*big_M + 10
    
    constraint_indicators.append(row_value)
    
    for i in range(num_features): #constraint (15), indicator 0

        for j in range(num_nodes):
            
            for l in get_left_leafs(j, num_nodes):

                col_names = [VARS["segment_leaf_"  + str(s) + "_" + str(l)] for s in range(len(segments_set[l]))] #x_{l,s}

                col_values = [max([get_feature_value(r,i) for r in s]) for s in segments_set[l]] #mu^{i,s} max

                col_names.extend([VARS["node_feature_" + str(j) + "_" + str(i)], VARS["node_constant_" + str(j)]])
                
                col_values.extend([big_M, -1])

                row_names.append("#" + str(row_value))
        
                row_values.append([col_names,col_values])
        
                row_right_sides.append(big_M)
        
                row_senses = row_senses + "L"
        
                row_value = row_value + 1
                
    constraint_indicators.append(row_value)
            
    for i in range(num_features): #constraint (16), indicator 1

        for j in range(num_nodes):
            
            for l in get_right_leafs(j, num_nodes):

                col_names = [VARS["segment_leaf_"  + str(s) + "_" + str(l)] for s in range(len(segments_set[l]))] #x_{l,s}

                col_values = [-min([get_feature_value(r,i) for r in s]) for s in segments_set[l]] #mu^{i,s} min

                col_names.extend([VARS["node_feature_" + str(j) + "_" + str(i)], VARS["node_constant_" + str(j)]])
                
                col_values.extend([big_M, 1])

                row_names.append("#" + str(row_value))
        
                row_values.append([col_names,col_values])
        
                row_right_sides.append(big_M)
        
                row_senses = row_senses + "L"
        
                row_value = row_value + 1
                
    constraint_indicators.append(row_value)
                
    for r in range(data_size): #constraint (17), indicator 2
        
        col_names, col_values = [], []
        
        for l in range(num_leafs):
            
            for s in range(len(segments_set[l])):
                
                if r in segments_set[l][s]:
        
                    col_names.extend([VARS["segment_leaf_"  + str(s) + "_" + str(l)]]) #x_{l,s}
                    
                    col_values.extend([1])
                    
        row_names.append("#" + str(row_value))
        
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    constraint_indicators.append(row_value)
        
    for l in range(num_leafs): #constraint (18), indicator 3
        
        col_names = [VARS["segment_leaf_"  + str(s) + "_" + str(l)] for s in range(len(segments_set[l]))] #x_{l,s}
        
        col_values = [1 for s in range(len(segments_set[l]))] #x_{l,s}
        
        row_names.append("#" + str(row_value))
        
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    constraint_indicators.append(row_value)
        
    for r in range(data_size): #constraint (19), indicator 4
        
        for l in range(num_leafs):
            
            col_names, col_values = [], []
            
            for s in range(len(segments_set[l])):
                
                if r in segments_set[l][s]:
            
                    col_names.extend([VARS["segment_leaf_"  + str(s) + "_" + str(l)]]) #x_{l,s}
                    
                    col_values.extend([1])
                    
            for t in range(get_num_targets()):
                
                if TARGETS[t] != get_target(r):

                    col_names.extend([VARS["prediction_type_" + str(t) + "_" + str(l)]])

                    col_values.extend([1])

            col_names.extend([VARS["row_error_" + str(r)]])

            col_values.extend([-1])
            
            row_names.append("#" + str(row_value))
        
            row_values.append([col_names,col_values])
    
            row_right_sides.append(1)
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1
            
    constraint_indicators.append(row_value)
            
    for l in range(num_leafs): #constraint (20), indicator 5

        col_names = [VARS["prediction_type_" + str(s) + "_" + str(l)] for s in range(get_num_targets())]

        col_values = [1 for s in range(get_num_targets())]

        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    constraint_indicators.append(row_value)

    for j in range(num_nodes): #constraint (21), indicator 6

        col_names = [VARS["node_feature_" + str(j) + "_" + str(i)] for i in range(num_features)]

        col_values = [1 for i in range(num_features)]

        row_names.append("#"+str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
                
    return row_names, row_values, row_right_sides, row_senses


def construct_master_problem(depth,segments_set):
    
    global VARS
    global TARGETS
    
    prob = cplex.Cplex()
    
    try:

        prob.objective.set_sense(prob.objective.sense.minimize)

        VARS, var_names, var_types, var_lb, var_ub, var_obj = create_variables_CG(depth,segments_set)
        
        prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types)#, names = var_names)

        row_names, row_values, row_right_sides, row_senses = create_rows_CG(depth,segments_set)
        
        prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
                
        prob.set_problem_type(0) #tell cplex this is a LP, not a MILP
        
        prob.set_log_stream(None)
        prob.set_error_stream(None)
        prob.set_warning_stream(None)
        prob.set_results_stream(None)
        
    except CplexError, exc:

        print exc

        return []
    
    return prob

def create_variables_pricing(depth,master_prob,leaf):
    
    global VARS2

    VARS2={}

    var_value = 0

    var_names = []

    var_types = ""

    var_lb = []

    var_ub = []

    var_obj = []

    num_features = get_num_features()

    data_size = get_data_size()

    num_leafs = 2**depth

    num_nodes = num_leafs-1
    
    duals = master_prob.solution.get_dual_values()
    
    #compute useful sums of dual values
    
    A_i_l, B_i_l = [], []
    
    for i in range(num_features):
        
        s=0
        
        for j in range(num_nodes):
            
            left_leaves = get_left_leafs(j,num_nodes)
            
            if leaf in left_leaves:
                
                idx = left_leaves.index(leaf)
                
                s = s + duals[i*(num_nodes*len(left_leaves)) + j*len(left_leaves) + idx]
                
            #print(s)
            
            if s<0:
                
                input()
                
        A_i_l.append(-s)
    
    for i in range(num_features):
        
        s=0
        
        for j in range(num_nodes):
            
            right_leaves = get_right_leafs(j,num_nodes)
            
            if leaf in right_leaves:
                
                idx = right_leaves.index(leaf)
                
                s = s + duals[constraint_indicators[1] + i*(num_nodes*len(right_leaves)) + j*len(right_leaves) + idx]
                
            #print(s)
            
            if s<0:
                
                input()
                
        B_i_l.append(s)

    # z_{r}, main decision variables

    for r in range(data_size):

        VARS2["row_" + str(r)] = var_value

        var_names.append("#" + str(var_value))

        var_types = var_types + "B"

        var_lb.append(0)

        var_ub.append(1)
        
        #print(r,leaf,"C_{r,l} ",duals[constraint_indicators[2] + r] + duals[constraint_indicators[4] + r*num_leafs + leaf])
        
        var_obj.append(duals[constraint_indicators[2] + r] + duals[constraint_indicators[4] + r*num_leafs + leaf])

        var_value = var_value + 1
        
    # kappa_{i,r}, indicate the min feature of row r
    
    for i in range(num_features):
        
        for r in range(data_size):

            VARS2["kappa_" + str(r) + "_" + str(i)] = var_value
        
            var_names.append("#" + str(var_value))
        
            var_types = var_types + "B"
        
            var_lb.append(0)
        
            var_ub.append(1)
        
            var_obj.append(-B_i_l[i]*get_feature_value(r,i))
        
            var_value = var_value + 1
        
    # omega_{i,r}, indicate the max feature of row r
    
    for i in range(num_features):
        
        for r in range(data_size):

            VARS2["omega_" + str(r) + "_" + str(i)] = var_value
        
            var_names.append("#" + str(var_value))
        
            var_types = var_types + "B"
        
            var_lb.append(0)
        
            var_ub.append(1)
        
            var_obj.append(A_i_l[i]*get_feature_value(r,i))
        
            var_value = var_value + 1
            
    return VARS2, var_names, var_types, var_lb, var_ub, var_obj
            
            
def create_rows_pricing(depth,exc_rows,incl_rows,existing_segments):
    
    row_value = 0

    row_names = []

    row_values = []

    row_right_sides = []

    row_senses = ""

    num_features = get_num_features()

    data_size = get_data_size()
    
    for r in range(data_size): #constraint (32)
        
        for i in range(num_features):

            col_names = [VARS2["kappa_"  + str(r) + "_" + str(i)]]
    
            col_values = [1]
            
            for r2 in range(data_size):
                
                if get_feature_value(r2,i) < get_feature_value(r,i):
                    
                    col_names.extend([VARS2["row_" + str(r2)]])
                    
                    col_values.extend([1./data_size])
    
        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "L"

        row_value = row_value + 1
     
    for r in range(data_size): #constraint (33)
        
        for i in range(num_features):
            
            col_names = [VARS2["omega_"  + str(r) + "_" + str(i)]]
    
            col_values = [1]
            
            for r2 in range(data_size):
                
                if get_feature_value(r2,i) > get_feature_value(r,i):
                    
                    col_names.extend([VARS2["row_" + str(r2)]])
                    
                    col_values.extend([1./data_size])
    
        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "L"

        row_value = row_value + 1
        
    for r in range(data_size): #constraint (34)
        
        col_names = [VARS2["kappa_"  + str(r) + "_" + str(i)] for i in range(num_features)]
        
        col_values = [1 for i in range(num_features)]
        
        col_names.extend([VARS2["row_"+str(r)]])
        
        col_values.extend([-1])
        
        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(0)

        row_senses = row_senses + "L"

        row_value = row_value + 1
        
    for r in range(data_size): #constraint (35)
        
        col_names = [VARS2["omega_"  + str(r) + "_" + str(i)] for i in range(num_features)]
        
        col_values = [1 for i in range(num_features)]
        
        col_names.extend([VARS2["row_"+str(r)]])
        
        col_values.extend([-1])
        
        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(0)

        row_senses = row_senses + "L"

        row_value = row_value + 1     
        
    for i in range(num_features): #constraint (36)
        
        col_names = [VARS2["kappa_"  + str(r) + "_" + str(i)] for r in range(data_size)]
        
        col_values = [1 for r in range(data_size)]
        
        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
        
    for i in range(num_features): #constraint (37)
        
        col_names = [VARS2["omega_"  + str(r) + "_" + str(i)] for r in range(data_size)]
        
        col_values = [1 for r in range(data_size)]
        
        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    # constraint to prevent the generated segment to be the entire set
    
    col_names = [VARS2["row_"+str(r)] for r in range(data_size)]
    
    col_values = [1 for r in range(data_size)]
    
    row_names.append("#" + str(row_value))

    row_values.append([col_names,col_values])

    row_right_sides.append(data_size-1)

    row_senses = row_senses + "L"

    row_value = row_value + 1
        
    
    """
    # constraints to prevent the pricing from generating existing segments
       
    for s in existing_segments:
        
        col_names, col_values = [], []
        
        for r in range(data_size):
            
            col_names.extend([VARS2["row_" + str(r)]])
                        
            if r in s:
                
                col_values.extend([1])
                
            else:
                
                col_values.extend([-1])
                
        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(len(s)-1)

        row_senses = row_senses + "L"

        row_value = row_value + 1
    """
    
        
    #branching constraint (0)
    
    if len(exc_rows) > 0:
        
        col_names = [VARS2["row_"  + str(r)] for r in exc_rows]
        
        col_values = [1 for r in exc_rows]
        
        row_names.append("#" + str(row_value))
    
        row_values.append([col_names,col_values])
    
        row_right_sides.append(0)
    
        row_senses = row_senses + "L"
    
        row_value = row_value + 1
    
    #branching constraint (1)
    
    if len(incl_rows) > 0:
    
        col_names = [VARS2["row_"  + str(r)] for r in incl_rows]
        
        col_values = [1 for r in exc_rows]
        
        row_names.append("#" + str(row_value))
    
        row_values.append([col_names,col_values])
    
        row_right_sides.append(len(incl_rows))
    
        row_senses = row_senses + "R"
    
        row_value = row_value + 1
        
        
        
    return row_names, row_values, row_right_sides, row_senses
    

def construct_pricing_problem(depth,master_prob,exc_rows,incl_rows,leaf,existing_segments):
    
    global VARS
    global TARGETS
    global VARS2
    
    prob = cplex.Cplex()
    
    try:

        prob.objective.set_sense(prob.objective.sense.minimize)

        VARS2, var_names, var_types, var_lb, var_ub, var_obj = create_variables_pricing(depth,master_prob,leaf)
                        
        prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types)#, names = var_names)

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
        
    except CplexError, exc:

        print exc
        
        return []
    
    return prob

def create_variables_pricing_all_at_once(depth,master_prob):
    
    global VARS3

    VARS3={}

    var_value = 0

    var_names = []

    var_types = ""

    var_lb = []

    var_ub = []

    var_obj = []

    num_features = get_num_features()

    data_size = get_data_size()

    num_leafs = 2**depth

    num_nodes = num_leafs-1
    
    duals = master_prob.solution.get_dual_values()
    
    #compute useful sums of dual values
    
    A_i_l, B_i_l = [[] for l in range(num_leafs)], [[] for l in range(num_leafs)]
    
    for leaf in range(num_leafs):
    
        for i in range(num_features):
            
            s=0
            
            for j in range(num_nodes):
                
                left_leaves = get_left_leafs(j,num_nodes)
                
                if leaf in left_leaves:
                    
                    idx = left_leaves.index(leaf)
                    
                    s = s + duals[i*(num_nodes*len(left_leaves)) + j*len(left_leaves) + idx]
                    
                #print(s)
                
                if s<0:
                    
                    input()
                    
            A_i_l[leaf].append(-s)
        
        for i in range(num_features):
            
            s=0
            
            for j in range(num_nodes):
                
                right_leaves = get_right_leafs(j,num_nodes)
                
                if leaf in right_leaves:
                    
                    idx = right_leaves.index(leaf)
                    
                    s = s + duals[constraint_indicators[1] + i*(num_nodes*len(right_leaves)) + j*len(right_leaves) + idx]
                    
                #print(s)
                
                if s<0:
                    
                    input()
                    
            B_i_l[leaf].append(s)

    # z_{r,l}, main decision variables
    
    for leaf in range(num_leafs):

        for r in range(data_size):
    
            VARS3["row_" + str(leaf) + "_" + str(r)] = var_value
    
            var_names.append("#" + str(var_value))
    
            var_types = var_types + "B"
    
            var_lb.append(0)
    
            var_ub.append(1)
            
            #print(r,leaf,"C_{r,l} ",duals[constraint_indicators[2] + r] + duals[constraint_indicators[4] + r*num_leafs + leaf])
            
            var_obj.append(duals[constraint_indicators[2] + r] + duals[constraint_indicators[4] + r*num_leafs + leaf])
    
            var_value = var_value + 1
        
    # kappa_{i,r,l}, indicate the min feature of row r
    
    for leaf in range(num_leafs):
    
        for i in range(num_features):
            
            for r in range(data_size):
    
                VARS3["kappa_" +str(leaf) + "_" + str(r) + "_" + str(i)] = var_value
            
                var_names.append("#" + str(var_value))
            
                var_types = var_types + "B"
            
                var_lb.append(0)
            
                var_ub.append(1)
            
                var_obj.append(-B_i_l[leaf][i]*get_feature_value(r,i))
            
                var_value = var_value + 1
        
    # omega_{i,r,l}, indicate the max feature of row r
    
    for leaf in range(num_leafs):
    
        for i in range(num_features):
            
            for r in range(data_size):
    
                VARS3["omega_" + str(leaf) + "_" + str(r) + "_" + str(i)] = var_value
            
                var_names.append("#" + str(var_value))
            
                var_types = var_types + "B"
            
                var_lb.append(0)
            
                var_ub.append(1)
            
                var_obj.append(A_i_l[leaf][i]*get_feature_value(r,i))
            
                var_value = var_value + 1
            
    return VARS3, var_names, var_types, var_lb, var_ub, var_obj



def create_rows_pricing_all_at_once(depth,branched_rows,branched_leaves,ID,existing_segments):
    
    row_value = 0

    row_names = []

    row_values = []

    row_right_sides = []

    row_senses = ""

    num_features = get_num_features()

    data_size = get_data_size()
    
    num_leafs = 2**depth
    
    for l in range(num_leafs):
    
        for r in range(data_size): #constraint (32)
            
            for i in range(num_features):
    
                col_names = [VARS3["kappa_" + str(l) + "_"  + str(r) + "_" + str(i)]]
        
                col_values = [1]
                
                for r2 in range(data_size):
                    
                    if get_feature_value(r2,i) < get_feature_value(r,i):
                        
                        col_names.extend([VARS3["row_" +str(l) + "_" + str(r2)]])
                        
                        col_values.extend([1./data_size])
        
            row_names.append("#" + str(row_value))
    
            row_values.append([col_names,col_values])
    
            row_right_sides.append(1)
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1
            
    for l in range(num_leafs):
     
        for r in range(data_size): #constraint (33)
            
            for i in range(num_features):
                
                col_names = [VARS3["omega_" + str(l) + "_" + str(r) + "_" + str(i)]]
        
                col_values = [1]
                
                for r2 in range(data_size):
                    
                    if get_feature_value(r2,i) > get_feature_value(r,i):
                        
                        col_names.extend([VARS3["row_" + str(l) + "_" + str(r2)]])
                        
                        col_values.extend([1./data_size])
        
            row_names.append("#" + str(row_value))
    
            row_values.append([col_names,col_values])
    
            row_right_sides.append(1)
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1
            
    for l in range(num_leafs):
        
        for r in range(data_size): #constraint (34)
            
            col_names = [VARS3["kappa_" + str(l) + "_"  + str(r) + "_" + str(i)] for i in range(num_features)]
            
            col_values = [1 for i in range(num_features)]
            
            col_names.extend([VARS3["row_" + str(l) + "_" + str(r)]])
            
            col_values.extend([-1])
            
            row_names.append("#" + str(row_value))
    
            row_values.append([col_names,col_values])
    
            row_right_sides.append(0)
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1
            
    for l in range(num_leafs):
        
        for r in range(data_size): #constraint (35)
            
            col_names = [VARS3["omega_" + str(l) + "_" + str(r) + "_" + str(i)] for i in range(num_features)]
            
            col_values = [1 for i in range(num_features)]
            
            col_names.extend([VARS3["row_" + str(l) + "_" + str(r)]])
            
            col_values.extend([-1])
            
            row_names.append("#" + str(row_value))
    
            row_values.append([col_names,col_values])
    
            row_right_sides.append(0)
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1     
            
    for l in range(num_leafs):
        
        for i in range(num_features): #constraint (36)
            
            col_names = [VARS3["kappa_" + str(l) + "_" + str(r) + "_" + str(i)] for r in range(data_size)]
            
            col_values = [1 for r in range(data_size)]
            
            row_names.append("#" + str(row_value))
    
            row_values.append([col_names,col_values])
    
            row_right_sides.append(1)
    
            row_senses = row_senses + "E"
    
            row_value = row_value + 1
        
    for l in range(num_leafs):
        
        for i in range(num_features): #constraint (37)
            
            col_names = [VARS3["omega_" + str(l) + "_" + str(r) + "_" + str(i)] for r in range(data_size)]
            
            col_values = [1 for r in range(data_size)]
            
            row_names.append("#" + str(row_value))
    
            row_values.append([col_names,col_values])
    
            row_right_sides.append(1)
    
            row_senses = row_senses + "E"
    
            row_value = row_value + 1
            
    for r in range(data_size): #new contraint for "all at once" pricing problem
        
        col_names = [VARS3["row_" + str(l) + "_" + str(r)] for l in range(num_leafs)]
        
        col_values = [1 for l in range(num_leafs)]
        
        row_names.append("#" + str(row_value))
    
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
    
    """
        
    # constraints to prevent the pricing from generating existing segments
       
    for s in existing_segments:
        
        col_names, col_values = [], []
        
        for r in range(data_size):
            
            col_names.extend([VARS2["row_" + str(r)]])
                        
            if r in s:
                
                col_values.extend([1])
                
            else:
                
                col_values.extend([-1])
                
        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(len(s)-1)

        row_senses = row_senses + "L"

        row_value = row_value + 1
        
    """
        
    #branching constraints
    
    for k in range(len(branched_rows)):
        
        r, l = branched_rows[k], branched_leaves[k]
        
        col_names = [VARS3["row_" + str(l) + "_" + str(r)]]
        
        col_values = [1]
        
        row_names.append("#" + str(row_value))
    
        row_values.append([col_names,col_values])
        
        if ID[k]==0:
    
            row_right_sides.append(0)
            
        else:
            
            row_right_sides.append(1)
    
        row_senses = row_senses + "E"
    
        row_value = row_value + 1
    
    return row_names, row_values, row_right_sides, row_senses



def contruct_pricing_problem_all_at_once(depth,master_prob,branched_rows,branched_leaves,ID,existing_segments):
    
    global VARS3
    global TARGETS
    
    prob = cplex.Cplex()
    
    try:

        prob.objective.set_sense(prob.objective.sense.minimize)

        VARS3, var_names, var_types, var_lb, var_ub, var_obj = create_variables_pricing_all_at_once(depth,master_prob)
                
        prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types)#, names = var_names)

        row_names, row_values, row_right_sides, row_senses = create_rows_pricing_all_at_once(depth,branched_rows,branched_leaves,ID,existing_segments)
        
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
        
    except CplexError, exc:

        print exc

        return []
    
    return prob