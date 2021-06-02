#!/usr/bin/env python
# coding: utf-8

# In[2]:


import gurobipy as gp
from gurobipy import GRB

def transModel(sOrigins, sDestinations, pSupply, pDemand, pCost, pOpenCost):
   
    #create model
    m=gp.Model()
    
    #create variables
    vTransport = m.addVars(sOrigins, sDestinations, name="vTransport")
    vOpenArc = m.addVars(sOrigins, sDestinations, vtype = GRB.BINARY, name="vOpenArc")
    
    #create constraints
    #supply constraint
    m.addConstrs((vTransport.sum(i,'*') <= pSupply[i] for i in sOrigins), name='capacity')
    #demand constraint
    m.addConstrs((vTransport.sum('*', j) >= pDemand[j] for j in sDestinations), name='demandSatisfaction')
    #open arc constraint
    m.addConstrs((vTransport[i, j] <= 999999*vOpenArc[i,j] for i in sOrigins for j in sDestinations), name='logicOpenArc')
    
    #create objective function
    m.setObjective(vTransport.prod(pCost) + vOpenArc.prod(pOpenCost), GRB.MINIMIZE)
    
    m.optimize()
    
    solutionVTransport = m.getAttr('x', vTransport)
    print('Objective function: ' + str(m.ObjVal))
    for i in sOrigins:
        for j in sDestinations:
            if solutionVTransport[i,j]>0:
                print('%s -> %s: %g' % (i, j,  solutionVTransport[i,j]))        
    
    solutionVOpenArc = m.getAttr('x', vOpenArc)
    
    return(solutionVTransport, solutionVOpenArc)

    

