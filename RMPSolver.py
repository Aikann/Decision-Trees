# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 10:25:53 2018

@author: Guillaume
"""

from cplex_problems_CG import construct_master_problem, add_variable_to_master_and_rebuild

def create_new_master(inputdepth,segments_set):
    
    return construct_master_problem(inputdepth,segments_set)

def solveRMP(prob):
    
    prob.solve()
    
def add_column(depth,prob,inputdepth,segments_set,segment_to_add,leaf):
    
    return add_variable_to_master_and_rebuild(depth,prob,inputdepth,segments_set,segment_to_add,leaf)