# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 11:55:03 2020

@author: tan185
"""

from mboxrun import processMboxFile
from textrun import processTextFile, processFolder
import os
import pandas as pd

class Queue:

  def __init__(self):
      self.queue = list()
      
# Insert method to add element
  def addtoq(self,dataval):
      if dataval not in self.queue:
          self.queue.insert(0,dataval)
          return True
      return False
  
# Pop method to remove element
  def removefromq(self):
      if len(self.queue)>0:
          return self.queue.pop()
      return ("No elements in Queue!")
  
raw_phish_dir = 'data/raw_data/phishing'
raw_enron_dir = 'data/raw_data/enron'

limit = 10000

processed_df = Queue()


def process_all_raw_files(file_path, file_type, phishy=True, limit=500):
    raw_files = os.listdir(file_path)
    for f in raw_files:
        if f.endswith(file_type):
            comb_dir = file_path + '/'+ f
            if file_type == '.mbox':
                data = processMboxFile(comb_dir, phishy, limit)
                processed_df.addtoq(data)
            elif file_type == '.txt':
                data = processTextFile(comb_dir, phishy, limit)
                processed_df.addtoq(data)
            else:
                data = processFolder(comb_dir, phishy, limit)
                processed_df.addtoq(data)

#example: process_all_raw_files(raw_phish_dir, "")

def process_raw_file(file_path, phishy=True, limit=500, ith=0):
    raw_files = os.listdir(file_path)
    if len(raw_files) > ith:
        return 'maximum number of files is '+ len(raw_files)
    f = raw_files[ith]    
    
    comb_dir = file_path + '/'+ f
    
    if  f.endswith('.mbox'):
        data = processMboxFile(comb_dir, phishy, limit)
        processed_df.addtoq(data)
    elif  f.endswith('.txt'):
        data = processTextFile(comb_dir, phishy, limit)
        processed_df.addtoq(data)
    else:
        data = processFolder(comb_dir, phishy, limit)
        processed_df.addtoq(data)
        

#%%

print('====Raw Files====')
print('____Phsihing_____')
raw_phish = os.listdir(raw_phish_dir)
i = 0
for r in raw_phish:
    print(str(i) + "  "  + r)
    i += 1

i = 0
print('\n______Legit______')
raw_enron = os.listdir(raw_enron_dir)
for r in raw_enron:
    print(str(i) + "  "  + r)
    i += 1
 

