# -*- coding: utf-8 -*-
"""
Created on Wed Apr 04 08:31:17 2018

@author: Guillaume

NOTE : This code is based on the paper "Finding Optimal Decision Trees via Column Generation" by Murat Fırat, Sicco Verwer and Yingqian Zhang.
The notations in the code are close to the ones found on this paper. 
"""

import cplex
from cplex.exceptions import CplexError
import sys
import numpy as np
import csv
import math
import getopt
import regtrees as tr
from learn_tree_funcs import get_min_value, get_max_value, sget_right_node, sget_left_node, TARGETS, VARS, get_left_node, get_right_node, get_parent, get_path, get_pathn, get_depth, get_target, get_feature_value, get_min_value, get_max_value, get_num_targets, convert_leaf, get_max_value_f, get_min_value_f, sget_feature, convert_node, sget_node_constant, read_file, transform_data, write_file, set_double_data, get_num_features, get_data_size, get_num_parents, get_feature, get_right_leafs, get_left_leafs

"""
def get_depth(node,inputdepth): #get the depth of an internal node
    
    for i in range(inputdepth):
        if (node + 1 - 2**i )%(2**(i+1))==0:
            return inputdepth-1-i
    raise ValueError('Function get_depth did not return any value')
"""

def get_start_solutions(depth):

    global inputsym

#hello

    col_var_names = []

    col_var_values = []

    num_features = get_num_features()

    num_leafs = 2**depth

    num_nodes = num_leafs-1

    

    num_features = get_num_features()

    data_size = get_data_size()

    

    num_leafs = 2**depth

    num_nodes = num_leafs-1

    

    values = tr.dt.tree_.value

    

    for n in range(num_nodes):

        feat = sget_feature(tr.dt, convert_node(tr.dt, n, num_nodes))

        if feat < 0:

            feat = 0

        for f in range(num_features):

            if f == feat:

                col_var_names.extend([VARS["node_feature_" + str(n) + "_" + str(f)]])

                col_var_values.extend([1])

            else:

                col_var_names.extend([VARS["node_feature_" + str(n) + "_" + str(f)]])

                col_var_values.extend([0])

        

        

        

        if inputsym == 1 and len(get_left_leafs(n, num_nodes)) == 1:

            ll = get_left_leafs(n, num_nodes)[0]

            rl = get_right_leafs(n, num_nodes)[0]

            

            predl = values[convert_leaf(tr.dt, ll, num_nodes)].tolist()[0]

            predr = values[convert_leaf(tr.dt, rl, num_nodes)].tolist()[0]

            

            if predl.index(max(predl)) == predr.index(max(predr)):

                val = get_max_value_f(feat)

    for n in range(num_nodes):
        
        val = sget_node_constant(tr.dt, convert_node(tr.dt, n, num_nodes))

        col_var_names.extend([VARS["node_constant_" + str(n)]])

        col_var_values.extend([int(math.floor(val))])


    
    odd = False

    prev_max_class = -1

    

    for l in reversed(range(num_leafs)):

        predictions = values[convert_leaf(tr.dt, l, num_nodes)].tolist()[0]

        max_index = predictions.index(max(predictions))

        max_class = tr.dt.classes_[max_index]

        

        if inputsym == 1 and odd and max_class == prev_max_class:

            if TARGETS[0] == max_class:

                col_var_names.extend([VARS["prediction_type_" + str(0) + "_" + str(num_leafs - 1 - l)]])

                col_var_values.extend([0])

                col_var_names.extend([VARS["prediction_type_" + str(1) + "_" + str(num_leafs - 1 - l)]])

                col_var_values.extend([1])

            else:

                col_var_names.extend([VARS["prediction_type_" + str(0) + "_" + str(num_leafs - 1 - l)]])

                col_var_values.extend([1])

                col_var_names.extend([VARS["prediction_type_" + str(1) + "_" + str(num_leafs - 1 - l)]])

                col_var_values.extend([0])

            for s in range(2,get_num_targets()):

                col_var_names.extend([VARS["prediction_type_" + str(s) + "_" + str(num_leafs - 1 - l)]])

                col_var_values.extend([0])

        else:

            for s in range(get_num_targets()):

                if TARGETS[s] == max_class:

                    col_var_names.extend([VARS["prediction_type_" + str(s) + "_" + str(num_leafs - 1 - l)]])

                    col_var_values.extend([1])

                else:

                    col_var_names.extend([VARS["prediction_type_" + str(s) + "_" + str(num_leafs - 1 - l)]])

                    col_var_values.extend([0])

        

        prev_max_class = max_class

        odd = not odd
    

    

    return col_var_names, col_var_values

