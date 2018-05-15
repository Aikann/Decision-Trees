# -*- coding: utf-8 -*-
"""
Created on Wed Apr 04 08:31:17 2018

@author: Guillaume

NOTE : This code is based on the paper "Finding Optimal Decision Trees via Column Generation" by Murat Fırat, Sicco Verwer and Yingqian Zhang.
The notations in the code are close to the ones found on this paper. 
"""

from RMPSolver import display_prob_lite
import cplex
from cplex.exceptions import CplexError
import sys
import numpy as np
import getopt
import pandas as pd
from Instance import create_instance
from learn_tree_funcs import get_left_nodes, get_right_nodes, get_parents, scale_data, sget_right_node, sget_left_node, TARGETS, VARS, get_left_node, get_right_node, get_parent, get_path, get_pathn, get_depth, get_target, get_feature_value, get_min_value, get_max_value, get_num_targets, convert_leaf, get_max_value_f, get_min_value_f, sget_feature, convert_node, sget_node_constant, read_file, transform_data, write_file, set_double_data, get_num_features, get_data_size, get_num_parents, get_feature, get_right_leafs, get_left_leafs

eps=1e-5

def create_variables(depth,C_set):

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

    for l in range(num_leafs): #x_{l,r}

        for r in range(data_size):

            var_names.append("x_"+str(l)+"_"+str(r))

            var_types = var_types + "B"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1
            
    for l in range(num_leafs): #p_{l,t}
        
        for t in range(get_num_targets()):
            
            var_names.append("prediction_type_"+str(l)+"_"+str(t))

            var_types = var_types + "B"

            var_lb.append(0)

            var_ub.append(1)

            var_obj.append(0)

            var_value = var_value + 1
            
    for i in range(num_features): #rho_{i,j,v}
        
        for j in range(num_nodes):
            
            for v in range(len(C_set[i])):
                
                var_names.append("rho_"+str(i)+"_"+str(j)+"_"+str(v))

                var_types = var_types + "B"
    
                var_lb.append(0)
    
                var_ub.append(1)
    
                var_obj.append(0)
    
                var_value = var_value + 1
                
    for r in range(data_size):
        
        var_names.append("row_error_"+str(r))

        var_types = var_types + "C"

        var_lb.append(0)

        var_ub.append(1)

        var_obj.append(1)

        var_value = var_value + 1

    return var_names, var_types, var_lb, var_ub, var_obj

