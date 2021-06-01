# -*- coding: utf-8 -*-
"""
Created on Tue May 11 10:20:25 2021

@author: calle
"""
import gurobipy as gp 
from gurobipy import GRB
import fctpdualsp as dual
import fctphomosystem as homo
import fctprmp as rmp
import pandas as pd
import time


### The Benders algorithm

#Define input data
benders_start_time = time.time()
I, s = gp.multidict({
    ('i1'):   10,
    ('i2'):  30,
    ('i3'):  40,
    ('i4'):  20,
    })

J, d = gp.multidict({
    ('j1'):   20,
    ('j2'):  50,
    ('j3'):  30,
    })

c = {
    ('i1', 'j1'): 2,
    ('i1', 'j2'): 3, 
    ('i1', 'j3'): 4,
    ('i2', 'j1'): 3,
    ('i2', 'j2'): 2,
    ('i2', 'j3'): 1,
    ('i3', 'j1'): 1,
    ('i3', 'j2'): 4,
    ('i3', 'j3'): 3,
    ('i4', 'j1'): 4,
    ('i4', 'j2'): 5,
    ('i4', 'j3'): 2  
}

f = {
    ('i1', 'j1'): 10,
    ('i1', 'j2'): 30,
    ('i1', 'j3'): 20,
    ('i2', 'j1'): 10,
    ('i2', 'j2'): 30,
    ('i2', 'j3'): 20,
    ('i3', 'j1'): 10,
    ('i3', 'j2'): 30,
    ('i3', 'j3'): 20,
    ('i4', 'j1'): 10,
    ('i4', 'j2'): 30,
    ('i4', 'j3'): 20  
}

M = {(i,j): min(s[i], d[j]) for i in I for j in J}

#Set of dual subproblem feasible extreme points points
P = []

#Set of dual subproblem unbounded rays
R = []

#parameters to save dsp solution
ub = {}
vb = {}
wb = {}

#parameters to save homogeneous system solution
ubu = {}
vbu = {}
wbu = {}

#Benders Algorithm
#Define intial feasible solution of the rmp
yb = {(i,j): 1 for i in I for j in J}

print ('Intial Solution:')
for i in I:
    for j in J:
        print('y( %s , %s )= %g' % (i, j, yb[i,j])) 


#Intialize bounds
lower_bound = -99999
upper_bound = +99999999
epsilon = 0.01

#iteration is used as a parameter to print results. It does not affect the logic of the algorithm
iteration = 0

l_iterations = []
l_type_cut= []
l_dual_of = []
l_fy = []
l_ub = []
l_lb = []
l_master_time = []
l_dual_time = []
l_homo_time = []

aux_start_time = 0
aux_end_time = 0

original_solution_found = False
stop_criteria = False