def convert_node2(tree, node, num_nodes):

    path = get_pathn(node, num_nodes)

    path_len = int(len(path)/2.0)

    

    index = 0

    

    for l in reversed(range(1,path_len)):

        node = path[l*2]

        dir = path[l*2+1]

                

        if sget_right_node(tree, index) == -1:

            return index



        if dir == "right":

            index = sget_right_node(tree, index)

        if dir == "left":

            index = sget_left_node(tree, index)



    return index



def convert_leaf2(tree, leaf, num_nodes):

    path = get_path(leaf, num_nodes)

    path_len = int(len(path)/2.0)

    

    index = 0

    

    for l in reversed(range(path_len)):

        node = path[l*2]

        dir = path[l*2+1]

        

        if sget_right_node(tree, index) == -1:

            return index

        

        if dir == "right":

            index = sget_right_node(tree, index)

        if dir == "left":

            index = sget_left_node(tree, index)



    return index

def create_rows(depth):

    global VARS
    global TARGETS

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
    
    for r in range(data_size): #constraint (2)

        for j in range(num_nodes):

            col_names = [VARS["node_feature_"  + str(j) + "_" + str(i)] for i in range(num_features)] #f_{i,j}

            col_values = [get_feature_value(r,i) for i in range(num_features)] #mu^{i,r}
                        
            left_node=get_left_node(j,num_nodes)
                        
            if int(left_node)!=-1: #if not a leaf

                col_names.extend([VARS["path_node_" + str(j) + "_" + str(r)], VARS["path_node_" + str(left_node) + "_" + str(r)]])#VARS["depth_true_" + str(r) + "_" + str(get_depth(j,num_nodes)-1)]])

            else:
                
                col_names.extend([VARS["path_node_" + str(j) + "_" + str(r)], VARS["path_leaf_" + str(j) + "_" + str(r)]])

            col_values.extend([big_M, big_M])

            col_names.extend([VARS["node_constant_" + str(j)]])

            col_values.extend([-1])

            row_names.append("#" + str(row_value))

            row_values.append([col_names,col_values])

            row_right_sides.append(2*big_M)

            row_senses = row_senses + "L"

            row_value = row_value + 1
            
    for r in range(data_size): #constraint (3)

        for j in range(num_nodes):

            col_names = [VARS["node_feature_"  + str(j) + "_" + str(i)] for i in range(num_features)] #f_{i,j}

            col_values = [-get_feature_value(r,i) for i in range(num_features)] #mu^{i,r}
                        
            right_node=get_right_node(j,num_nodes)
            
            if int(right_node)!=-1: #if not a leaf

                col_names.extend([VARS["path_node_" + str(j) + "_" + str(r)], VARS["path_node_" + str(right_node) + "_" + str(r)]])#VARS["depth_true_" + str(r) + "_" + str(get_depth(j,num_nodes)-1)]])

            else:
                
                col_names.extend([VARS["path_node_" + str(j) + "_" + str(r)], VARS["path_leaf_" + str(j+1) + "_" + str(r)]])

            #col_names.extend([VARS["path_node_" + str(j) + "_" + str(r)], VARS["depth_true_" + str(r) + "_" + str(get_depth(j,num_nodes)-1)]])

            col_values.extend([big_M, big_M])

            col_names.extend([VARS["node_constant_" + str(j)]])

            col_values.extend([1])

            row_names.append("#" + str(row_value))

            row_values.append([col_names,col_values])
            
            row_right_sides.append(2*big_M -0.01)

            row_senses = row_senses + "L"

            row_value = row_value + 1
    
    for l in range(num_leafs): #constraint (4)

        col_names = [VARS["prediction_type_" + str(s) + "_" + str(l)] for s in range(get_num_targets())]

        col_values = [1 for s in range(get_num_targets())]

        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1

    for j in range(num_nodes): #constraint (5)

        col_names = [VARS["node_feature_" + str(j) + "_" + str(i)] for i in range(num_features)]

        col_values = [1 for i in range(num_features)]

        row_names.append("#"+str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
            
    for r in range(data_size): # constraint (6)
        
        col_names = [VARS["path_leaf_" + str(l) + "_" + str(r)] for l in range(num_leafs)]

        col_values = [1 for l in range(num_leafs)]
        
        col_names.extend([VARS["path_node_" + str(j) +"_" + str(r)] for j in range(num_nodes)])
        
        col_values.extend([1 for j in range(num_nodes)])
        
        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(depth+1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    for r in range(data_size): # contraint (7)
                    
        col_names = []

        col_values = []
        
        for l in range(num_leafs):
                            
            col_names.extend([VARS["path_leaf_" + str(l) +"_" +str(r)]])
            
            col_values.extend([1])
                
        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
            
    for r in range(data_size): # constraint (8) for internal nodes
        
        for j in range(num_nodes):
            
            if j != (num_nodes-1)/2:
            
                col_names = [VARS["path_node_" + str(j) + "_" + str(r)]]
        
                col_values = [1]
                
                col_names.extend([VARS["path_node_" + str(get_parent(j,depth)) +"_" +str(r)]])
                        
                col_values.extend([-1])
                        
                row_names.append("#" + str(row_value))
    
                row_values.append([col_names,col_values])
    
                row_right_sides.append(0)
    
                row_senses = row_senses + "L"
    
                row_value = row_value + 1
            
    for r in range(data_size): # constraint (8) for leaves
        
        for l in range(num_leafs):
            
            col_names = [VARS["path_leaf_" + str(l) + "_" + str(r)]]
    
            col_values = [1]
            
            col_names.extend([VARS["path_node_" + str(l-l%2) +"_" +str(r)]])
                    
            col_values.extend([-1])
                    
            row_names.append("#" + str(row_value))

            row_values.append([col_names,col_values])

            row_right_sides.append(0)

            row_senses = row_senses + "L"

            row_value = row_value + 1
            
    for r in range(data_size): #constraint (9)

        for l in range(num_leafs):

            col_names = [VARS["path_leaf_" + str(l) + "_" + str(r)]]

            col_values = [1]

            for s in range(get_num_targets()):

                if TARGETS[s] != get_target(r):

                    col_names.extend([VARS["prediction_type_" + str(s) + "_" + str(l)]])

                    col_values.extend([1])

            col_names.extend([VARS["row_error_" + str(r)]])

            col_values.extend([-1])

            row_names.append("#" + str(row_value))

            row_values.append([col_names,col_values])

            row_right_sides.append(1)

            row_senses = row_senses + "L"

            row_value = row_value + 1

    if inputsym == 1: #valid inequalties ?

        for n in range(num_nodes):

            left_leaf = get_left_leafs(n, num_nodes)

            right_leaf = get_right_leafs(n, num_nodes)

            if len(left_leaf) != 1:

                continue

            for s in range(get_num_targets()):

                col_names = [VARS["prediction_type_" + str(s) + "_" + str(left_leaf[0])]]

                col_values = [1]

                col_names.extend([VARS["prediction_type_" + str(s) + "_" + str(right_leaf[0])]])

                col_values.extend([1])

                row_names.append("#" + str(row_value))

                row_values.append([col_names,col_values])

                row_right_sides.append(1)

                row_senses = row_senses + "L"

                row_value = row_value + 1

    return row_names, row_values, row_right_sides, row_senses



def create_variables(depth,prob):

    global VARS

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

            var_types = var_types + "B"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1

    # value used in the boolean test in node n, integer. On the paper: c_{j}

    for j in range(num_nodes):

        VARS["node_constant_" + str(j)] = var_value

        var_names.append("#" + str(var_value))

        if continuousconstant == 1:

            var_types = var_types + "C"

        else:

            var_types = var_types + "I"

        var_lb.append(get_min_value())

        var_ub.append(get_max_value())

        var_obj.append(0)

        var_value = var_value + 1

    # leaf l predicts type t, boolean. On the paper: p_{l,t}
    
    for l in range(num_leafs):

        for t in range(get_num_targets()):

            VARS["prediction_type_" + str(t) + "_" + str(l)] = var_value

            var_names.append("#" + str(var_value))

            var_types = var_types + "B"

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

    # indicates that data row r passes node j when executed in decision tree. Careful, leafs are included. On the paper: pt_{r,j}
    
    for r in range(data_size):
    
        for j in range(num_nodes):

            VARS["path_node_" + str(j) + "_" + str(r)] = var_value

            var_names.append("#" + str(var_value))

            var_types = var_types + "B"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1
            
        for l in range(num_leafs):

            VARS["path_leaf_" + str(l) + "_" + str(r)] = var_value

            var_names.append("#" + str(var_value))

            var_types = var_types + "B"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1

    return var_names, var_types, var_lb, var_ub, var_obj


def get_start_solutions_new(depth):

    global inputsym
    global TARGETS

    col_var_names = []

    col_var_values = []

    num_features = get_num_features()

    num_leafs = 2**depth

    num_nodes = num_leafs-1

    data_size = get_data_size()

    values = tr.dt.tree_.value

    for n in range(num_nodes): 

        feat = sget_feature(tr.dt, convert_node2(tr.dt, n, num_nodes))

        if feat < 0:

            feat = 0

        for f in range(num_features): #f_{i,j}
            

            if f == feat:

                col_var_names.extend([VARS["node_feature_" + str(n) + "_" + str(f)]])

                col_var_values.extend([1])

            else:

                col_var_names.extend([VARS["node_feature_" + str(n) + "_" + str(f)]])

                col_var_values.extend([0])
        
    for n in range(num_nodes): #c_{j}
        
        """TODO
        
        if inputsym == 1 and len(get_left_leafs(n, num_nodes)) == 1:

            ll = get_left_leafs(n, num_nodes)[0]

            rl = get_right_leafs(n, num_nodes)[0]

            predl = values[convert_leaf2(tr.dt, ll, num_nodes)].tolist()[0]

            predr = values[convert_leaf2(tr.dt, rl, num_nodes)].tolist()[0]

            if predl.index(max(predl)) == predr.index(max(predr)):

                val = get_max_value_f(feat)
                
        else:
        """
        
        val = sget_node_constant(tr.dt, convert_node2(tr.dt, n, num_nodes))

        col_var_names.extend([VARS["node_constant_" + str(n)]]) 

        col_var_values.extend([val])
        
    odd = False

    prev_max_class = None

    for l in range(num_leafs):

        predictions = values[convert_leaf2(tr.dt, l, num_nodes)].tolist()[0]

        max_index = predictions.index(max(predictions))

        max_class = tr.dt.classes_[max_index]  
        
        """TODO
        
        if inputsym == 1 and odd and max_class == prev_max_class: #trick to be sure that valid inequalties hold

            if TARGETS[0] == max_class:

                col_var_names.extend([VARS["prediction_type_" + str(0) + "_" + str(l)]])

                col_var_values.extend([0])

                col_var_names.extend([VARS["prediction_type_" + str(1) + "_" + str(l)]])

                col_var_values.extend([1])

            else:

                col_var_names.extend([VARS["prediction_type_" + str(0) + "_" + str(l)]])

                col_var_values.extend([1])

                col_var_names.extend([VARS["prediction_type_" + str(1) + "_" + str(l)]])

                col_var_values.extend([0])

            for s in range(2,get_num_targets()):

                col_var_names.extend([VARS["prediction_type_" + str(s) + "_" + str(l)]])

                col_var_values.extend([0])
                
        else:
        """

        for s in range(get_num_targets()):
            
            if TARGETS[s] == max_class:

                col_var_names.extend([VARS["prediction_type_" + str(s) + "_" + str(l)]])

                col_var_values.extend([1])

            else:

                col_var_names.extend([VARS["prediction_type_" + str(s) + "_" + str(l)]])

                col_var_values.extend([0])

        odd = not odd

        prev_max_class=max_class                
    
                            
    for r in range(data_size): #e_{r}
        
        final_leaf = tr.dt.apply(np.array([tr.df.drop(tr.df.columns[-1],axis=1).values[r]],dtype=np.float32))[0]
                    
        predictions = values[final_leaf].tolist()[0]

        max_index = predictions.index(max(predictions))

        max_class = tr.dt.classes_[max_index]
        
        if get_target(r)==(max_class):
            
            col_var_names.extend([VARS["row_error_" + str(r)]])

            col_var_values.extend([0])
            
        else:
            
            col_var_names.extend([VARS["row_error_" + str(r)]])

            col_var_values.extend([1])
            
    
            
    M = tr.dt.decision_path(np.array(tr.df.drop(tr.df.columns[-1],axis=1).values,dtype=np.float32)) 
    
    for r in range(data_size): #pt_{r,j}
        
        for j in range(num_nodes):
                        
            if M[r,convert_node2(tr.dt,j,num_nodes)]==1:
                
                col_var_names.extend([VARS["path_node_" + str(j) + "_" +str(r)]])

                col_var_values.extend([1])
                
            else:
                
                col_var_names.extend([VARS["path_node_" + str(j) + "_" +str(r)]])

                col_var_values.extend([0])
                
        for l in range(num_leafs):
                        
            if M[r,convert_leaf2(tr.dt,l,num_nodes)]==1:
                
                col_var_names.extend([VARS["path_leaf_" + str(l) + "_" +str(r)]])

                col_var_values.extend([1])
                
            else:
                
                col_var_names.extend([VARS["path_leaf_" + str(l) + "_" +str(r)]])

                col_var_values.extend([0])
               
    
                
    
                

    return col_var_names, col_var_values



def print_nodes(node, diff, depth, solution_values, num_nodes, num_features):
    
    if diff > 0:

        for f in range(num_features):

            if solution_values[VARS["node_feature_" + str(node) + "_" + str(f)]] > 0.5:

                print "  " * depth, node, get_feature(f), "<=", solution_values[VARS["node_constant_" + str(node)]]

        print_nodes(node-diff, diff/2, depth+1, solution_values, num_nodes, num_features)

        for f in range(num_features):

            if solution_values[VARS["node_feature_" + str(node) + "_" + str(f)]] > 0.5:

                print "  " * depth, node, get_feature(f), ">", solution_values[VARS["node_constant_" + str(node)]]

        print_nodes(node+diff, diff/2, depth+1, solution_values, num_nodes, num_features)

    else:

        for f in range(num_features):

            if solution_values[VARS["node_feature_" + str(node) + "_" + str(f)]] > 0.5:

                print "  " * depth, node, get_feature(f), "<=", solution_values[VARS["node_constant_" + str(node)]]

        for l in get_left_leafs(node, num_nodes):

            for s in range(get_num_targets()):

                if solution_values[VARS["prediction_type_" + str(s) + "_" + str(l)]] > 0.5:

                    print "  " * (depth+1), l, TARGETS[s]

        for f in range(num_features):

            if solution_values[VARS["node_feature_" + str(node) + "_" + str(f)]] > 0.5:

                print "  " * depth, node, get_feature(f), ">", solution_values[VARS["node_constant_" + str(node)]]

        for l in get_right_leafs(node, num_nodes):

            for s in range(get_num_targets()):

                if solution_values[VARS["prediction_type_" + str(s) + "_" + str(l)]] > 0.5:

                    print "  " * (depth+1), l, TARGETS[s]
            

def print_tree(num_nodes, solution_values, num_features):

    print "tree:"

    diff = (num_nodes + 1) / 2

    print_nodes(diff-1, diff / 2, 0, solution_values, num_nodes, num_features)



def lpdtree(depth):

    global SORTED_FEATURE, inputstart, inputtime, inputpolish

    prob = cplex.Cplex()

    num_features = get_num_features()

    data_size = get_data_size()

    num_leafs = 2**depth

    num_nodes = num_leafs-1

    try:

        prob.objective.set_sense(prob.objective.sense.minimize)

        var_names, var_types, var_lb, var_ub, var_obj = create_variables(depth,prob)

        print "num_vars", len(var_names)

        prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types)#, names = var_names)

        row_names, row_values, row_right_sides, row_senses = create_rows(depth)

        print "num_rows", len(row_names)

        prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)

        order_set = []

        for n in range(num_nodes):

            for f in range(num_features):

                order_set.append((VARS["node_feature_" + str(n) + "_" + str(f)], 11+2*((num_nodes - get_num_parents(n,num_nodes))), 1))

        for n in range(num_nodes):

            order_set.append((VARS["node_constant_" + str(n)], 10+2*((num_nodes - get_num_parents(n,num_nodes))), -1))

        prob.order.set(order_set)

        if inputstart == 1:

            col_var_names, col_var_values = get_start_solutions_new(depth)
                        
            #return get_start_solutions_new(depth)

            prob.MIP_starts.add([col_var_names, col_var_values], 1)#prob.MIP_starts.effort_level.auto)#  level=1 forces cplex to take the entire solution as it is

        prob.write("test.lp")

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

        prob.parameters.mip.polishafter.time.set(inputtime - inputpolish)
        prob.parameters.timelimit.set(inputtime)

        prob.solve()

    except CplexError, exc:

        print exc

        return []

    print

    print "Solution status = " , prob.solution.get_status(), ":", prob.solution.status[prob.solution.get_status()]

    if "infeasible" in prob.solution.status[prob.solution.get_status()]:

        return []

    print "Solution value  = ", prob.solution.get_objective_value()
    
    print "Accuracy = ", (data_size-prob.solution.get_objective_value())/data_size

    num_features = get_num_features()

    data_size = get_data_size() #useless ?

    num_leafs = 2**depth

    num_nodes = num_leafs-1

    solution = []

    solution_values = prob.solution.get_values()

    print_tree(num_nodes, solution_values, num_features)

    return solution_values