def create_rows(depth,C_set):
    
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
            
    for r in range(data_size): #constraint (1)

        for j in range(num_nodes):

            col_names = ["x_"+str(l)+"_"+str(r) for l in get_left_leafs(j,num_nodes)]

            col_values = [-1 for l in get_left_leafs(j,num_nodes)]
                        
            for i in range(num_features):
                
                for v in range(len(C_set[i])):
                    
                    if get_feature_value(r,i) > C_set[i][v]:
                        
                        col_names.append("rho_"+str(i)+"_"+str(j)+"_"+str(v))
                        
                        col_values.append(-1)
                                                
            for j2 in get_parents(j,depth):
                
                for i in range(num_features):
                
                    for v in range(len(C_set[i])):
                        
                        if get_feature_value(r,i) <= C_set[i][v] and j in get_left_nodes(j2,num_nodes):
                            
                            col_names.append("rho_"+str(i)+"_"+str(j2)+"_"+str(v))
                            
                            col_values.append(1)
                            
                        if get_feature_value(r,i) > C_set[i][v] and j in get_right_nodes(j2,num_nodes):
                            
                            col_names.append("rho_"+str(i)+"_"+str(j2)+"_"+str(v))
                        
                            col_values.append(1)
                            
            row_names.append("constraint_1_"+str(r)+"_"+str(j))

            row_values.append([col_names,col_values])

            row_right_sides.append(get_depth(j,num_nodes)-2)

            row_senses = row_senses + "L"

            row_value = row_value + 1
            
    for r in range(data_size): #constraint (1bis)

        for j in range(num_nodes):

            col_names = ["x_"+str(l)+"_"+str(r) for l in get_right_leafs(j,num_nodes)]

            col_values = [-1 for l in get_right_leafs(j,num_nodes)]
                        
            for i in range(num_features):
                
                for v in range(len(C_set[i])):
                    
                    if get_feature_value(r,i) <= C_set[i][v]:
                        
                        col_names.append("rho_"+str(i)+"_"+str(j)+"_"+str(v))
                        
                        col_values.append(-1)
                        
            for j2 in get_parents(j,depth):
                
                for i in range(num_features):
                
                    for v in range(len(C_set[i])):
                        
                        if get_feature_value(r,i) <= C_set[i][v] and j in get_left_nodes(j2,num_nodes):
                            
                            col_names.append("rho_"+str(i)+"_"+str(j2)+"_"+str(v))
                            
                            col_values.append(1)
                            
                        if get_feature_value(r,i) > C_set[i][v] and j in get_right_nodes(j2,num_nodes):
                            
                            col_names.append("rho_"+str(i)+"_"+str(j2)+"_"+str(v))
                        
                            col_values.append(1)

            row_names.append("constraint_1bis_"+str(r)+"_"+str(j))

            row_values.append([col_names,col_values])

            row_right_sides.append(get_depth(j,num_nodes)-2)

            row_senses = row_senses + "L"

            row_value = row_value + 1
            
    for j in range(num_nodes): #constraint (2)
        
        col_names, col_values = [], []
        
        for i in range(num_features):
            
            for v in range(len(C_set[i])):
                
                col_names.append("rho_"+str(i)+"_"+str(j)+"_"+str(v))
                
                col_values.append(1)
                
        row_names.append("constraint_2_"+str(j))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    for r in range(data_size): #constraint (3)
        
        for l in range(num_leafs):
            
            col_names, col_values = [], []
                                        
            col_names.append("x_"  + str(l) + "_" + str(r)) #x_{l,s}
            
            col_values.append(1)
                    
            for t in range(get_num_targets()):
                
                if TARGETS[t] == get_target(r):

                    col_names.append("prediction_type_" + str(l) + "_" + str(t))

                    col_values.append(-1)

            col_names.append("row_error_" + str(r))

            col_values.append(-1)
            
            row_names.append("constraint_3_" + str(r) + "_" +str(l))
        
            row_values.append([col_names,col_values])
    
            row_right_sides.append(0)
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1
            
    for l in range(num_leafs): #constraint (4)

        col_names = ["prediction_type_" + str(l) + "_" + str(t) for t in range(get_num_targets())]

        col_values = [1 for t in range(get_num_targets())]

        row_names.append("constraint_4_"+str(l))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    for r in range(data_size): #constraint (4)

        col_names = ["x_" + str(l) + "_" + str(r) for l in range(num_leafs)]

        col_values = [1 for l in range(num_leafs)]

        row_names.append("constraint_4_"+str(l))

        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1

    return row_names, row_values, row_right_sides, row_senses


def solve_ILP(depth,C_set):

    prob = cplex.Cplex()

    data_size = get_data_size()

    prob.objective.set_sense(prob.objective.sense.minimize)

    var_names, var_types, var_lb, var_ub, var_obj = create_variables(depth,C_set)

    prob.variables.add(obj = var_obj, lb = var_lb, ub = var_ub, types = var_types, names = var_names)

    row_names, row_values, row_right_sides, row_senses = create_rows(depth,C_set)

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
    
    prob.solve()
    
    display_prob_lite(prob,"primal")

    print

    print "Solution status = " , prob.solution.get_status(), ":", prob.solution.status[prob.solution.get_status()]

    if "infeasible" in prob.solution.status[prob.solution.get_status()]:

        return []

    print "Solution value  = ", prob.solution.get_objective_value()
    
    print "Accuracy = ", (data_size-prob.solution.get_objective_value())/data_size
    
    
    
def compute_C_set(inputfile):
    
    num_features = get_num_features()
    
    C = []
    
    df = pd.read_csv(inputfile+".transformed",sep=';')
        
    for i in range(num_features):
        
        matrix = df.as_matrix([df.columns[i]]).squeeze()
        
        uni = np.unique(matrix)
        
        C.append(uni)
            
    return C
        
        


def main(argv):
    
   global TARGETS

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

   create_instance(inputfile)
   
   TARGETS.sort()
   
   C_set = compute_C_set(inputfile)

   solve_ILP(inputdepth,C_set)
   
   return
   
   
   
ws=main(['-fIndiansDiabetes.csv', '-d 1'])
    