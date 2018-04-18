# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:44:53 2018

@author: Guillaume
"""

from learn_tree_funcs import get_data_size
from cplex_problems_CG import construct_master_problem
from nodes_external_management import give_solution_type, solve_pricing, check_unicity, adapt_segments_set, hash_seg
import time
import matplotlib.pyplot as plt


def obtain_depth2(d):
    
    global depth
    depth=d


class BaP_Node:
    
    def __init__(self,segments_set,prob,ID,parent,branched_rows,branched_leaves,H):
        
        self.prob=prob #cplex problem
        self.segments_set=segments_set #list containing lists of sets for each leaf
        self.ID = ID
        self.parent = parent
        self.branched_rows = branched_rows #list of branched rows
        self.branched_leaves = branched_leaves #list of corresponding leaves
        self.H = H #hash table for segments
        
    def solve_relaxation(self): #do CG until the master problem is solved
        
        plt.figure()
                
        plt.show()
        
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
        
        self.prob = construct_master_problem(depth,self.segments_set)
        
        convergence = False
        
        global count_iter
        
        count_iter=1
        
        previous_solution = float('+inf')
        
        not_imp=0
        
        pricing_method=1
        
        while not convergence:
            
            #b=time.time()
            
            self.prob.solve()
            
            print(self.prob.solution.get_values())
            
            #print("MP : "+str(time.time()-b))
            
            #a=time.time()
            
            if count_iter%50==0:
                
                pricing_method=1
                
            else:
                
                #pricing_method=2
                
                
            
                if previous_solution-0.01<=self.prob.solution.get_objective_value()<=previous_solution+0.01:
                    
                    not_imp += 1
                    
                if not_imp>20 and pricing_method!=3:
                    
                    not_imp, pricing_method = 0, 3
                    
                elif not_imp>15 and pricing_method!=2:
                    
                    not_imp, pricing_method = 0, 2
                    
                
                    
            pricing_method=1   
                                
            previous_solution = self.prob.solution.get_objective_value()
                        
            segments_to_be_added, convergence = solve_pricing(self.prob,self.segments_set,self.branched_rows,self.branched_leaves,self.ID,pricing_method)
                                
            self.add_segments(segments_to_be_added,True)#(pricing_method==3))
            
            #print("Pricing : "+str(time.time()-a))
            
            count_iter=count_iter+1
            
            plt.scatter(count_iter,self.prob.solution.get_objective_value(),color='g')
            
            plt.pause(0.01)
            
            if count_iter%200==0:
            
                print("Current solution value "+str(self.prob.solution.get_objective_value()))
            
                print("Number of segments "+str(sum([len(self.segments_set[l]) for l in range(len(self.segments_set))])))
                
                #check_unicity(self.segments_set)
                                
                #input()
                                
                time.sleep(0.1)
                
            #c=time.time()
            
            if not convergence:
                                    
                self.prob = construct_master_problem(depth,self.segments_set)
            
            #print("Construction of MP : "+str(time.time()-c)) 
        
        self.solution_value = self.prob.solution.get_objective_value()
        self.solution = self.prob.solution.get_values()
        self.solution_type = give_solution_type(self.prob)
        
    def solve_warp_up(self): #TODO ; return a tuple is_truly_infeasible, segments so that the master problem can be feasible
        
        return
        
    def add_segments(self,segs_to_add,safe_insertion=False):
                
        for l in range(len(self.segments_set)):
            
            if segs_to_add[l]!=[]:
                
                if safe_insertion:
                                                                                                                    
                    if hash_seg(segs_to_add[l]) not in self.H[l]:
                    
                        self.segments_set[l].append(segs_to_add[l])
                                                
                        self.H[l].append(hash_seg(segs_to_add[l]))
                            
                else:
                        
                    self.segments_set[l].append(segs_to_add[l])
                                            
                    self.H[l].append(hash_seg(segs_to_add[l]))
            
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