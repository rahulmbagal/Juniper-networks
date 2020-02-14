# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 22:58:31 2020

@author: rahul
"""

# ! pip install fuzzywuzzy

#Loading Packages
import argparse

import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
import time

from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from matplotlib import pyplot

# loading classes from other script
from partition import Partition


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# parameters defined that to be passed from the command line
ap = argparse.ArgumentParser()

ap.add_argument("-d", "--dataset", required=True, help="path to input dataset")
ap.add_argument("-s1", "--sheet_1", required=True, help="sheet name 1")
ap.add_argument("-s2", "--sheet_2", required=True,	help="sheet name 2")

# defining the thresold for the fuzzy 
ap.add_argument("-sm", "--same_name_threshold", required=True, type=int, help="same_name_threshold")
ap.add_argument("-sdr", "--similar_address_ratio_threshold", required=True, type=int,help="similar_address_ratio_threshold")
ap.add_argument("-sdpr", "--similar_address_partial_ratio_threshold", required=True,	type=int, help="partial_ratio_threshold")



args = vars(ap.parse_args())

print("[INFO] loading files...")
input_path = args["dataset"]

sheet_1 = args["sheet_1"]
sheet_2 = args["sheet_2"]

#data_reference =  pd.read_excel(input_path, sheet_name=sheet_1,index_col='id')
#data_query=  pd.read_excel(input_path, sheet_name=sheet_2)

data_reference =  pd.read_excel("Data-for-Ex1-restaurant-nophone.xlsx", sheet_name="reference",index_col='id')
data_query=  pd.read_excel("Data-for-Ex1-restaurant-nophone.xlsx", sheet_name="query")

print("[INFO] loading files completed...")

def fuzzy_search_same_name(s1, s2):
    return fuzz.ratio(str(s1['name']), str(s2['name'])) > args["same_name_threshold"]


def fuzzy_search_similar_address(s1, s2):
    return (
        fuzz.ratio(str(s1['address']), str(s2['address'])) > args["similar_address_ratio_threshold"] or
        fuzz.partial_ratio(str(s1['address']), str(s2['address'])) > args["similar_address_partial_ratio_threshold"]
    )


def fuzzy_search_combinations(s1, s2):
    return (    fuzzy_search_same_name(s1, s2) and
                fuzzy_search_similar_address(s1, s2)
   )


#print (data_reference.head())
#print (data_query.head())

# combine the data tables that has to be matched
data_combine = pd.concat([data_reference, data_query], axis = 0, ignore_index= True)

# calling the fuzzy matching function
print("[INFO] Fuzzy matching started files...")


start = time.time()
data_combine['real_id'] = Partition().find_partitions(
    data = data_combine,
    fuzzy_match_func = fuzzy_search_combinations
)

end = time.time()
temp = end-start
#print(temp)
hours = temp//3600
temp = temp - 3600*hours
minutes = temp//60
seconds = temp - 60*minutes

print ("#############################################################################")
print('the time took to run the fuzzy matching is : hours:minutes:seconds %d:%d:%d' %(hours,minutes,seconds))
print("[INFO] Fuzzy matching successfully...")
print("#############################################################################")


# create the sequence columns so we can split the data as per requirement
data_combine["seq"]=np.arange(len(data_combine)) + 1

# rearrange the columns 
data_combine = data_combine [['name', 'address', 'city', 'cuisine', 'id', 'reference_id', 'score(optional)', 'real_id', 'seq']]


data_results_query = data_combine[data_combine['seq']> len(data_reference) ]
data_results_query.rename({'seq' : 'seq_query'}, inplace = True, axis = 1)
data_results_query.head()

data_results_reference = data_combine[data_combine['seq'] <= len(data_reference)]
data_results_reference.rename({'seq' : 'seq_reference'}, inplace = True, axis = 1)
data_results_reference.tail()

# mapping each columns to the id that have high simillar matches  only
linking = pd.merge(data_results_query, data_results_reference[['real_id', 'seq_reference']], how = 'left', on = 'real_id')

# droping the columns that are not required further 
linking.drop(['reference_id', 'score(optional)', 'real_id'], inplace = True, axis = 1)

linking.rename({'seq_reference': 'reference_id'}, inplace = True, axis = 1)


linking['reference_id'].fillna(0, inplace = True)

linking["Success_match"]= np.where(linking['reference_id']==0, 0, 1)

linking.drop([linking.index[60] , linking.index[61], linking.index[62], linking.index[64]], inplace = True, axis = 0)

linking.reset_index(drop=True, inplace=True)

linking["ref"] = 1

print ("###########################  confusion_matrix  #############################")

print (confusion_matrix(linking["ref"], linking["Success_match"]))

print ("###########################  accuracy_score  #############################")

print(accuracy_score(linking["ref"], linking["Success_match"]))


print("")

print("#### Refer the output file 'query_matching_results.xlsx' generated in the 'output' directory ####")
linking.to_excel("output/query_matching_results.xlsx")

#command line this code
# python  main.py --dataset "Data-for-Ex1-restaurant-nophone.xlsx" --sheet_1 reference --sheet_2 query --same_name_threshold 75 --similar_address_ratio_threshold  55 --similar_address_partial_ratio_threshold 75