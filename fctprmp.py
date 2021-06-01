# -*- coding: utf-8 -*-
"""
Created on Mon May 10 17:45:17 2021

@author: calle
"""
import gurobipy as gp 
from gurobipy import GRB

### The Relaxed Master Problem


def solve_rmp(I, J, P, R, s, d, f, M, ub, vb, wb, ubu, vbu, wbu):
    #Define model
    rmp = gp.Model()
    
    #Define variables
    y = rmp.addVars(I, J, vtype = GRB.BINARY, name = 'y')
    n = rmp.addVar(vtype = GRB.CONTINUOUS, lb = -GRB.INFINITY)
    
    #Define constraint
    cOptimalityCut = rmp.addConstrs((n>= gp.quicksum(-s[i]*ub[i,p] for i in I) + gp.quicksum(d[j]*vb[j,p] for j in J) + gp.quicksum(-M[i,j]*y[i,j]*wb[i,j,p] for i in I for j in J )
                                     for p in P), name = 'optimalityCut')
    cFeasabilityCut = rmp.addConstrs((gp.quicksum(-s[i]*ubu[i,r] for i in I) + gp.quicksum(d[j]*vbu[j,r] for j in J) + gp.quicksum(-M[i,j]*y[i,j]*wbu[i,j,r] for i in I for j in J ) <=0 
                                      for r in R), name = 'feasabilityCut')
    cVI1 = rmp.addConstrs((gp.quicksum(s[i]*y[i,j] for i in I)>= d[j] for j in J), name = 'vi1')
    cVI2 = rmp.addConstrs((gp.quicksum(d[j]*y[i,j] for j in J)>= s[i] for i in I), name = 'vi2')
    
    #Define Objective Function
    rmp.setObjective(gp.quicksum(f[i,j]*y[i,j] for i in I for j in J) + n, GRB.MINIMIZE)
    #Define solver parameters
    #Mute the optimze output
    rmp.Params.LogToConsole = 0

    rmp.optimize()
    
    
    
    #retrieve the solution
    oy = rmp.getAttr('x', y)
    oof = rmp.objVal
    
    return(oy, oof)
    #rmp.write("fctpRMP.lp")




