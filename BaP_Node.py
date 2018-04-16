# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:44:53 2018

@author: Guillaume
"""

from learn_tree_funcs import get_data_size
from cplex_problems_CG import construct_master_problem, construct_pricing_problem
import time

def obtain_depth(d):
    global depth
    depth=d
    
def check_unicity(segments_set):
    
    check=True
    
    for l in range(len(segments_set)):
        
        for s1 in range(len(segments_set[l])):
            
            for s2 in range(s1,len(segments_set[l])):
                
                if s1!=s2 and segments_set[l][s1]==segments_set[l][s2]:
                
                    check=False
                    
        print(check)
        
        if not check:
            
            input()
    
def extract_rows_pricing(pricing_prob): #return the segment given by the pricing pb
    
    seg, sol = [], pricing_prob.solution.get_values()
    
    for r in range(get_data_size()):
        
        if sol[r] == 1:
            
            seg.append(r)
    
    return seg

def give_solution_type(prob): #return a string saying if the solution is integral, continuous or infeasible
    
    if "infeasible" in prob.solution.status[prob.solution.get_status()]:

        return "infeasible"
    
    else:
        
        for i in prob.solution.get_values():
            
            if (float(i) <= round(i) - 0.01) or (float(i) >= round(i) + 0.01):
                
                return "continuous"
            
        return "integer"
    
def adapt_segments_set(segments_set,row,leaf,branching): #this function adapts the segments_set according to the branching rule
    
    new_segments_set=[[] for l in range(len(segments_set))]
    
    if branching==1:
        
        for l in range(len(segments_set)):
            
            for s in segments_set[l]:
            
                if l==leaf and row in s:
                    
                    new_segments_set[l].append(s)
                    
                elif l!=leaf and row not in s:
                    
                    new_segments_set[l].append(s)
                    
    else:
        
        for l in range(len(segments_set)):
            
            for s in segments_set[l]:
            
                if l==leaf and row not in s:
                    
                    new_segments_set[l].append(s)
                    
                elif l!=leaf and row in s:
                    
                    new_segments_set[l].append(s)    
    
    return new_segments_set

def solve_pricing_given_leaf(prob,leaf,branched_rows,branched_leaves,ID,existing_segments): #return a tuple (segments, obj_value). segments is actually a list of segments.
    
    rows_to_be_excluded, rows_to_be_included = [], []
    
    for l in range(len(branched_leaves)):
        
        if branched_leaves[l] == leaf:
            
            if ID[l] == 1:
                
                rows_to_be_included.append(branched_rows[l])
                
            else:
                
                rows_to_be_excluded.append(branched_rows[l])
                
    pricing_prob = construct_pricing_problem(depth,prob,rows_to_be_excluded,rows_to_be_included,leaf,existing_segments)
        
    pricing_prob.solve()
        
    obj_value = pricing_prob.solution.get_objective_value()
    
    from cplex_problems_CG import constraint_indicators
    
    obj_value = obj_value + prob.solution.get_dual_values()[constraint_indicators[3] + leaf]
    
    segment = extract_rows_pricing(pricing_prob)
        
    return segment, obj_value

def solve_pricing(prob,segments_set,branched_rows,branched_leaves,ID): #return a tuple (segments_to_be_added, convergence)
    
    num_leafs = len(segments_set)
    
    pricing_method=1
    
    segments_to_be_added, obj_values = [], []
    
    if pricing_method==1:
    
        for l in range(num_leafs): # TODO ; implement new pricing_method
            
            segments, value = solve_pricing_given_leaf(prob,l,branched_rows,branched_leaves,ID,segments_set[l])
            
            segments_to_be_added.append(segments)
            
            obj_values.append(value)
                        
            print("Reduced cost ",str(value))
            
    elif pricing_method==2:
        
        s=0
        
    return segments_to_be_added, (min(obj_values) > -0.01)

class BaP_Node:
    
    def __init__(self,segments_set,prob,ID,parent,branched_rows,branched_leaves):
        
        self.prob=prob #cplex problem
        self.segments_set=segments_set #list containing lists of sets for each leaf
        self.ID = ID
        self.parent = parent
        self.branched_rows = branched_rows #list of branched rows
        self.branched_leaves = branched_leaves #list of corresponding leaves
        
    def solve_relaxation(self): #do CG until the master problem is solved
        
        self.prob.solve()
        
        print(self.segments_set)
                
        if give_solution_type(self.prob)=='infeasible': #if master problem is infeasible in the first place...
            
            is_truly_infeasible, segments = self.solve_warm_up() #check if it is really an infeasible problem
            
            if is_truly_infeasible: #if yes, just return infeasibility
                
                self.solution_type = 'infeasible'
                self.solution_value = float('+inf')
                
                return
            
            else: #if no, add the necessary segments, and proceed to the "usual" algorithm
                
                self.add_segments(segments)
        
        self.prob = construct_master_problem(depth,self.segments_set)# TODO ; cuurently working, but can be improved : no need to reconstruct the constraints, just the variables
        
        convergence = False
        
        count=1
        
        while not convergence:
            
            b=time.time()
            
            self.prob.solve()
            
            print("MP : "+str(time.time()-b))
            
            a=time.time()
            
            segments_to_be_added, convergence = solve_pricing(self.prob,self.segments_set,self.branched_rows,self.branched_leaves,self.ID)
                                
            print("Pricing : "+str(time.time()-a))
            
            count=count+1
            
            if count%100==0:
            
                print("Current solution value "+str(self.prob.solution.get_objective_value()))
            
                print("Number of segments "+str(sum([len(self.segments_set[l]) for l in range(len(self.segments_set))])))
                
                input()
                
                #check_unicity(self.segments_set)
                
                time.sleep(0.01)
                
            c=time.time()
            
            self.add_segments(segments_to_be_added)
            
            if not convergence:
                                    
                self.prob = construct_master_problem(depth,self.segments_set)
            
            print("Construction of MP : "+str(time.time()-c)) 
        
        self.solution_value = self.prob.solution.get_objective_value()
        self.solution = self.prob.solution.get_values()
        self.solution_type = give_solution_type(self.prob)
        
    def solve_warp_up(self): #TODO ; return a tuple is_truly_infeasible, segments so that the master problem can be feasible
        
        return
        
    def add_segments(self,segs_to_add):
                
        for l in range(len(self.segments_set)):
                        
            self.segments_set[l].append(segs_to_add[l])
            
    def select_var_to_branch(self): #return a tuple (row, leaf)
        
        global VARS
    
        best_row, best_leaf, best_score = None, None, 0
        
        sol=self.prob.solution.get_values()
        
        for r in range(get_data_size()):
            
            for l in range(len(self.segments_set)):
                
                score=0
                
                for s in self.segments_set[l]:
                    
                    if r in s:
                
                        score = score + sol[VARS["segment_leaf_"+str(s)+"_"+str(l)]]
                        
                if score > best_score and score < 0.99:
                    
                    best_row, best_leaf, best_score = r, l, score
        
        return best_row, best_leaf
            
    def create_children_by_branching(self,row,leaf):
        
        child1_segments = adapt_segments_set(self.segments_set,row,leaf,1)
        
        child1_prob = construct_master_problem(child1_segments,depth)
        
        self.child1 = BaP_Node(child1_segments,child1_prob,self.ID.append(1),self,self.branched_rows.append(row),self.branched_leaves.append(leaf))
        
        child0_segments = adapt_segments_set(self.segments_set,row,leaf,0)
        
        child0_prob = construct_master_problem(child0_segments,depth)
        
        self.child0 = BaP_Node(child0_segments,child0_prob,self.ID.append(0),self,self.branched_rows.append(row),self.branched_leaves.append(leaf))
        
        return

    def solve_branch_and_price(self): #solve the branch and price problem recursively
        
        global best_solution
        global best_solution_value
        
        self.solve_relaxation()
                
        if self.solution_type=='integer': 
            
            if self.solution_value < best_solution_value:
            
                best_solution=self.solution
                best_solution_value=self.solution_value
            
            return self.solution_value
        
        elif self.solution_type=='infeasible':
            
            return float('+inf')
        
        else:
            
            if self.solution_value > best_solution_value:
                
                return self.solution_value
            
            else:
                
                row, leaf = self.select_var_to_branch()
                
                self.create_children_by_branching(row,leaf)
                
                return min(self.child1.solve_branch_and_price(), self.child2.solve_branch_and_price())