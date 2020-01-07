# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 11:55:03 2020

@author: tan185
"""

from mboxrun import processMboxFile
from textrun import processTextFile
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

raw_phish_files = os.listdir(raw_phish_dir)
raw_enron_files = os.listdir(raw_enron_dir)

#for f in raw_phish_files:
#     comb_dir = raw_phish_dir + '/'+ f
#     data = processFile(comb_dir, True, limit)
#     processed_df.addtoq(data)
#     
#for f in raw_enron_files:
#     comb_dir = raw_enron_dir + '/'+ f
#     data = processFile(comb_dir, True, limit)
#     processed_df.addtoq(data)