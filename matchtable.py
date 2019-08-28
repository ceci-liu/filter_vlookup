# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 13:04:47 2019

@author: HongLiu
"""

import pandas as pd
import csv
import xlsxwriter
import openpyxl
import xlrd
from openpyxl import load_workbook
import sys
import re
import os 
import datetime

def filter19(newfile,column):
    datall = pd.read_csv(newfile,skiprows = range(0,10))
    datall = datall.filter(['Campaign','Campaign ID','Placement','Placement ID'],axis = 1)
    fy19 =datall[datall[column].str.contains('CY19|FY19')] 
    #fy19 = fy19[~fy19.Campaign.str.contains('FY18')]  #drop campaign name with FY18-FY19
    return fy19
    
def vlookup(file,sheet, skiprow,usecol,num,data1,left,right,columns):
    
    data2 = pd.read_excel(open(file,'rb'),sheet_name = sheet,skiprows = skiprow,usecols = usecol,keep_default_na = False)
    data2 = data2[0:num]
  
    lookup1 = pd.merge(data1,data2,how = 'left', left_on = left,right_on = right)
    lookup1 = lookup1.drop(columns,axis = 1)
    return lookup1


if __name__ == '__main__':
    # filenames
    # 1.the path of the report you just dowloaded (csv)
    folder = r'C:\Users\HongLiu\Desktop\Match Table'
    placement = r'C:\Users\HongLiu\Desktop\Match Table\3340_Ralph-Match-Table-Placement_20190827_103417_2637812689.csv'
    # 2. Match table from last month (csv)
    old_table19=r'C:\Users\HongLiu\Desktop\Match Table\FY19_Placement_ID_Key_20190819.csv'
    old_table18 = r'C:\Users\HongLiu\Desktop\Match Table\20190405\match_tables_fy17_match_tables_FY18_Placement_ID_Key_20190405.csv'
    # 3.vlookup "how to parse placement for viant" (xlsx)
    pf = r'C:\Users\HongLiu\Desktop\Match Table\how to parse placement for viant.xlsx'
    # 4.The path of final file you wanna save (This should be with .xlsx)
    final = r'C:\Users\HongLiu\Desktop\Match Table\match_table_null.xlsx'
   
    #filter Campaign name with FY19
    #try:
    fy19 = filter19(placement,'Campaign')
    #vlookup on lastest version of match table
    lookup1 = pd.read_csv(old_table19,low_memory=False)
    lookup2 = pd.read_csv(old_table18,low_memory=False)
     
    lookup_tactic = lookup1.filter(['Placement_id','Tactic'],axis = 1)
    lookup_tactic1 = lookup2.filter(['Placement_id','Tactic'],axis = 1)
 
    fy19['Placement ID']=fy19['Placement ID'].astype(int)
    #vlookup fy19 old table and new file
    df = pd.merge(fy19,lookup_tactic,how = 'left',left_on = 'Placement ID',right_on = 'Placement_id')
    #Find tactic with NAs
    tactic = df[df['Placement_id'].isnull()]
    tactic = tactic.drop(['Placement_id','Tactic'],axis = 1)
    #vlookup FY18's old table 
    tactic['Placement ID']=tactic['Placement ID'].astype(str)
    df1 = pd.merge(tactic,lookup_tactic1,how = 'left',left_on = 'Placement ID',right_on = 'Placement_id')
    
    
    tactic1 = df1[df1['Placement_id'].isnull()]
    tactic1 = tactic1.drop('Placement_id',axis = 1)
   
    #Text to column on 'Placement'
    a = tactic1['Placement'].str.split('_',expand = True)
    
    a.columns = ['Region','DMA Name','DMA Code','tactic','Site','Model','Audience Segment','Platform','Unit Execution','Dimensions/Ad size','Demographic Segment','Targeting','Marketing Objectives/Optimizations','Audience Segment Data Source','Placement Description','Media Type','AD Serving Method','DSP','Cost Structure']
    #a = a.filter(['tactic','Site','Model','Platform','Format'])
    # file with column in 'tactic','Site','Model','Platform'

    data_tsmp = pd.concat([tactic1,a],axis = 1)
    data_tsmp= data_tsmp.drop('Tactic',axis = 1)
    
    #vlookup to get 'format' and 'frienfly_name'
    
   # vformat = vlookup(pf,'Format Lookup',2,"C:D",23,data_tsmp,'Dimensions/Ad size','Unit',['Unit'])     
    vfriend_name = vlookup(pf,'Friendly Name Lookup',2,"C:D",202,data_tsmp,'tactic','Tactic','Tactic')
    vcampaign = vlookup(pf,'Campaign Rollup',0,"A:B",105,vfriend_name,'Campaign','Campaign Dimension','Campaign Dimension')
    vmodel = vlookup(pf,'Parse Poistions',15,"D:E",59,vcampaign,'Model','Model','Model')
    vmodel.rename(columns = {'Full Model Name':'Model','tactic':'Tactic','Placement ID':'Placement_id'},inplace = True)
    vmodel['Format'] = vmodel['Media Type']
    #reorder the columns
    datall = vmodel[['Campaign','Campaign ID','Placement','Placement_id','Tactic','Site','Model','Platform','Format','Friendly_Name','Campaign_Rollup','Region','DMA Name','DMA Code','Audience Segment','Unit Execution','Dimensions/Ad size','Demographic Segment','Targeting','Marketing Objectives/Optimizations','Audience Segment Data Source','Placement Description','Media Type','AD Serving Method','DSP','Cost Structure']]
    # Check any column contains null value
    null = datall[datall.isna().any(axis=1)]
       
     # The path of the new file you wanna save to 
    #if got null values, generate a xlsx file with null record
    if null.shape[0] != 0:
        path = final
        writer = pd.ExcelWriter(path, engine = 'xlsxwriter')
        datall.to_excel(writer, sheet_name = 'match table',index = False)
        null.to_excel(writer,sheet_name = 'with null values',index = False)
        writer.save()
        writer.close()
        print("Find null values, need to update table manually!")
    #if didn't get null value, append new records to old match table
    else:
        if any(datall.duplicated('Placement_id')) == True:   # check if there's any duplicate placement_id
            datall = datall.drop_duplicates('Placement_id',keep = False)
            print("Duplicate value was found and dropped!")
     #   datall.to_csv(old_table19,index = False,header = False,mode = 'a')
        now = datetime.datetime.now()
        date = str(now)[:10]
        date = 'FY19_Placement_ID_Key_' + date.replace("-", "") +'.csv'
        newname = os.path.join(folder,date)
        os.rename(old_table19,newname)
        print("New placements were added!")
        
#read the whole file, check and drop duplicate values under "placement_id" column
  #  check_dup = pd.read_csv(old_table)
  #  finish = check_dup.drop_duplicates(subset = 'Placement_id', keep = False,inplace = True)

   
        
  
  

    