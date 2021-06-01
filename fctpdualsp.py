# -*- coding: utf-8 -*-
"""
Created on Mon May 10 10:41:43 2021

@author: calle
"""

import gurobipy as gp 
from gurobipy import GRB

### The dual subproblem
def solve_dsp(I, J, s, d, c, f, M, yb):
    #Define model
    dsp = gp.Model()
    
    #Define variables
    u =  dsp.addVars(I, name = 'u')
    v = dsp.addVars(J, name = 'v')
    w = dsp.addVars(I, J, name = 'w')
    
    #Define constraint
    cConstraint1 = dsp.addConstrs((-u[i] + v[j] -w[i,j]<=c[i,j] for i in I for j in J), name = 'constraint1')
    
    #Define Objective Function
    dsp.setObjective(gp.quicksum(-s[i]*u[i] for i in I) + gp.quicksum(d[j]*v[j] for j in J) + gp.quicksum(-M[i,j]*yb[i,j]*w[i,j] for i in I for j in J), GRB.MAXIMIZE)
    
    #Define solver parameters
    #Mute the optimze output
    dsp.Params.LogToConsole = 0

    dsp.optimize()
    
    #2 means that an optimal solution could be found.
    #status codes: https://www.gurobi.com/documentation/9.1/refman/optimization_status_codes.html#sec:StatusCodes
    if dsp.status == 2:
        #retrieve the solution
        ou = dsp.getAttr('x', u)
        ov = dsp.getAttr('x', v)
        ow = dsp.getAttr('x', w)
        oof = dsp.objVal
        x = dsp.getAttr('pi', cConstraint1)
        
        return('optimal',ou, ov, ow, oof, x)
    else:
        return('unbounded')