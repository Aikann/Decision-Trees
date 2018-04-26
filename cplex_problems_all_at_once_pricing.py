# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 10:00:09 2018

@author: Guillaume
"""

from learn_tree_funcs import get_left_leafs, get_right_leafs
from learn_tree_funcs import get_num_features, get_data_size, get_feature_value
import cplex

def create_variables_pricing_all_at_once(depth,master_prob):
        
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
        
    #compute useful sums of dual values
    
    A_i_l, B_i_l = [[] for l in range(num_leafs)], [[] for l in range(num_leafs)]
    
    for leaf in range(num_leafs):
    
        for i in range(num_features):
            
            s=0
            
            for j in range(num_nodes):
                
                left_leaves = get_left_leafs(j,num_nodes)
                
                if leaf in left_leaves:
                                        
                    s = s + master_prob.solution.get_dual_values("constraint_15_"+str(i)+"_"+str(j)+"_"+str(leaf))
                                        
                #print(s)
                
                if s>0:
                    
                    print(s)
                    
                    input("STOP B")
                    
            B_i_l[leaf].append(-s)
        
        for i in range(num_features):
            
            s=0
            
            for j in range(num_nodes):
                
                right_leaves = get_right_leafs(j,num_nodes)
                
                if leaf in right_leaves:
                    
                    s = s + master_prob.solution.get_dual_values("constraint_16_"+str(i)+"_"+str(j)+"_"+str(leaf))
                                        
                #print(s)
                
                if s>0:
                    
                    print(s)
                    
                    input("STOP A")
                    
            A_i_l[leaf].append(-s)

    print("SUM DUALS :",A_i_l," ",B_i_l)
    # z_{r,l}, main decision variables
    
    for leaf in range(num_leafs):
        
        #print("SUM0",sum([duals[constraint_indicators[2] + r2] + duals[constraint_indicators[4] + r2*num_leafs] for r2 in [0, 1, 4, 8, 11, 15, 16, 17, 18, 19, 21, 23, 24, 27, 28, 29]])+duals[constraint_indicators[3]])
            
        #print("SUM1",sum([duals[constraint_indicators[2] + r3] + duals[constraint_indicators[4] + r3*num_leafs + 1] for r3 in [2, 3, 5, 6, 7, 9, 10, 12, 13, 14, 20, 22, 25, 26]])+duals[constraint_indicators[3]+1])

        for r in range(data_size):
        
            var_names.append("row_" + str(leaf) + "_" + str(r))
    
            var_types = var_types + "B"
    
            var_lb.append(0)
    
            var_ub.append(1)
            
            #print(r,leaf,"C_{r,l} ",duals[constraint_indicators[2] + r] + duals[constraint_indicators[4] + r*num_leafs + leaf])
                                                            
            var_obj.append(-master_prob.solution.get_dual_values("constraint_17_"+str(r)) - master_prob.solution.get_dual_values("constraint_19_"+str(r)+"_"+str(leaf)))
    
            var_value = var_value + 1
        
    # kappa_{i,r,l}, indicate the min feature of row r
    
    for leaf in range(num_leafs):
    
        for i in range(num_features):
            
            for r in range(data_size):
                
                var_names.append("kappa_" +str(leaf) + "_" + str(r) + "_" + str(i))
            
                var_types = var_types + "B"
            
                var_lb.append(0)
            
                var_ub.append(1)
            
                var_obj.append(A_i_l[leaf][i]*get_feature_value(r,i))
            
                var_value = var_value + 1
        
    # omega_{i,r,l}, indicate the max feature of row r
    
    for leaf in range(num_leafs):
    
        for i in range(num_features):
            
            for r in range(data_size):
                
                var_names.append("omega_" + str(leaf) + "_" + str(r) + "_" + str(i))
            
                var_types = var_types + "B"
            
                var_lb.append(0)
            
                var_ub.append(1)
            
                var_obj.append(-B_i_l[leaf][i]*get_feature_value(r,i))
            
                var_value = var_value + 1
            
    return var_names, var_types, var_lb, var_ub, var_obj



def create_rows_pricing_all_at_once(depth,branched_rows,branched_f,ID,existing_segments):
    
    row_value = 0

    row_names = []

    row_values = []

    row_right_sides = []

    row_senses = ""

    num_features = get_num_features()

    data_size = get_data_size()
    
    num_leafs = 2**depth
    
    num_nodes = num_leafs - 1
    
    for l in range(num_leafs):
    
        for r in range(data_size): #constraint (32)
            
            for i in range(num_features):
    
                col_names = ["kappa_" + str(l) + "_"  + str(r) + "_" + str(i)]
        
                col_values = [1]
                
                for r2 in range(data_size):
                    
                    if get_feature_value(r2,i) < get_feature_value(r,i):
                        
                        col_names.extend(["row_" +str(l) + "_" + str(r2)])
                        
                        col_values.extend([1./data_size])
        
                row_names.append("constraint_32_"+str(l)+"_"+str(r)+"_"+str(i))
        
                row_values.append([col_names,col_values])
        
                row_right_sides.append(1)
        
                row_senses = row_senses + "L"
        
                row_value = row_value + 1
    
            
    for l in range(num_leafs):
     
        for r in range(data_size): #constraint (33)
            
            for i in range(num_features):
                
                col_names = ["omega_" + str(l) + "_" + str(r) + "_" + str(i)]
        
                col_values = [1]
                
                for r2 in range(data_size):
                    
                    if get_feature_value(r2,i) > get_feature_value(r,i):
                        
                        col_names.extend(["row_" + str(l) + "_" + str(r2)])
                        
                        col_values.extend([1./data_size])
        
                row_names.append("constraint_33_"+str(l)+"_"+str(r)+"_"+str(i))
        
                row_values.append([col_names,col_values])
        
                row_right_sides.append(1)
        
                row_senses = row_senses + "L"
        
                row_value = row_value + 1
            
    for l in range(num_leafs):
        
        for r in range(data_size): #constraint (34)
            
            col_names = ["kappa_" + str(l) + "_"  + str(r) + "_" + str(i) for i in range(num_features)]
            
            col_values = [1 for i in range(num_features)]
            
            col_names.extend(["row_" + str(l) + "_" + str(r)])
            
            col_values.extend([-num_features])
            
            row_names.append("constraint_34_"+str(l)+"_"+str(r))
    
            row_values.append([col_names,col_values])
    
            row_right_sides.append(0)
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1
            
    for l in range(num_leafs):
        
        for r in range(data_size): #constraint (35)
            
            col_names = ["omega_" + str(l) + "_" + str(r) + "_" + str(i) for i in range(num_features)]
            
            col_values = [1 for i in range(num_features)]
            
            col_names.extend(["row_" + str(l) + "_" + str(r)])
            
            col_values.extend([-num_features])
            
            row_names.append("constraint_35_"+str(l)+"_"+str(r))
    
            row_values.append([col_names,col_values])
    
            row_right_sides.append(0)
    
            row_senses = row_senses + "L"
    
            row_value = row_value + 1     
            
    for l in range(num_leafs):
        
        for i in range(num_features): #constraint (36)
            
            col_names = ["kappa_" + str(l) + "_" + str(r) + "_" + str(i) for r in range(data_size)]
            
            col_values = [1 for r in range(data_size)]
            
            row_names.append("constraint_36_"+str(l)+"_"+str(i))
    
            row_values.append([col_names,col_values])
    
            row_right_sides.append(1)
    
            row_senses = row_senses + "E"
    
            row_value = row_value + 1
        
    for l in range(num_leafs):
        
        for i in range(num_features): #constraint (37)
            
            col_names = ["omega_" + str(l) + "_" + str(r) + "_" + str(i) for r in range(data_size)]
            
            col_values = [1 for r in range(data_size)]
            
            row_names.append("constraint_37_"+str(l)+"_"+str(i))
    
            row_values.append([col_names,col_values])
    
            row_right_sides.append(1)
    
            row_senses = row_senses + "E"
    
            row_value = row_value + 1
            
    for r in range(data_size): #new contraint for "all at once" pricing problem
        
        col_names = ["row_" + str(l) + "_" + str(r) for l in range(num_leafs)]
        
        col_values = [1 for l in range(num_leafs)]
        
        row_names.append("constraint_partition_"+str(r))
    
        row_values.append([col_names,col_values])

        row_right_sides.append(1)

        row_senses = row_senses + "E"

        row_value = row_value + 1
        
    if len(branched_f)>0: # branching constraints on f
        
        for (i,j) in branched_f:
            
            print("Hey",i,j)
            
            for l1 in get_left_leafs(j,num_nodes):
                
                for l2 in get_right_leafs(j,num_nodes):
                    
                    print(l1,l2)
                    
                    col_names = ["omega_" + str(l1) + "_" + str(r) + "_" + str(i) for r in range(data_size)]
                    
                    col_values = [get_feature_value(r,i) for r in range(data_size)]
                    
                    col_names.extend(["kappa_" + str(l2) + "_" + str(r) + "_" + str(i) for r in range(data_size)])
                    
                    col_values.extend([-get_feature_value(r,i) for r in range(data_size)])
                    
                    row_names.append("constraint_branching_f_"+str(i)+"_"+str(j)+"_"+str(l1)+"_"+str(l2))
        
                    row_values.append([col_names,col_values])
    
                    row_right_sides.append(0)
    
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



def contruct_pricing_problem_all_at_once(depth,master_prob,branched_rows,branched_f,ID,existing_segments):
    
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