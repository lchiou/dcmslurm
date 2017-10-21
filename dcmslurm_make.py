"""dcmuslurm_make.py
This module generates scripts to run spectral DCM on a SLURM cluster.

The functions can be called independently, but the typical usage is to call
make_scripts_all in a script in which the relevant keywords are given and the
parameters are defined in a separate script. The general use is to generate the
parameters using the dcmslurm_make_params module. An example such script
follows below.

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

import os

def replace_in_outline(**kwargs):
	"""Loads a text outline and replaces all specified keyword strings (in all
	caps) and replaces the ith keyword string (in the outline) with the ith
	variable. Writes to path_output if specified.

	Keyword strings are in the format "$KEYWORD$" (i.e., always bookended by
	dollar signs).

	Args:
		**kwargs:
			- path_outline: file path to the outline
			- overwrite: True if overwriting of an existing file is desired
			- path_output_filename: file path to write the outline
			- keywords to replace in the outline (not case sensitive)
	Returns:
		outline_contents: contents of the outline as a single string
	"""

	# change to directory containing this script and outlines (dcmslurm folder)
	path_script = os.path.abspath(__file__)
	os.chdir(os.path.dirname(path_script))

	path_outline = kwargs['path_outline']
	outline = open(path_outline, 'r')
	outline_contents = outline.read()
	outline.close()

	for key in kwargs:
		key_format = '$%s$' % key.upper()
		outline_contents = outline_contents.replace(key_format, str(kwargs[key]))

	# option to prevent overwriting if file already exists
	if 'overwrite' in kwargs:
		overwrite = kwargs['overwrite']
	else:
		overwrite = True

	if 'path_output_filename' in kwargs:
		path_output_filename = kwargs['path_output_filename']
		if overwrite or (not os.path.exists(path_output_filename) \
			and not overwrite):
			path_output_filename = kwargs['path_output_filename']

			# create directory if it does not exist already
			directory_output = os.path.dirname(path_output_filename)
			if not os.path.exists(directory_output):
				os.makedirs(directory_output)
			script = open(path_output_filename, 'wb')
			script.write(outline_contents)
			script.close()

	return outline_contents

def make_parse(filename, **kwargs):
	"""Loads the outline 'outline_sh.txt' and replaces the ith keyword string
	(in the outline) with the ith variable. Writes to path_output if specified.

	Keyword strings are in the format "$KEYWORD$" (i.e., always bookended by
	dollar signs).

	Args:
		filename: output file path
		**kwargs:
			- overwrite: True if overwriting of an existing file is desired
			- keywords to replace in the outline (not case sensitive)
	Returns:
		None
	"""
	replace_in_outline( \
		path_outline='outline_sh.txt', \
		path_output_filename=os.path.join( \
			os.path.dirname(kwargs['path_parsed']), filename), \
		commands=replace_in_outline(path_outline='commands_parse.txt', \
			**kwargs), \
		**kwargs)

def make_estimate(filename, commands_variable, **kwargs):
	"""Loads the outline 'outline_sbatch.txt' and replaces the ith keyword
	string (in the outline) with the ith variable. Writes to path_output if
	specified. Replaces the commands keyword with the commands in
	'commands_estimate.txt' (for running 'dcmslurm_estimate.m').

	Keyword strings are in the format "$KEYWORD$" (i.e., always bookended by
	dollar signs).

	Args:
		filename: output file path
		commands_variable: variable commands
		**kwargs:
			- overwrite: True if overwriting of an existing file is desired
			- keywords to replace in the outline (not case sensitive)
	Returns:
		None
	"""
	replace_in_outline( \
		path_outline='outline_sbatch.txt', \
		path_output_filename=os.path.join(kwargs['path_output'], filename), \
		script_name=os.path.splitext(filename)[0], \
		path_log= '%s.log' % os.path.join(kwargs['path_output'], \
			os.path.splitext(filename)[0]), \
		path_err= '%s.err' % os.path.join(kwargs['path_output'], \
			os.path.splitext(filename)[0]), \
		commands=replace_in_outline(path_outline='commands_estimate.txt', \
			variable=commands_variable, \
			**kwargs), \
		**kwargs)

def make_favg(filename, **kwargs):
	"""Loads the outline 'outline_sbatch.txt' and replaces the ith keyword
	string (in the outline) with the ith variable. Writes to path_output if
	specified. Replaces the commands keyword with the commands in
	'commands_favg.txt' (for finding the average F among subjects).

	Keyword strings are in the format "$KEYWORD$" (i.e., always bookended by
	dollar signs).

	Args:
		filename: output file path
		**kwargs
			- overwrite: True if overwriting of an existing file is desired
			- keywords to replace in the outline (not case sensitive)
	Returns:
		None
	"""
	replace_in_outline( \
		path_outline='outline_sbatch.txt', \
		path_output_filename=os.path.join(kwargs['path_output'], filename), \
		script_name=os.path.splitext(filename)[0], \
		path_log= '%s.log' % os.path.join(kwargs['path_output'], \
			os.path.splitext(filename)[0]), \
		path_err= '%s.err' % os.path.join(kwargs['path_output'], \
			os.path.splitext(filename)[0]), \
		commands=replace_in_outline(path_outline='commands_favg.txt', \
			**kwargs), \
		**kwargs)

def make_ttest(filename, **kwargs):
	"""Loads the outline 'outline_sbatch.txt' and replaces the ith keyword
	string (in the outline) with the ith variable. Writes to path_output if
	specified. Replaces the commands keyword with the commands in
	'commands_ttest.txt' (for t-testing among subjects---recommended only as a
	preliminary measure).

	Keyword strings are in the format "$KEYWORD$" (i.e., always bookended by
	dollar signs).

	Args:
		filename: output file path
		**kwargs
			- overwrite: True if overwriting of an existing file is desired
			- keywords to replace in the outline (not case sensitive)
	Returns:
		None
	"""
	replace_in_outline( \
		path_outline='outline_sbatch.txt', \
		path_output_filename=os.path.join(kwargs['path_output'], filename), \
		script_name=os.path.splitext(filename)[0], \
		path_log= '%s.log' % os.path.join(kwargs['path_output'], \
			os.path.splitext(filename)[0]), \
		path_err= '%s.err' % os.path.join(kwargs['path_output'], \
			os.path.splitext(filename)[0]), \
		commands=replace_in_outline(path_outline='commands_ttest.txt', \
			**kwargs), \
		**kwargs)

def make_run(filename, script_list_estimate, script_list_post, **kwargs):
	"""Loads the outline 'outline_sh.txt' and replaces the ith keyword string
	(in the outline) with the ith variable. Writes to path_output if specified.
	Writes the list of all batch scripts to be run to a shell script.

	Args:
		filename: output filename
		script_list_estimate: list of scripts calling dcmslurm_estimate.m
		script_list_post: list of scripts for "post-processing" (e.g., t-test)
		**kwargs
			- overwrite: True if overwriting of an existing file is desired
			- keywords to replace in the outline (not case sensitive)
	Returns:
		None
	"""
	commands_run = ''

	# string needed to make sure post-processing tasks happen after DCM fitting
	dependency_string = '--dependency=afterany'

	counter = 1
	for script_name in script_list_estimate:
		commands_run += 'j%s=$(sbatch %s)\n' % (counter, script_name)
		dependency_string += ':${j%s:20}' % (counter)
		counter += 1

	commands_run += '\necho %s jobs submitted\n' % filename

	if len(script_list_post) > 0:
		for script_name in script_list_post:
			commands_run += '\nj%s=$(sbatch %s %s)' \
				% (counter, dependency_string, script_name)
			counter += 1

	replace_in_outline( \
		path_outline='outline_sh.txt', \
		path_output_filename=os.path.join(kwargs['path_output'], filename), \
		commands=commands_run, \
		**kwargs)

def make_run_all(filename, script_list_run, **kwargs):
	"""Loads the outline 'outline_sh.txt' and replaces the ith keyword string
	(in the outline) with the ith variable. Writes to path_output if specified.
	Writes the list of shell scripts to be run to a "master" shell script.

	Args:
		filename: output filename
		script_list_run: list of shell scripts to be run
		**kwargs
			- overwrite: True if overwriting of an existing file is desired
			- keywords to replace in the outline (not case sensitive)
	Returns:
		None
	"""
	commands_run_all = ''
	for script_name in script_list_run:
		directory_script = os.path.dirname(script_name)
		commands_run_all += \
			'hasmatfile=$(find %s -type f \( -name "*.mat" \))\n' \
			% directory_script
		commands_run_all += \
			'if [ ${#hasmatfile} -eq 0 ]; then sh %s; fi\n\n' \
			% script_name

	replace_in_outline( \
		path_outline='outline_sh.txt', \
		path_output_filename=os.path.join( \
			os.path.dirname(kwargs['path_parsed']), filename), \
		commands=commands_run_all, \
		**kwargs)

def make_scripts(include_parse=True, include_favg=True, include_ttest=True, \
	**kwargs):
	"""Makes all individual scripts (for DCM estimation and "post-processing")
	and accompanying shell scripts for submitting and running all scripts for a
	single set of parameters.

	Args:
		include_parse: True if scripts for parsing the MATLAB data file should be
			included
		include_favg: True if scripts for calculting the average F score should
			be included
		include_ttest: True if scripts for t-testing should be included
		**kwargs
			- overwrite: True if overwriting of an existing file is desired
			- job_name: job name that should prefix each filename
			- path_output: output directory
			- path_raw: path to the MATLAB data file
			- labels: labels for the experimental conditions
			- subjects: number of subjects
			- keywords to replace in the outline (not case sensitive)
	Returns:
		None
	"""
	job_name = kwargs['job_name']
	path_output = kwargs['path_output']
	path_raw = kwargs['path_raw']

	# list of scripts for make_run
	script_list_estimate = []
	script_list_post = []

	if include_parse:
		script_name_parse = '%s-parse.sh' \
			% os.path.basename(os.path.normpath(path_raw))
		make_parse(filename=script_name_parse, **kwargs)

	# create estimate scripts
	label_string = kwargs['labels']
	labels = [x[1:-1] for x in label_string[1:-1].split(', ')]
	subjects = kwargs['subjects']
	for label in labels:
		for subject in range(1, subjects+1):
			script_name_estimate = '%s-%s-%s.sbatch' \
				% (job_name, label, str(subject))
			commands_variable = "'%s', %d, %d" % (label, subject, subject)
			script_list_estimate.append(os.path.join(path_output, \
				script_name_estimate))
			make_estimate(filename=script_name_estimate, \
				commands_variable=commands_variable, **kwargs)

	if include_favg:
		script_name_favg = '%s-favg.sbatch' % job_name
		script_list_post.append(os.path.join(path_output, script_name_favg))
		make_favg(filename=script_name_favg, **kwargs)

	if include_ttest:
		script_name_ttest = '%s-ttest.sbatch' % job_name
		script_list_post.append(os.path.join(path_output, script_name_ttest))
		make_ttest(filename=script_name_ttest, **kwargs)

	script_name_run = '%s-run.sh' % job_name
	make_run(script_name_run, script_list_estimate, script_list_post, **kwargs)

def make_scripts_all(**kwargs):
	"""Makes all individual scripts (for DCM estimation and "post-processing")
	and accompanying shell scripts for submitting and running all scripts for
	many parameters.

	Args:
		**kwargs
			- path_params: path to the parameter files
			- directory_output: output directory
			- prefix_output: any prefix that should go at the beginning of file
				names
			- keywords to replace in the outline (not case sensitive)
	Returns:
		None
	"""
	path_params = kwargs['path_params']
	directory_output = kwargs['directory_output']
	prefix_output = kwargs['prefix_output']

	file_params = open(path_params, 'r')
	list_params = []
	for line in file_params.readlines():
		line_split = line.split('&')
		if len(line_split) == 3:
			params = {}
			params['matrix_A'] = line_split[0]
			params['matrix_C'] = line_split[1]
			params['matrix_hidden'] = line_split[2].replace('\n', '')
			list_params.append(params)
	file_params.close()
	
	script_list_run = []
	for params in list_params:

		# job_name is matrix_A and matrix_hidden converted from a binary string
		string_raw = params['matrix_A'] + params['matrix_hidden']
		string_bin = filter(lambda d: d.isdigit(), string_raw)
		job_name = '%s_%s' % (prefix_output, \
			str(int(string_bin, 2)).zfill(len(str(int(string_bin.replace('0', \
			'1'), 2)))))
		path_output = os.path.join(directory_output, job_name)
	
		make_scripts(
			path_output = path_output, \
			job_name = job_name, \
			matrix_A = params['matrix_A'], \
			matrix_C = params['matrix_C'], \
			matrix_hidden = params['matrix_hidden'], \
			**kwargs)

		script_list_run.append('%s-run.sh' % os.path.join(path_output, job_name))

	script_name_run_all = '%s-run_all.sh' % prefix_output
	make_run_all(script_name_run_all, script_list_run, **kwargs)