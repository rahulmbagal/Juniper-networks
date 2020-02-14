# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 23:25:38 2020

@author: rahul
"""


 # Logic replicated from the book “An Introduction to Duplicate Detection”
import argparse
# ! pip install fuzzywuzzy
import pandas as pd
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz

class Partition:
#    def __init__(self, data, fuzzy_match_func, max_size=None):
#        self.data = data
#        self.fuzzy_match_func = fuzzy_match_func 
#        self.max_size = max_size
    
  
    def find_partitions(self, data, fuzzy_match_func):
        """Recursive algorithm for finding duplicates in a DataFrame."""
        self.data = data
        self.fuzzy_match_func = fuzzy_match_func 
        self.max_size = None
        
        # If block_by is provided, then we apply the algorithm to each block and
        # stitch the results back together
        def get_record_index(r):
            self.r = r
            return self.r[self.data.index.name or 'index']
    
        # Records are easier to work with than a DataFrame
        self.records = self.data.to_records()
    
        # This is where we store each partition
        self.partitions = []
    
        def find_partition( at=0, partition=None, indexes=None):
#            print ("=========================================")
#            print ("at ====>", at)
            
            r1 = self.records[at]
#            print ("=========================================>>>>>>>>>>>")
            if partition is None:
                partition = {get_record_index(r1)}
                indexes = [at]
    
            # Stop if enough duplicates have been found
            if self.max_size is not None and len(partition) == self.max_size:
                return partition, indexes
    
            for i, r2 in enumerate(self.records):
    
                if get_record_index(r2) in partition or i == at:
                    continue
    
                if self.fuzzy_match_func(r1, r2):
                    partition.add(get_record_index(r2))
                    indexes.append(i)
                    find_partition(at=i, partition=partition, indexes=indexes)
    
            return partition, indexes
    
        while len(self.records) > 0:
            self.partition, self.indexes = find_partition()
            self.partitions.append(self.partition)
            self.records = np.delete(self.records, self.indexes)
    
        return pd.Series({
            idx: partition_id
            for partition_id, idxs in enumerate(self.partitions)
            for idx in idxs
        })