def main(argv):

   global inputstart
   global inputsym
   global inputtime
   global inputpolish
   global double_data
   global ctype
   global continuousconstant

   inputfile = ''

   try:
       
      opts, args = getopt.getopt(argv,"f:d:s:y:t:p:u:v:c:",["ifile=","depth=","start=","symmetry=","timelimit=","polishtime=","doubledata=","variant=","constant="])

   except getopt.GetoptError:
       
      sys.exit(2)

   for opt, arg in opts:

      if opt in ("-f", "--ifile"):

         inputfile = arg

      elif opt in ("-d", "--depth"):

         inputdepth = int(arg)

      elif opt in ("-s", "--start"):

         inputstart = int(arg)

      elif opt in ("-y", "--symmetry"):

         inputsym = int(arg)

      elif opt in ("-u", "--doubledata"):

         if int(arg) == 1:

            double_data = True
            set_double_data(True)

         else:

            double_data = False
            set_double_data(False)

      elif opt in ("-t", "--timelimit"):

         inputtime = int(arg)

      elif opt in ("-p", "--polishtime"):

         inputpolish = int(arg)

      elif opt in ("-v", "--variant"):

         ctype = int(arg)

      elif opt in ("-c", "--constant"):

         continuousconstant = int(arg)

   read_file(inputfile)
   
   transform_data()

   write_file(inputfile+".transformed")
   
   tr.df = tr.get_data(inputfile+".transformed")
   
   TARGETS.sort()
            
   tr.learnTrees(inputdepth)

   tr.get_code()

   return lpdtree(inputdepth)
   
   
   
