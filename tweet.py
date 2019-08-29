# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 16:17:57 2019

@author: HongLiu
"""

import os
import pandas as pd
import datetime
from datetime import date
from datetime import timedelta, date
from datetime import datetime

#os.chdir(r'C:\Users\HongLiu\Desktop')
foldername = r'C:\Users\HongLiu\Desktop\tweet'
foldername1 =  r'C:\Users\HongLiu\Desktop\tweet1'



for filename in os.listdir(foldername):
    
    if filename.endswith(".csv"): 
        d = filename.find('_')
        date = filename[1:d]        
        date = str(date)
        day = datetime.strptime('2019-04-'+ date,'%Y-%m-%d') 
        a = str(day).find(' ')
        name = str(day)[:a]
        f = pd.read_csv(os.path.join(foldername, filename),encoding = 'unicode_escape')
       # f.astype(str)['created'].map(lambda x:  type(x))
        f['created'] = pd.to_datetime(f['created'].astype(str))
     
        f = f.loc[f['created']==day] 
        f.to_csv(os.path.join(foldername1, name +'.csv'))
     
             
                
              
             
        
       # list1.append(f)
   # datall = pd.concat(list1)
   # datall.to_csv(r'C:\Users\HongLiu\Desktop\tweet\1.csv')
    
       
 
      
          
