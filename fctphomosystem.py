# -*- coding: utf-8 -*-
"""
Created on Mon May 10 11:31:33 2021

@author: calle
"""
import gurobipy as gp 
from gurobipy import GRB

### The homogeneous system
#Define model

def solve_homo(I, J, s, d, f, M, yb):
    
    homo = gp.Model()
    
    #Define variables
    u =  homo.addVars(I, name = 'u')
    v = homo.addVars(J, name = 'v')
    w = homo.addVars(I, J, name = 'w')
    
    #Define constraint
    homo.addConstrs((-u[i] + v[j] -w[i,j]<=0 for i in I for j in J), name = 'constraint1')
    
    #Define normalization constraint
    homo.addConstr((gp.quicksum(-s[i]*u[i] for i in I) + gp.quicksum(d[j]*v[j] for j in J) + gp.quicksum(-M[i,j]*yb[i,j]*w[i,j] for i in I for j in J)) ==1, name = 'ofNorm')
    
    #We need to solve a linear system. We do not need to optimize to find the unbounded ray
    homo.setObjective(0)
    
    #Define solver parameters
    #Mute the optimze output
    homo.Params.LogToConsole = 0

    homo.optimize()
    
    #retrieve the solution
    ou = homo.getAttr('x', u)
    ov = homo.getAttr('x', v)
    ow = homo.getAttr('x', w)      
   
    #homo.write("homogeneusSystem.lp")
    return(ou, ov, ow)