ws=main(['-fwinequality-red.csv', '-d 1', '-s 1', '-t 10', '-y 0', '-p 0', '-c 1'])

def print_solution(sol,depth):
    
    num_features = get_num_features()

    data_size = get_data_size()

    num_leafs = 2**depth

    num_nodes = num_leafs-1
    
    for j in range(num_nodes):
        print("c_{j}",j,sol[VARS["node_constant_"+str(j)]])
        
        
    for r in range(data_size):
        
        print("Path: (pt_{r,j} ","r=",r)
    
        for j in range(num_nodes):

            print(sol[VARS["path_node_" + str(j) + "_" + str(r)]])
            
        print("Final leaf:")

        for l in range(num_leafs):

            print(sol[VARS["path_leaf_" + str(l) + "_" + str(r)]])
        print
    
        
    for r in range(data_size):
        
        print("Row error ("+str(r)+") ",sol[VARS["row_error_"+str(r)]])
        
    for t in range(get_num_targets()):

        for l in range(num_leafs):

            print("p_{l,t} l=",l," t=",t," ",sol[VARS["prediction_type_" + str(int(TARGETS[t])) + "_" + str(l)]])
            
    for j in range(num_nodes):

        for i in range(num_features):

            print("f_{i,j} i=",i," j=",j,sol[VARS["node_feature_" + str(j) + "_" + str(i)]])
    