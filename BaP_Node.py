# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:44:53 2018

@author: Guillaume
"""

from RMPSolver import add_column, solveRMP, display_RMP_solution_dual, display_RMP_solution_primal, RMP_add_f_constraint, add_column2, create_new_master
from nodes_external_management import give_solution_type, check_unicity, adapt_segments_set, hash_seg

from PricingSolver import solve_pricing
import time
import matplotlib.pyplot as plt
from copy import deepcopy as dc


def obtain_depth2(d):
    
    global depth
    depth=d


class BaP_Node:
    
    def __init__(self,segments_set,prob,ID,parent,branched_rows,H,branched_f):
        
        self.prob=prob #cplex problem
        self.segments_set=segments_set #list containing lists of sets for each leaf
        self.ID = ID
        self.parent = parent
        self.branched_rows = branched_rows #list of branched rows
        self.H = H #hash table for segments
        self.branched_f = branched_f
        
    def explore(self): #do CG until the master problem is solved
        
        plt.figure()
                
        plt.show()
                        
        #print(self.segments_set)
                
        convergence = False
        
        solveRMP(self.prob)
                        
        if give_solution_type(self.prob) == 'infeasible':
            
            self.solution_type = 'infeasible'
            self.solution_value = float('+inf')
            
            return
        
        global count_iter
        
        count_iter=1
        
        #previous_solution = float('+inf')
        
        #not_imp=0
        
        #pricing_method=3
        
        red_cost = float('-inf')
        
        while not convergence:
            """
            if count_iter==2:
                
                print(self.segments_set)
            
                del self.segments_set[0][0]
                
                self.prob = create_new_master(depth, self.segments_set)
            """
            c=time.time()
                        
            solveRMP(self.prob)
            
            #display_RMP_solution_primal(depth,self.prob,count_iter,self.segments_set)
            
            #display_RMP_solution_dual(depth,self.prob,count_iter)
            
            print(count_iter,"Time MP :",time.time()-c)
            
            #print(self.prob.solution.get_values())
                                    
            if red_cost >= -0.01:
                
                pricing_method=1
                
            else:
                
                #pricing_method=2
                
                """
                
                if previous_solution-0.01<=self.prob.solution.get_objective_value()<=previous_solution+0.01:
                    
                    not_imp += 1
                    
                if not_imp>20 and pricing_method!=3:
                    
                    not_imp, pricing_method = 0, 3
                    
                elif not_imp>15 and pricing_method!=2:
                    
                    not_imp, pricing_method = 0, 2
                    
                """
                    
                pricing_method = 3
                    
            #previous_solution = self.prob.solution.get_objective_value()
            
            b=time.time()
                        
            segments_to_be_added, convergence, red_cost = solve_pricing(depth,
            self.prob,self.segments_set,self.branched_rows,
            self.branched_f,self.ID,pricing_method)
            
            print(count_iter,"Time pricing :",time.time()-b)
            
            plt.scatter(count_iter,self.prob.solution.get_objective_value(),color='g')
            
            plt.pause(0.01)
            
            if count_iter%1==0:
            
                print("Current solution value "+str(self.prob.solution.get_objective_value()))
            
                print("Number of segments "+str(sum([len(self.segments_set[l]) for l in range(len(self.segments_set))])))
                
                #check_unicity(self.segments_set)
                                                                       
                print(self.segments_set)
                
                print(segments_to_be_added)
                
                #display_RMP_solution_dual(depth,self.prob,count_iter)
                
                #display_RMP_solution_primal(depth,self.prob,count_iter,self.segments_set)
                
                input()
                                
                time.sleep(0.1)
                
            a=time.time()
            
            #print("Full set",self.segments_set)
            
            #print("seg to be added",segments_to_be_added)
            
            previous_seg_set = dc(self.segments_set)
            
            #print("Full set after addition",self.segments_set)
                        
            if not convergence:
                
                self.add_segments(segments_to_be_added,True)
                                                    
                self.prob = add_column(depth,self.prob,depth,previous_seg_set,segments_to_be_added,self.segments_set)
                
            print(count_iter,"Time MP construction :",time.time()-a)
            
            
            """
            a=time.time()
                
            if not convergence:
                
                self.prob = create_new_master(depth,self.segments_set)
                
            print(count_iter,time.time()-a)
              """    
            count_iter=count_iter+1
            
            
        
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
                    
    def create_children_by_branching_on_f(self,i,j):
                
        child1_prob = RMP_add_f_constraint(self.prob,i,j,1)
                
        child1_branch_f = dc(self.branched_f)
        
        child1_branch_f.append((i,j))
        
        self.child1 = BaP_Node(dc(self.segments_set),child1_prob,self.ID+"1",self,dc(self.branched_rows),dc(self.H),child1_branch_f)
                
        child0_prob = RMP_add_f_constraint(self.prob,i,j,0)
        
        child0_branch_f = dc(self.branched_f)
        
        child0_branch_f.append((i,j))
        
        self.child0 = BaP_Node(dc(self.segments_set),child0_prob,self.ID+"0",self,dc(self.branched_rows),dc(self.H),child0_branch_f)
        
        return
    
    def create_children_by_branching_on_row(self,row,leaf):
        
        child1_segments, H1 = adapt_segments_set(self.segments_set,row,leaf,1)
        
        child1_prob = create_new_master(depth,child1_segments)
        
        child1_branched_rows = dc(self.branched_rows)
        
        child1_branched_rows.append((row,leaf))
        
        self.child1 = BaP_Node(child1_segments,child1_prob,self.ID+"1",self,child1_branched_rows,H1,self.branched_f)
        
        child0_segments, H0 = adapt_segments_set(self.segments_set,row,leaf,0)
        
        child0_prob = create_new_master(depth,child0_segments)
        
        child0_branched_rows = dc(self.branched_rows)
        
        child0_branched_rows.append((row,leaf))
        
        self.child0 = BaP_Node(child0_segments,child0_prob,self.ID+"0",self,child0_branched_rows,H0,self.branched_f)
        
        return
                    
    """ NOT FULLY IMPLEMENTED
            
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
                
    """