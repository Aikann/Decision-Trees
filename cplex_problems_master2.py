# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 10:05:32 2018

@author: Guillaume
"""

from learn_tree_funcs import get_num_targets, get_left_leafs, get_right_leafs, get_left_node, get_right_node, get_depth, get_path
from learn_tree_funcs import get_num_features, get_data_size, get_min_value, get_max_value, get_feature_value, get_target, get_max_value_f, get_min_value_f
import cplex

def obtain_TARGETS2(t):
    global TARGETS
    TARGETS=t

def add_variable_to_master_and_rebuild2(depth,prob,prev_segments_set,segments_to_add,leaf):
    
    num_features = get_num_features()
    
    data_size = get_data_size()

    num_leafs = 2**depth

    num_nodes = num_leafs-1
                    
    value=prob.variables.get_num()
    
    var_types, var_lb, var_ub, var_obj, var_names = "", [], [], [], []
        
    my_columns = [[[],[]]]
            
    s=segments_to_add
                            
    var_types += "C"

    var_lb.append(0)

    var_ub.append(1)

    var_obj.append(0)
    
    var_names.append("segment_leaf_" + str(len(prev_segments_set)) + "_" + str(leaf))
    
    value=value+1
    
    row_value=0
    
    for i in range(num_features): #constraint (2)
        
        for r in range(data_size):

            for j in range(num_nodes):
                
                if leaf in get_left_leafs(j, num_nodes) and r in s:

                    my_columns[0][0].append("constraint_2_" + str(i) + "_" + str(j) + "_" +str(r))

                    my_columns[0][1].append(get_feature_value(r,i))
                    
                    row_value = row_value + 1
                
    for i in range(num_features): #constraint (3)
        
        for r in range(data_size):

            for j in range(num_nodes):
                
                if leaf in get_right_leafs(j, num_nodes) and r in s:

                    my_columns[0][0].append("constraint_3_" + str(i) + "_" + str(j) + "_" +str(r))

                    my_columns[0][1].append(1)
                    
                    row_value = row_value + 1
                
    for t in range(get_num_targets()): #constraint (4)
        
        for l in range(num_leafs):
            
            if l == leaf:
                        
                my_columns[0][0].append("constraint_4_" + str(leaf) + "_" +str(t))
    
                my_columns[0][1].append(sum([1 for r in s if get_target(r)!=TARGETS[t]]))
                    
                row_value = row_value + 1
                
    for r in range(data_size): #constraint (4bis)
        
        if r in s:
            
            my_columns[0][0].append("constraint_4bis_" + str(r) + "_" +str(leaf))
            
            my_columns[0][1].append(1)
                    
            row_value = row_value + 1
                
    for r in range(data_size): #constraint (5)
                                                    
        if r in s:
    
            my_columns[0][0].append("constraint_5_" + str(r))

            my_columns[0][1].append(1)
        
            row_value = row_value + 1
        
    for l in range(num_leafs): #constraint (6)
        
        if l==leaf:
            
            my_columns[0][0].append("constraint_6_" + str(l))

            my_columns[0][1].append(1)
            
            row_value = row_value + 1
                                    
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, columns = my_columns, names = var_names)

    #row_names, row_values, row_right_sides, row_senses = create_rows_CG(inputdepth,segments_set)
    
    #prob.linear_constraints.delete()
    
    #prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
    
    prob.set_problem_type(0)
    
    return prob

def create_variables_CG(depth,segments_set):
    
    var_value = 0

    var_names = []

    var_types = ""

    var_lb = []

    var_ub = []

    var_obj = []
    
    data_size = get_data_size()

    num_features = get_num_features()

    num_leafs = 2**depth

    num_nodes = num_leafs-1

    # node n had a boolean test on feature f, boolean. On the paper: f_{i,j}

    for j in range(num_nodes):

        for i in range(num_features):

            var_names.append("node_feature_" + str(j) + "_" + str(i))

            var_types = var_types + "C"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1

    # value used in the boolean test in node n, integer. On the paper: c_{j}

    for j in range(num_nodes):

        var_names.append("node_constant_" + str(j))

        var_types = var_types + "C"

        var_lb.append(0-0.01)

        var_ub.append(1+0.01)

        var_obj.append(0)

        var_value = var_value + 1

    # leaf l predicts type t, boolean. On the paper: p_{l,t}
    
    for l in range(num_leafs):

        for t in range(get_num_targets()):

            var_names.append("prediction_type_" + str(t) + "_" + str(l))

            var_types = var_types + "C"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1
            
    
            
    # leaf error, variables to minimize. On the paper: e_{l}

    for l in range(num_leafs):

        var_names.append("leaf_error_" + str(l))

        var_types = var_types + "C"

        var_lb.append(0)

        var_ub.append(cplex.infinity)

        var_obj.append(0.5)

        var_value = var_value + 1
        
    
        
    # row error, variables to minimize. On the paper: e_{r}

    for r in range(data_size):

        var_names.append("row_error_" + str(r))

        var_types = var_types + "C"

        var_lb.append(0)

        var_ub.append(cplex.infinity)

        var_obj.append(0.5)

        var_value = var_value + 1
        
    for l in range(num_leafs): # x_{l,s}
    
        for s in range(len(segments_set[l])): 
        
            var_names.append("segment_leaf_" + str(s) + "_" + str(l))

            var_types = var_types + "C"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1

    return var_names, var_types, var_lb, var_ub, var_obj


def create_rows_CG(depth,segments_set):

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
            
    constraint_indicators.append(row_value)
    
    for i in range(num_features): #constraint (2), indicator 0

        for j in range(num_nodes):
            
            for r in range(data_size):
                
                col_names, col_values = [], []
            
                for l in get_left_leafs(j, num_nodes):
    
                    col_names.extend(["segment_leaf_"  + str(s) + "_" + str(l) for s in range(len(segments_set[l])) if r in segments_set[l][s]]) #x_{l,s}
    
                    col_values.extend([get_feature_value(r,i) for s in range(len(segments_set[l])) if r in segments_set[l][s]])
    
                col_names.extend(["node_feature_" + str(j) + "_" + str(i), "node_constant_" + str(j)])
                
                col_values.extend([1, -1])

                row_names.append("constraint_2_" + str(i) + "_" + str(j) + "_" +str(r))
        
                row_values.append([col_names,col_values])
        
                row_right_sides.append(1)
        
                row_senses = row_senses + "L"
        
                row_value = row_value + 1
                
    constraint_indicators.append(row_value)
            
    for i in range(num_features): #constraint (3), indicator 1

        for j in range(num_nodes):
            
            for r in range(data_size):
                
                col_names, col_values = [], []
            
                for l in get_right_leafs(j, num_nodes):
    
                    col_names.extend(["segment_leaf_"  + str(s) + "_" + str(l) for s in range(len(segments_set[l])) if r in segments_set[l][s]]) #x_{l,s}
    
                    col_values.extend([1 for s in range(len(segments_set[l])) if r in segments_set[l][s]])
    
                col_names.extend(["node_feature_" + str(j) + "_" + str(i), "node_constant_" + str(j)])
                
                col_values.extend([1, 1])

                row_names.append("constraint_3_" + str(i) + "_" + str(j) + "_" +str(r))
        
                row_values.append([col_names,col_values])
        
                row_right_sides.append(get_feature_value(r,i) + 2 - 0.01)
        
                row_senses = row_senses + "L"
        
                row_value = row_value + 1
                                
    constraint_indicators.append(row_value)
    
    #compute r_t
    
    r_t = [0 for t in range(get_num_targets())]
    
    for r in range(data_size):
        
        for t in range(get_num_targets()):
            
            if TARGETS[t] != get_target(r):
        
                r_t[t] += 1
            
    for l in range(num_leafs): #constraint (4), indicator 2
        
        for t in range(get_num_targets()):
            
            col_names, col_values = [], []
            
            for s in range(len(segments_set[l])):
                            
                col_names.extend(["segment_leaf_"  + str(s) + "_" + str(l)]) #x_{l,s}
                
                s_t = 0
                
                for r in segments_set[l][s]:
                    
                    if TARGETS[t] != get_target(r):
                        
                        s_t += 1
                
                col_values.extend([s_t])
                                                    
            col_names.extend(["prediction_type_" + str(t) + "_" + str(l)])

            col_values.extend([r_t[t]])

            col_names.extend(["leaf_error_" + str(l)])

            col_values.extend([-1])
            
            row_names.append("constraint_4_" + str(l) + "_" +str(t))
        
            row_values.append([col_names,col_values])
    
            row_right_sides.append(r_t[t])
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1
            
    constraint_indicators.append(row_value)
    
    for r in range(data_size): #constraint (4bis), indicator 3
        
        for l in range(num_leafs):
            
            col_names, col_values = [], []
            
            for s in range(len(segments_set[l])):
                
                if r in segments_set[l][s]:
            
                    col_names.extend(["segment_leaf_"  + str(s) + "_" + str(l)]) #x_{l,s}
                    
                    col_values.extend([1])
                    
            for t in range(get_num_targets()):
                
                if TARGETS[t] == get_target(r):

                    col_names.extend(["prediction_type_" + str(t) + "_" + str(l)])

                    col_values.extend([-1])

            col_names.extend(["row_error_" + str(r)])

            col_values.extend([-1])
            
            row_names.append("constraint_4bis_" + str(r) + "_" +str(l))
        
            row_values.append([col_names,col_values])
    
            row_right_sides.append(0)
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1
            
    constraint_indicators.append(row_value)
    
    for r in range(data_size): #constraint (5), indicator 4
        
        col_names, col_values = [], []
        
        for l in range(num_leafs):
            
            for s in range(len(segments_set[l])):
                
                if r in segments_set[l][s]:
        
                    col_names.extend(["segment_leaf_"  + str(s) + "_" + str(l)]) #x_{l,s}
                    
                    col_values.extend([1])
                    
        row_names.append("constraint_5_" + str(r))
                
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    constraint_indicators.append(row_value)
            
    for l in range(num_leafs): #constraint (6), indicator 5
        
        col_names = ["segment_leaf_"  + str(s) + "_" + str(l) for s in range(len(segments_set[l]))] #x_{l,s}
        
        col_values = [1 for s in range(len(segments_set[l]))] #x_{l,s}
        
        row_names.append("constraint_6_" + str(l))
        
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
                                
    constraint_indicators.append(row_value)
            
    for l in range(num_leafs): #constraint (8), indicator 6

        col_names = ["prediction_type_" + str(s) + "_" + str(l) for s in range(get_num_targets())]

        col_values = [1 for t in range(get_num_targets())]

        row_names.append("constraint_8_"+str(l))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    constraint_indicators.append(row_value)

    for j in range(num_nodes): #constraint (9), indicator 7

        col_names = ["node_feature_" + str(j) + "_" + str(i) for i in range(num_features)]

        col_values = [1 for i in range(num_features)]

        row_names.append("constraint_9_"+str(j))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    constraint_indicators.append(row_value)
                
    return row_names, row_values, row_right_sides, row_senses


def construct_master_problem2(depth,segments_set):
    
    global TARGETS
    
    prob = cplex.Cplex()
    
    prob.objective.set_sense(prob.objective.sense.minimize)

    var_names, var_types, var_lb, var_ub, var_obj = create_variables_CG(depth,segments_set)
    
    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, names = var_names)

    row_names, row_values, row_right_sides, row_senses = create_rows_CG(depth,segments_set)
    
    prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
            
    prob.set_problem_type(0) #tell cplex this is a LP, not a MILP
    
    prob.set_log_stream(None)
    prob.set_error_stream(None)
    prob.set_warning_stream(None)
    prob.set_results_stream(None)
    
    
    return prob