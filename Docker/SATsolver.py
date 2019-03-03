#DEPENDENCIES
import numpy as np
from copy import deepcopy as copy
from collections import Counter
import operator


def sudoku_to_dimacs(file_name = "1000_sudokus.txt"):
    f = open(file_name, "r")
    lines = f.readlines()
    total_dimacs = []
    for i, sudoku in enumerate(lines):
        dimacs_sudoku = []
        for j, cell in enumerate(sudoku):
            row, column = divmod(j, 9)
            if cell=="." or cell == '\n':
                continue
            else:
                
                dimacs_sudoku.append(str(row+1)+str(column+1)+str(cell))  
        total_dimacs.append(dimacs_sudoku)
    return total_dimacs
	

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



def read_dimac(file_name = "sudoku-rules.txt", is_txt = True):
    #read file
    if is_txt:
        f = open(file_name, "r")
        lines = f.readlines()
    else:
        lines = file_name
        
    #generate variables
    clauses={}
    variables = {}

    #for each clause
    for i, line in enumerate(lines):
        if is_txt:
            if i == 0:
                continue
        
        clause = transform_dict(line.split())
        clauses[int(i+3)] = clause
        for key in clause.keys():
            try:
                variables[key].append(i+3)
            except:
                variables[key] = [None]
                variables[key].append(i+3)

    return clauses, variables
	
	

def merge (variables_1, variables_2, clauses_1, clauses_2):
    len_1 = max(clauses_1)
    clauses_2_new = {}
    for idx, clause in clauses_2.items():
        idx_new = idx+len_1
        clauses_1[idx_new] = clause
        for variable in clause:
            variables_1[variable].append(idx_new)
        
    return variables_1, clauses_1
	
	
	
	
# NEED TO SPECIFY INPUT FILE

clauses, variables =read_dimac()                       
clauses_example, variables_example =read_dimac(file_name = "sudoku-example.txt")  

variables, clauses = merge( variables,  variables_example, clauses, clauses_example)


def remove_tautology(clauses, variables):
    # for each variable
    for var_name, var_idx in variables.items():
        # check if variable has double occurance in any clause
        duplicates = set([x for x in var_idx[1:] if var_idx[1:].count(x) > 1])
        #if not, continue
        if len(duplicates) == 0:
            continue
        #for each clause where variable occurs twice
        for idx in duplicates:
            is_break = False
            #for each literal of that variable in the clause
            for literal_i in  clauses[idx][var_name]:
                #double_break
                if is_break:
                    break
                #for every other literal
                for literal_j in clauses[idx][var_name]:
                    #if there is a tautology
                    if literal_i != literal_j:
                        #remove this clause
                        del clauses[idx]
                        #removing index of this clause from variables
                        for var_name_2, var_idx_2 in variables.items():
                            new_var = [var_idx_2[0]] + [x for x in var_idx_2[1:] if x != idx]
                            variables[var_name_2] = new_var
                        
                        #double break
                        is_break = True
                        break
    return clauses, variables
	
	
	
def delete_clause(idx, clauses, variables):
    
    #remove the clause from mentions in all variables
    for variable in clauses[idx]:

        new_var = [variables[variable][0]] + [x for x in variables[variable][1:] if x!=idx]
        variables[variable] = new_var
        
    #delete the clause
    del clauses[idx]
   
    return clauses, variables


def belief_propogation(variable, clauses, variables):
    truth_value = variables[variable][0]

    for clause in variables[variable][1:]:
        if truth_value == clauses[clause][variable][0]:
            clauses, variables = delete_clause(clause, clauses, variables)
        else:
        
            new_var = [variables[variable][0]] + [x for x in variables[variable][1:] if x!=clause]
            variables[variable] = new_var
            del clauses[clause][variable]
    return clauses, variables
    

def unit_check(clauses, variables):
    
    generator = ( (idx, clause) for (idx, clause) in clauses.items() )
    empty = True
    for idx, clause in  generator:
        
        if len(clause) == 1:
            variable = list(clause.keys())[0]
            literal = list(clause.values())[0][0]
            
            if literal:
                variables[variable][0] = True  
                clauses, variables = delete_clause(idx, clauses, variables)
                clauses, variables = belief_propogation(variable, clauses, variables)
                empty = False
                break
            else:
                variables[variable][0] = False  
                clauses, variables = delete_clause(idx, clauses, variables)
                clauses, variables = belief_propogation(variable, clauses, variables)
                empty = False
                break
          
                
                
            
    return clauses, variables, empty
                
      
	  
def check_for_empty_clause(clauses):
    for clause in clauses.values():
        if len(clause) == 0:
            return True
    return False
def check_emptiness(clauses):
    if len(clauses) == 0:
        return True
    return False
	
	
	
