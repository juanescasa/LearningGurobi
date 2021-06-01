# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 10:41:22 2021

@author: calle
"""

#this package only support xls files
import xlrd

import fixedChargeTransportationModel
import time

start_time_read_data = time.time()

path="C:\OneDrive - Deakin University\OD\Personal\Software Documentation\Gurobi\data fixed charge transportation problem.xlsx"
book = xlrd.open_workbook(path)

sOrigins=[]
sDestinations=[]
pSupply={}
pDemand={}
pCost={}
pCostOpen={}

sh = book.sheet_by_name("shOrigins")
#a = sh.cell_value(0,0)
#print(a)
row=1
while True:
    try:
     i = sh.cell_value(row,0)
     sOrigins.append(i)
     pSupply[i]=sh.cell_value(row,1)
     row=row+1
    except IndexError:
        break
sh = book.sheet_by_name("shDestinations")
row=1
while True:
    try:
        j = sh.cell_value(row, 0)
        sDestinations.append(j)
        pDemand[j]=sh.cell_value(row,1)
        row=row+1
    except IndexError:
        break

sh = book.sheet_by_name("shOriginsDestinations")
row=1
while True:
    try:
        i = sh.cell_value(row, 0)
        j = sh.cell_value(row, 1)
        
        pCost[i,j]=sh.cell_value(row,2)
        row=row+1
    except IndexError:
        break

end_time_read_data = time.time()

print('read from xlrd takes' + str(end_time_read_data-start_time_read_data))
print("--- %s seconds ---" % (end_time_read_data-start_time_read_data))

outputVTransport =fixedChargeTransportationModel.transModel(sOrigins, sDestinations, pSupply, pDemand, pCost, pCostOpen)[0]