while not(original_solution_found):
    iteration +=1
    l_iterations.append(iteration)
    
    print()
    print("Iteration " + str(iteration))
    
    #Solve dual subproblem and save the outputs from the function
    aux_start_time = time.time()
    solution_dsp = dual.solve_dsp(I, J, s, d, c, f, M, yb)
    aux_end_time = time.time()
    l_dual_time.append(aux_end_time - aux_start_time)
    #This queries the first element of the output tuple and ask if it found an optimal solution
    if solution_dsp[0]=='optimal':
        #print solution. This does not affect the logic of the algorithm
        l_type_cut.append('optimality')
        l_homo_time.append('')
        print('The dual subproblem is bounded')
        print('An extrene point is defined by')
        for i in I:
            print('u( %s )= %g' % (i,solution_dsp[1][i]))
        for j in J:
            print('v( %s )= %g' % (j,solution_dsp[2][j]))
        for i in I:
            for j in J:
                print('w( %s , %s )= %g' % (i,j,solution_dsp[3][i,j]))
        
        print()
        print('The dual objective function is: ' + str(solution_dsp[4]))
        print('fy = ' + str(sum(f[i,j]*yb[i,j] for i in I for j in J)))    
        print('The current upper bound is: ' + str(upper_bound))
        l_dual_of.append(solution_dsp[4])
        l_fy.append(sum(f[i,j]*yb[i,j] for i in I for j in J))
        
        
        #check if you need to update the upper bound
        upper_bound_aux = sum(f[i,j]*yb[i,j] for i in I for j in J) + solution_dsp[4] 
        upper_bound = min(upper_bound_aux, upper_bound)
        
        l_ub.append(upper_bound)
        
        
        print('The new upper bound is: ' + str(upper_bound))
        #If the stop criteria has already being met and the dsp is feasible, 
        #it meas that this solution can be used to retrieve the original solution
        if stop_criteria:
            l_lb.append(lower_bound)
            l_master_time.append(0)
            break
        
        print('Add an optimaility cut to the master and solve it')
        #add one element to the set of extreme points
        p_aux = "p" + str(len(P)+1)
        P.append(p_aux)
    
        #assign the values of ub, vb, wb (solution of the dsp, which becomes parameters in the RMP)
        #These parameters are indexed in P (set of extreme feasible points)
        for i in I:
            ub[i,p_aux] =  solution_dsp[1][i]
        for j in J:
            vb[j, p_aux] = solution_dsp[2][j]
        for i in I:
            for j in J:
                wb[i,j,p_aux] =  solution_dsp[3][i,j]        
    else:
               
        #solve the homogeneous system to find the unboundnes rays
        aux_start_time = time.time()
        solution_homo = homo.solve_homo(I, J, s, d, f, M, yb)
        aux_end_time = time.time()
        l_homo_time.append(aux_end_time-aux_start_time)
                
        l_type_cut.append('feasability')
        l_dual_of.append('')
        l_fy.append('')
        l_ub.append(upper_bound)
        print()
        print('The dsp was unbounded, then solve the homogeneous system to find an extreme ray')
        for i in I:
            print('u( %s )= %g' % (i,solution_homo[0][i]))
        for j in J:
            print('v( %s )= %g' % (j,solution_homo[1][j]))
        for i in I:
            for j in J:
                print('w( %s , %s )= %g' % (i,j,solution_homo[2][i,j]))
        print('Add a feasability cut to the master and solve it: ')
        #add one element to the set of unbounded rays
        r_aux = "r" + str(len(R)+1)
        R.append(r_aux)
        #assign the values of ubu, vbu, wbu (solution of the homogeneus system, which becomes parameters in the RMP)
        #These parameters are indexed in R (set of extreme unbounded rays)
        for i in I:
            ubu[i,r_aux] =  solution_homo[0][i]
        for j in J:
            vbu[j, r_aux] = solution_homo[1][j]
        for i in I:
            for j in J:
                wbu[i,j,r_aux] =  solution_homo[2][i,j]
        
                
    #solve the RMP
    aux_start_time = time.time()
    solution_rmp = rmp.solve_rmp(I, J, P, R, s, d, f, M, ub, vb, wb, ubu, vbu, wbu)
    aux_end_time = time.time()
    l_master_time.append(aux_end_time - aux_start_time)
    print('the current lower bound is: ' + str(lower_bound))
    lower_bound = solution_rmp[1]
    print('the new lower bound is: ' + str(lower_bound))
    #update yb
    yb = solution_rmp[0]
    print('the new value of yb is: ')
    for i in I:
        for j in J:
            print('y( %s , %s )= %g' % (i, j, yb[i,j]))    
    
    l_lb.append(lower_bound)
    if (upper_bound - lower_bound)<epsilon:
        stop_criteria = True
    
    
    
#Retrieve the solution of the original problem: the dual value of the last subproblem
#if (upper_bound - lower_bound)<=epsilon:
    #solve again the dual subproblem
#    solution_dsp = dual.solve_dsp(I, J, s, d, c, f, M, yb)
    
print('The solution to the original problem is: ')
for i in I:
   for j in J:
       print('x( %s , %s )= %g' % (i, j, solution_dsp[5][i,j] ))
       print('y( %s , %s )= %g' % (i, j, yb[i,j]))    
    
print('The total cost is: ' + str(lower_bound))

df_algorithm_evolution = pd.DataFrame({'Iteration':l_iterations, 'Type of Cut':l_type_cut, 'Dual Objective Function': l_dual_of, 'fy':l_fy, 'UB': l_ub, 'LB': l_lb, 
                                       'dual time':l_dual_time, 'homo time': l_homo_time, 'master time': l_master_time })

benders_end_time = time.time()

benders_total_time = benders_end_time - benders_start_time

master_total_time = df_algorithm_evolution['master time'].sum()
subproblem_total_time = df_algorithm_evolution['dual time'].sum() + df_algorithm_evolution[df_algorithm_evolution['Type of Cut']=='feasible']['Type of Cut'].sum()

print('Benders Total Time: ' + str(benders_total_time))
print('master total time: ' + str(master_total_time))
print('subproblem total time: ' + str(subproblem_total_time))
print('percentage solving master: ' + str(master_total_time/benders_total_time))
print('percentage solving subproblem: ' + str(subproblem_total_time/benders_total_time))


#print("yupi I finish")
#print('LB=')
#print(lower_bound)
#print('UB=')
#print(upper_bound)