# VIDS heuristic

# TODO Initialize counter beforehand:
# var_counter = Counter()

def heu1(clauses, variables, var_counter):
    alpha = 0.5
    for key, value in variables.items():
        if len(value[1:]) > 0:
            var_counter[key] += len(value[1:]) *alpha
    next_var = var_counter.most_common(1)[0][0] if var_counter else None
    return next_var, var_counter
            
def jeroslow(clauses, variables):
   
    J = {key:0 for key in variables.keys()}
    for variable_key, variable_clauses in variables.items():
        for clause_idx in variable_clauses[1:]:
            if clauses[clause_idx][variable_key][0] == 1:
                
                J[variable_key]+=len(clauses[clause_idx])
   
    #print( max(J.items(), key=operator.itemgetter(1))[0], J[ max(J.items(), key=operator.itemgetter(1))[0]])
    return max(J.items(), key=operator.itemgetter(1))[0]

def human(clauses, variables):
    
    #find the most full row or column
    
    matrix = np.zeros((10,10))
    for i in range(1, 10): 
        for j in range(1, 10):
            for z in range(1,10):
                if variables[100*i+10*j+z][0]:
                    matrix[i,j]+=1
    
    matrix = matrix[1:,1:]
    
    column = np.sum(matrix,0)
    row = np.sum(matrix,1)
    for typ in [row, column]:
        for i, value in enumerate(typ):
            if value == 9:
                typ[i] = 0
    

    max_column = (np.max(column), np.argmax(column)+1)
    max_row = (np.max(row), np.argmax(row)+1)
    #change a random value in that row or column 
    if max_row[0] > max_column[0]:
        possible_values = []
        for col in range(1,10): 
            for val in range(1,10):
                if variables[max_row[1]*100+col*10+val][0]==None:
                    possible_values.append(max_row[1]*100+col*10+val)
        
        return np.random.choice(possible_values)
    else: 
        possible_values = []
        for row in range(1,10): 
            for val in range(1,10):
                if variables[row*100+max_column[1]*10+val][0]==None:
                    possible_values.append(row*100+max_column[1]*10+val)
        
        return np.random.choice(possible_values)
    
    
	

def dpll(clauses, variables, heuristic, metrics):
    var_counter = Counter()
    while True:
        #simplification round
        
        while True:
            #simplify
            
            clauses, variables, empty = unit_check(clauses, variables)
            
            if empty:
                break
        #print(0)    
        if check_for_empty_clause(clauses):
            #print("Empty clause")
            return False, variables, clauses, metrics
            
        if check_emptiness(clauses):
            #print("Empty conjunction of  clauses")
            return True, variables, clauses, metrics
            
            
        #split randomly for now
        if heuristic == 0:
            variable = np.random.choice([key for (key, value) in variables.items() if value[0]==None])
        elif heuristic == 1:
            variable, var_counter = heu1(clauses, variables, var_counter)
        elif heuristic == 2:
            
            variable = human(clauses, variables)
        
        #copy variables and clauses
        variables_new, clauses_new = copy(variables), copy(clauses)
        unsat_clauses = len(clauses)
        #metrics
        if len(metrics) == 0: 
            metrics.append([len(clauses), 0])
        else:
            backtracks = metrics[-1][1]
            metrics.append([len(clauses), backtracks])
        #set variable to True
        variables_new[variable][0] = True
        clauses_new, variables_new  = belief_propogation(variable, clauses_new, variables_new)
        is_true, variables_new, clauses_new, metrics = dpll(clauses_new, variables_new, heuristic, metrics)
        if is_true:
            #print("TRUE")
            return True, variables_new, clauses_new, metrics
        else:
            #metrics
            backtracks = metrics[-1][1]
            metrics.append([len(clauses), backtracks+1])
            #print(1)
            variables[variable][0] = False
            clauses, variables = belief_propogation(variable, clauses, variables)
            is_true, variables, clauses, metrics = dpll(clauses, variables, heuristic, metrics)
            #print("SAT")
            return is_true, variables, clauses, metrics
            

    return False

	
# RUN AND RETURN FILE
np.random.seed(10312343)
var_counter = Counter()
clauses, variables =read_dimac()                       
clauses_example, variables_example =read_dimac(file_name = "sudoku-example.txt")  
variables, clauses = merge( variables,  variables_example, clauses, clauses_example)
clauses, variables = remove_tautology(clauses, variables)
t, variables, clauses, metrics = dpll(clauses, variables, 2 , metrics = [])


f = open("output.txt",'w+')
for line in variables:
	print(variables[line][0])
	if variables[line][0]:
		
		print(line)
		var_w = str(line)
		f.write("".join([var_w,'\n']))
	
f.close