# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:09:31 2018

@author: Guillaume
"""

from BaP_Node import BaP_Node
from learn_tree_funcs import transform_data, read_file, write_file, get_num_targets, get_left_leafs, get_right_leafs
from learn_tree_funcs import get_num_features, get_data_size, get_min_value, get_max_value, get_feature_value, get_target
import regtrees2 as tr
import getopt
import sys
import cplex
from cplex.exceptions import CplexError

def create_variables_CG(depth,segments_number):

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
    
    for s in range(segments_number): # x_{l,s}
        
        for l in range(num_leafs):
            
            VARS["segment_leaf_" + str(s) + "_" + str(l)] = var_value

            var_names.append("#" + str(var_value))

            var_types = var_types + "C"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1

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

    return var_names, var_types, var_lb, var_ub, var_obj


def create_rows_CG(depth,segments_set):

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
    
    segments_number = len(segments_set)
    
    big_M = get_max_value() - get_min_value()
    
    big_M=10*big_M + 10
    
    for i in range(num_features): #constraint (15)

        for j in range(num_nodes):
            
            for l in get_left_leafs(j, num_nodes):

                col_names = [VARS["segment_leaf_"  + str(s) + "_" + str(l)] for s in range(segments_number)] #x_{l,s}

                col_values = [max([get_feature_value(r,i) for r in s]) for s in segments_set] #mu^{i,s} max

                col_names.extend([VARS["node_feature_" + str(j) + "_" + str(i)], VARS["node_constant_" + str(j)]])
                
                col_values.extend([big_M, -1])

                row_names.append("#" + str(row_value))
        
                row_values.append([col_names,col_values])
        
                row_right_sides.append(big_M)
        
                row_senses = row_senses + "L"
        
                row_value = row_value + 1
            
    for i in range(num_features): #constraint (16)

        for j in range(num_nodes):
            
            for l in get_right_leafs(j, num_nodes):

                col_names = [VARS["segment_leaf_"  + str(s) + "_" + str(l)] for s in range(segments_number)] #x_{l,s}

                col_values = [-min([get_feature_value(r,i) for r in s]) for s in segments_set] #mu^{i,s} min

                col_names.extend([VARS["node_feature_" + str(j) + "_" + str(i)], VARS["node_constant_" + str(j)]])
                
                col_values.extend([big_M, 1])

                row_names.append("#" + str(row_value))
        
                row_values.append([col_names,col_values])
        
                row_right_sides.append(big_M)
        
                row_senses = row_senses + "L"
        
                row_value = row_value + 1
                
    for r in range(data_size): #constraint (17)
        
        col_names, col_values = [], []
        
        for l in range(num_leafs):
            
            for s in range(segments_number):
                
                if r in segments_set[s]:
        
                    col_names.extend([VARS["segment_leaf_"  + str(s) + "_" + str(l)]]) #x_{l,s}
                    
                    col_values.extend([1])
                    
        row_names.append("#" + str(row_value))
        
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    for l in range(num_leafs): #constraint (18)
        
        col_names = [VARS["segment_leaf_"  + str(s) + "_" + str(l)] for s in range(segments_number)] #x_{l,s}
        
        row_names.append("#" + str(row_value))
        
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    for r in range(data_size): #constraint (19)
        
        for l in range(num_leafs):
            
            col_names, col_values = [], []
            
            for s in range(segments_number):
                
                if r in segments_set[s]:
            
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
            
    for l in range(num_leafs): #constraint (20)

        col_names = [VARS["prediction_type_" + str(s) + "_" + str(l)] for s in range(get_num_targets())]

        col_values = [1 for s in range(get_num_targets())]

        row_names.append("#" + str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1

    for j in range(num_nodes): #constraint (21)

        col_names = [VARS["node_feature_" + str(j) + "_" + str(i)] for i in range(num_features)]

        col_values = [1 for i in range(num_features)]

        row_names.append("#"+str(row_value))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    return row_names, row_values, row_right_sides, row_senses


def construct_problem(depth,segments_set):
    
    prob = cplex.Cplex()

    try:

        prob.objective.set_sense(prob.objective.sense.minimize)

        var_names, var_types, var_lb, var_ub, var_obj = create_variables_CG(depth,len(segments_set))

        print "num_vars", len(var_names)

        prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types)#, names = var_names)

        row_names, row_values, row_right_sides, row_senses = create_rows_CG(depth,segments_set)

        print "num_rows", len(row_names)

        prob.linear_constraints.add(lin_expr = row_values, senses = row_senses, rhs = row_right_sides, names = row_names)

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

        #prob.parameters.mip.polishafter.time.set(inputtime - inputpolish)
        #prob.parameters.timelimit.set(inputtime)
        
    except CplexError, exc:

        print exc

        return []
    
    return prob



def main(argv):
    
    global TARGETS
    global segments_set
    global VARS
    
    VARS={}

    inputfile = ''

    try:
       
        opts, args = getopt.getopt(argv,"f:d:",["ifile=","depth="])

    except getopt.GetoptError:
       
        sys.exit(2)
      
    for opt, arg in opts:

        if opt in ("-f", "--ifile"):

            inputfile = arg
        
        elif opt in ("-d", "--depth"):

            inputdepth = int(arg)
            
    read_file(inputfile)
   
    transform_data()

    write_file(inputfile+".transformed")
   
    tr.df = tr.get_data(inputfile+".transformed")
                   
    TARGETS, segments_set, best_solution_value=tr.learnTrees_and_return_segments(inputdepth)
    
    tr.get_code()
            
    prob=construct_problem(inputdepth,segments_set)
            
    root_node=BaP_Node(segments_set,prob)
            
    root_node.solve_relaxation()
    
    return root_node
    