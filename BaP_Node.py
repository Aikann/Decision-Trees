# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:44:53 2018

@author: Guillaume
"""

class BaP_Node:
    
    def __init__(self,segments_set,prob):
        
        self.prob=prob
        self.segments_set=segments_set
        
    def solve_relaxation(self): #do CG until the master problem is solved
        
        convergence = False
        
        while not convergence:
            
            self.prob.solve()
            
            segments_to_be_added = solve_pricing(prob)
            
            convergence = check_convergence(prob)
                        
            self.add_segments(segments_to_be_added)
        
        self.prob.solve() 
        self.solution_value = self.prob.solution.get_objective_value()
        self.solution = self.prob.solution.get_values()
        
    def add_segments(self): #TODO
        
        return
    
    def create_children_by_branching(self,branching_variable): #TODO
        
        return

    def solve_branch_and_price(self): #solve the branch and price problem recursively
        
        global best_solution
        global best_solution_value
        
        self.solve_relaxation()
        
        self.add_segments()
        
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
                
                self.create_children_by_branching(var)
                
                return min(self.child1.solve_branch_and_price(), self.child2.solve_branch_and_price())