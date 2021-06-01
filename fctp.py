#!/usr/bin/env python
# coding: utf-8

# In[2]:


import gurobipy as gp
from gurobipy import GRB

# Base data
sOrigins, pSupply = gp.multidict({
    ('i1'):   10,
    ('i2'):  30,
    ('i3'):  40,
    ('i4'):  20,
    })
print(sOrigins)
print(pSupply)


# In[3]:



sDestinations, pDemand = gp.multidict({
    ('j1'):   20,
    ('j2'):  50,
    ('j3'):  30,
    })
print(sDestinations)
print(pDemand)


# In[4]:


pCost = {
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

print(pCost)


# In[9]:


#create model
m=gp.Model()

#create variables
vTransport = m.addVars(sOrigins, sDestinations, name="vTransport")
print(vTransport)


# In[31]:


#create constraints
#supply constraint
m.addConstrs((vTransport.sum(i,'*') <= pSupply[i] for i in sOrigins), name='capacity')
#demand constraint
m.addConstrs((vTransport.sum('*', j) >= pDemand[j] for j in sDestinations), name='demandSatisfaction')

#create objective function
m.setObjective(vTransport.prod(pCost), GRB.MINIMIZE)

m.optimize()

solution = m.getAttr('x', vTransport)
print('Objective function: ' + str(m.ObjVal))
for i in sOrigins:
    for j in sDestinations:
        if solution[i,j]>0:
            print('%s -> %s: %g' % (i, j,  solution[i,j]))        
        

