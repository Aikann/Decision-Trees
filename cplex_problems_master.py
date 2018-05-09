# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 15:36:08 2018

@author: Guillaume
"""

from learn_tree_funcs import get_num_targets, get_left_leafs, get_right_leafs
from learn_tree_funcs import get_num_features, get_data_size, get_min_value, get_max_value, get_feature_value, get_target
import cplex

def obtain_TARGETS(t):
    global TARGETS
    TARGETS=t
    
def add_f_constraint(prob,i,j,right_side):
            
    new_prob = cplex.Cplex()
    
    prob.write("tmp.lp",'lp')
    
    new_prob.read("tmp.lp",'lp')
    
    col_names = ["node_feature_"+str(j)+"_"+str(i)]

    col_values = [1]

    row_names=["branch_f_" + str(i) + "_" + str(j)]

    row_values=[[col_names,col_values]]

    row_right_sides = [right_side]

    row_senses = "E"
    
    new_prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
    
    new_prob.set_problem_type(0) #tell cplex this is a LP, not a MILP
    
    new_prob.set_log_stream(None)
    new_prob.set_error_stream(None)
    new_prob.set_warning_stream(None)
    new_prob.set_results_stream(None)
    
    return new_prob

def add_p_constraint(prob,l,t,right_side):
            
    new_prob = cplex.Cplex()
    
    prob.write("tmp.lp",'lp')
    
    new_prob.read("tmp.lp",'lp')
    
    col_names = ["prediction_type_"+str(t)+"_"+str(l)]

    col_values = [1]

    row_names=["branch_p_" + str(t) + "_" + str(l)]

    row_values=[[col_names,col_values]]

    row_right_sides = [right_side]

    row_senses = "E"
    
    new_prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)
    
    new_prob.set_problem_type(0) #tell cplex this is a LP, not a MILP
    
    new_prob.set_log_stream(None)
    new_prob.set_error_stream(None)
    new_prob.set_warning_stream(None)
    new_prob.set_results_stream(None)
    
    return new_prob

def add_variable_to_master_and_rebuild(depth,prob,prev_segments_set,segments_to_add,leaf):
    
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
        
    for i in range(num_features): #constraint (15)

        for j in range(num_nodes):
    
            for l in get_left_leafs(j, num_nodes):

                my_columns[0][0].append("constraint_15_" + str(i) + "_" + str(j) + "_" +str(l))

                my_columns[0][1].append(max([get_feature_value(r,i) for r in s])) #mu^{i,s} max
                
                row_value = row_value + 1
                
    for i in range(num_features): #constraint (16)

        for j in range(num_nodes):
    
            for l in get_right_leafs(j, num_nodes):

                my_columns[0][0].append("constraint_16_" + str(i) + "_" + str(j) + "_" +str(l))

                my_columns[0][1].append(max([get_feature_value(r,i) for r in s])) #mu^{i,s} max
                
                row_value = row_value + 1
                
    for r in range(data_size): #constraint (17)
        
        if r in s:
            
            my_columns[0][0].append("constraint_17_" + str(r))

            my_columns[0][1].append(1)
            
        row_value = row_value + 1
        
    for l in range(num_leafs): #constraint (18)
        
        if l==leaf:
            
            my_columns[0][0].append("constraint_18_" + str(l))

            my_columns[0][1].append(1)
            
        row_value = row_value + 1
        
    for r in range(data_size): #constraint (19)
    
        for l in range(num_leafs):
                            
            if l == leaf:
                
                if r in s:
            
                    my_columns[0][0].append("constraint_19_" + str(r) + "_" +str(l))

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

    num_features = get_num_features()

    data_size = get_data_size()

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

        var_lb.append(get_min_value())

        var_ub.append(get_max_value())

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
            
    # row error, variables to minimize. On the paper: e_{r}

    for r in range(data_size):

        var_names.append("row_error_" + str(r))

        var_types = var_types + "C"

        var_lb.append(0)

        var_ub.append(1)

        var_obj.append(1)

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
        
    big_M = get_max_value() - get_min_value()
    
    constraint_indicators.append(row_value)
    
    for i in range(num_features): #constraint (15), indicator 0

        for j in range(num_nodes):
            
            for l in get_left_leafs(j, num_nodes):

                col_names = ["segment_leaf_"  + str(s) + "_" + str(l) for s in range(len(segments_set[l]))] #x_{l,s}

                col_values = [max([get_feature_value(r,i) for r in s]) for s in segments_set[l]] #mu^{i,s} max

                col_names.extend(["node_feature_" + str(j) + "_" + str(i), "node_constant_" + str(j)])
                
                col_values.extend([big_M, -1])

                row_names.append("constraint_15_" + str(i) + "_" + str(j) + "_" +str(l))
        
                row_values.append([col_names,col_values])
        
                row_right_sides.append(big_M)
        
                row_senses = row_senses + "L"
        
                row_value = row_value + 1
                
    constraint_indicators.append(row_value)
            
    for i in range(num_features): #constraint (16), indicator 1

        for j in range(num_nodes):
            
            for l in get_right_leafs(j, num_nodes):

                col_names = ["segment_leaf_"  + str(s) + "_" + str(l) for s in range(len(segments_set[l]))] #x_{l,s}

                col_values = [-min([get_feature_value(r,i) for r in s]) for s in segments_set[l]] #mu^{i,s} min

                col_names.extend(["node_feature_" + str(j) + "_" + str(i), "node_constant_" + str(j)])
                
                col_values.extend([big_M, 1])

                row_names.append("constraint_16_" + str(i) + "_" + str(j) + "_" +str(l))
        
                row_values.append([col_names,col_values])
        
                row_right_sides.append(big_M + 0.01)
        
                row_senses = row_senses + "L"
        
                row_value = row_value + 1
                
    constraint_indicators.append(row_value)
                
    for r in range(data_size): #constraint (17), indicator 2
        
        col_names, col_values = [], []
        
        for l in range(num_leafs):
            
            for s in range(len(segments_set[l])):
                
                if r in segments_set[l][s]:
        
                    col_names.extend(["segment_leaf_"  + str(s) + "_" + str(l)]) #x_{l,s}
                    
                    col_values.extend([1])
                    
        row_names.append("constraint_17_" + str(r))
                
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    constraint_indicators.append(row_value)
        
    for l in range(num_leafs): #constraint (18), indicator 3
        
        col_names = ["segment_leaf_"  + str(s) + "_" + str(l) for s in range(len(segments_set[l]))] #x_{l,s}
        
        col_values = [1 for s in range(len(segments_set[l]))] #x_{l,s}
        
        row_names.append("constraint_18_" + str(l))
        
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
            
                    col_names.extend(["segment_leaf_"  + str(s) + "_" + str(l)]) #x_{l,s}
                    
                    col_values.extend([1])
                    
            for t in range(get_num_targets()):
                
                if TARGETS[t] != get_target(r):

                    col_names.extend(["prediction_type_" + str(t) + "_" + str(l)])

                    col_values.extend([1])

            col_names.extend(["row_error_" + str(r)])

            col_values.extend([-1])
            
            row_names.append("constraint_19_" + str(r) + "_" +str(l))
        
            row_values.append([col_names,col_values])
    
            row_right_sides.append(1)
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1
            
    constraint_indicators.append(row_value)
            
    for l in range(num_leafs): #constraint (20), indicator 5

        col_names = ["prediction_type_" + str(s) + "_" + str(l) for s in range(get_num_targets())]

        col_values = [1 for s in range(get_num_targets())]

        row_names.append("constraint_20_"+str(l))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    constraint_indicators.append(row_value)

    for j in range(num_nodes): #constraint (21), indicator 6

        col_names = ["node_feature_" + str(j) + "_" + str(i) for i in range(num_features)]

        col_values = [1 for i in range(num_features)]

        row_names.append("constraint_21_"+str(j))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
                
    return row_names, row_values, row_right_sides, row_senses


def construct_master_problem(depth,segments_set):
    
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