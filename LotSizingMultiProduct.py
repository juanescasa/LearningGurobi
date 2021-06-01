# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 12:16:39 2021

@author: calle
"""
#Implementation of the lot sizing problem
#This implementation is to practise the use of compound sets and joins using pandas.
#There could be easier ways to do it.

#---------------------Problem description-------------------------------------------------------------------------
# The problem
#     Situation
#         You run a supermarket and you are interested in defining how much rice of each type to order each day of the week
#         You know what will be the rice demand per day
#         Your rice supplier charge you each time you ask an order a fixed value
#         There is a cost of holding 1 kg of rice per day in inventory
#     Decision
#         How much to order each day?
#     Objective
#         Minimize the Inventory Holding Cost and ordering cost
#         Find the balance between both costs
#             If you order a lot, you will have to pay the inventory holding cost
#             If you order a little, you wiil have to order frequently and pay many orders





#import all what we need

import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import os

#read the data
#this creates a string conctenating with the symbol /
#the .. means that python will look into the previous folder a folder call data,
# and then look for a file call LotSizing.xlsx
file = os.path.join("..", "data", "LotSizing.xlsx")
sh = 'shProducts'
df_products = pd.read_excel(file, sheet_name = sh)
sh = 'shPeriods'
df_periods = pd.read_excel(file, sheet_name = sh)
sh = 'shProductsPeriods'
df_products_periods = pd.read_excel(file, sheet_name = sh)
sh = 'shScalars'
df_scalars = pd.read_excel(file, sheet_name = sh)

#Calculate dataframes. For the first inventory balance constraint I need the compound set sProductsFirstPeriod

#this merge is a kind of vlookup that adds to the df_products_periods the columns in df_periods
df_products_firstPeriod = df_products_periods.merge(df_periods, how='inner', on = 'Period')
#This filters the rows in which 'isFirstPeriod=1' and selecet the columns Product and Period in the resulting datafram
df_products_firstPeriod = df_products_firstPeriod[(df_products_firstPeriod['isFirstPeriod']==1)][['Product','Period']]

#read unidimensional parameters
pHoldingCost = df_scalars['Value'][0]
pOrderCost =df_scalars['Value'][1]

#Read inputs mathematical model
sProducts=[]
sPeriods=[]
sProductsFirstPeriod=[]
sProductsPeriodsPreviousPeriod=[]
pInitialInventory={}
pDemand={}

#print(df_products.shape[0])
for index in range(df_products.shape[0]):
     p = df_products['Product'][index]
     sProducts.append(p)
     pInitialInventory[p] = df_products['pInitialInventory'][index]
     
for index in range(df_periods.shape[0]):
    t = df_periods['Period'][index]
    sPeriods.append(t)
    
for index in range(df_products_periods.shape[0]):
    p = df_products_periods['Product'][index]
    t = df_products_periods['Period'][index]
    pDemand[p,t]= df_products_periods['Demand'][index]
 
#Compound set defintion

for index in range(df_products_firstPeriod.shape[0]):
    p = df_products_firstPeriod['Product'][index]
    t = df_products_firstPeriod['Period'][index]
    sProductsFirstPeriod.append((p,t))
    
tt='t0'    
for index in range(df_products_periods.shape[0]):
    p=df_products_periods['Product'][index]
    t=df_products_periods['Period'][index]
      
    if t !='t1':
        sProductsPeriodsPreviousPeriod.append((p,t,tt))
    tt=t
#Calculate parameters

pBigM = sum(pDemand.values())

#create model

m = gp.Model()

#create variables
vQtyOrder = m.addVars(sProducts, sPeriods, name = "vQtyOrder")
vOrder = m.addVars(sPeriods, vtype = GRB.BINARY, name = "vOrder" )
vInventory = m.addVars(sProducts, sPeriods, name = "vInventory")

#create constraints
#Intial Inventory
m.addConstrs((vInventory[p,t] == pInitialInventory[p] + vQtyOrder[p,t] - pDemand[p,t] for (p,t) in sProductsFirstPeriod ), name = 'InitialInventory')
#Inventory Balance
m.addConstrs((vInventory[p,t] == vInventory[p,tt] + vQtyOrder[p,t] - pDemand[p,t] for (p,t,tt) in sProductsPeriodsPreviousPeriod), name = 'InventoryBalance')
#Logic binary continuous variable
m.addConstrs((vQtyOrder.sum('*',t) <= pBigM*vOrder[t] for t in sPeriods), name = 'OrderLogic')

#create objective function
m.setObjective(pHoldingCost*vInventory.sum('*', '*') + pOrderCost*vOrder.sum('*'), GRB.MINIMIZE)

m.optimize()

#write the lp model in a file in the same folder as the script
m.write("LotSizingMultiproducts.lp")
#write the solution of the model in a file in the same folder as the script
m.write("outputLotSizingMultiproduct.sol")







