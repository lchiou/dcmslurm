"""dcmuslurm_make_params.py
This module generates a list of input parameters using which to generate the
job scripts.

The functions can be called independently, but the typical usage is to generate
the parameters using the dcmslurm_make_params module. And then build the batch
and shell scripts using make_scripts_all from dcmslurm_make. An example such
script follows below.

Lawrence Chiou
20 October 2017
_______________________________________________________________________________
Example script:

path_dcmslurm = '/home/usr/dcm/dcmslurm'
path_spm = '/home/usr/dcm/spm12beta'

path_raw = '/scratch/users/usr/dcm_data'
path_raw_file = '/scratch/users/usr/dcm_data/brain_data.mat'
path_parsed = '/scratch/users/usr/dcm_data/brain_data_parsed'

import os
import sys
sys.path.append(path_dcmslurm)
from dcmslurm_make import make_scripts_all
from dcmslurm_make_params import make_params

directory_output = '/scratch/users/usr/dcm_data/brain_data_output'
prefix_output = 'brain_data'

path_params_list = make_params( \
	filename='%s_params' % prefix_output, \
	path_output=os.path.dirname(path_parsed), \
	n_in=5, \
	free_connects=1, \
	self_connect=True, \
	dominant_nodes=[1])

for i in range(len(path_params_list)):
	make_scripts_all(
		path_params = path_params_list[i], \
		directory_output = directory_output, \
		prefix_output = '%s_%s' % (prefix_output, str(i+1)), \
		path_dcmslurm = path_dcmslurm, \
		path_spm = path_spm, \
		path_raw = path_raw, \
		path_raw_file = path_raw_file, \
		path_parsed = path_parsed, \
		save_in_path_parsed = 'false', \
		labels = "{'cond 1', 'cond 2', 'cond 3'}", \
		subjects = 16, \
		em_steps_max = 150, \
		time = '00:10:00', \
		email = 'user@email.com', \
		partition = 'normal', \
		nodes = 1, \
		memory = 700, \
		overwrite = True)	
"""

import copy
import itertools
import os

def nkstrings(n, k):
	"""Returns list of all binary strings of length n with k '1's.

	Args:
		n: string length
		k: number of '1's that appear in each string
	Returns:
		list_nkstrings: list of binary strings of length n with k '1's
	"""
    list_nkstrings = []
    for bits in itertools.combinations(range(n), k):
        s = ['0'] * n
        for bit in bits:
            s[bit] = '1'
        list_nkstrings.append(''.join(s))
    return list_nkstrings

def matrix_options(n_in = 5, free_connects = 2, \
	matrix_A = [], \
	self_connect = True, dominant_nodes = []):
	"""Generates the list of A matrices that adhere to a set of specified
	conditions.

	Args:
		n_in: number of nodes
		free_connects: 
		matrix_A: matrix of pre-specified values (default is empty matrix)
		self_connect: allow self-connects if True
		dominant_nodes: nodes that should always accept connections from
			the "non-dominant nodes" (i.e., nodes not specified in the list).
			For instance, given dominant nodes [2, 3], there will always be
			connections from 1 (non-dominant node) to 2 and 3 (dominant nodes).
	Returns:
		matrix_A_list: list of A matrices satisfying the input options
	"""
	if matrix_A == []:
		n = n_in
		matrix_A_out = [['*' for i in range(n)] for j in range(n)]
	else:
		matrix_A_out = matrix_A[:]
		n = len(matrix_A_out)

	if self_connect:
		for i in range(n):
			matrix_A_out[i][i] = 1

	for node in dominant_nodes:
		for i in range(n):
			matrix_A_out[i][node-1] = 1   

	ast_total = 0
	for row in matrix_A_out:
		ast_total += row.count('*')

	matrix_A_list = []
	for nkstring in nkstrings(ast_total, ast_total-free_connects):
		matrix_A_temp = copy.deepcopy(matrix_A_out)
		string_pos = 0
		for i in range(n):
			for j in range(n):
				if matrix_A_temp[i][j] == '*':
					matrix_A_temp[i][j] = int(nkstring[string_pos])
					string_pos += 1
		matrix_A_list.append(matrix_A_temp[:])
	return matrix_A_list

def format_matrix(matrix_in):
	"""Reformats Python list syntax to MATLAB array syntax.

	Args:
		matrix_in: Python-formatted list
	Returns:
		MATLAB-formatted array
	"""
	return str(matrix_in).replace('], [', '; ').replace('[[', '[') \
		.replace(']]', ']').replace(', ', ' ')

def format_matrix_all(matrix_A_out = [], matrix_C = [1, 0, 0, 0, 0], \
	hidden_nodes = [], **kwargs):
	"""Reformats Python-formatted lists for the A matrix, C matrix, and list of
	hidden nodes.

	Args:
		matrix_A_out: Python-formatted A matrix
		matrix_C: Python-formatted C matrix
		hidden_nodes: Python-formatted list of hidden nodes
		**kwargs: matrix options to be passed to matrix_options
	Returns:
		Single string containing the corresponding MATLAB-formatted arrays
			delimited by ampersands (&)
	"""
	return '%s&%s&%s\n' % (format_matrix(matrix_A_out), \
		format_matrix(matrix_C), format_matrix(hidden_nodes))

def make_params(filename, path_output, **kwargs):
	"""Reformats Python-formatted lists for the A matrix, C matrix, and list of
	hidden nodes.

	Args:
		filename: name of the output file (no extension)
		path_output: directory where the output file should go
		**kwargs: matrix options to be passed to matrix_options
	Returns:
		List of parameter script paths
	"""
	script_list = []
	matrix_A_list = matrix_options(**kwargs)
	
	count = 0
	for matrix_A_out in matrix_A_list:
		if count % 60 == 0:
			if count != 0:
				script.close()
			num_scripts = count / 60 + 1
			path = os.path.join(path_output, \
				'%s-%s.txt' % (filename, str(num_scripts)))
			script_list.append(path)
			script = open(path, 'wb')
		script.write(format_matrix_all(matrix_A_out=matrix_A_out, **kwargs))
		count += 1
	script.close()

	return script_list