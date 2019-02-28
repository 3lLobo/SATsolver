import numpy as np
import pandas as pd
from copy import deepcopy as copy
from collections import Counter
import operator

#clause representation
clauses=[{1:0,2:1,3:0},[{4:1,2:0}]]
#variable representation
test_var = {1:[True, 0], 2: [False, 0,1,1], 3:[None, 0,1], 4:[None, 1,2,2] }

def transform_dict(l):
    new_dict = {}
    for element in l:
        if element[0]=="0": 
            break  
        elif element[0] == "-":
            key = int(element[1:])
        else:
            key = int(element)
        new_dict[key]=[]
    
    for element in l:
        if element[0]=="0": 
            break  
        elif element[0] == "-":
            new_dict[int(element[1:])].append(0)
        else:
            new_dict[int(element)].append(1)
    
    return new_dict

