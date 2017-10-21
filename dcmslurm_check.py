"""dcmuslurm_check.py
Check a directory containing batch files and logs to determine if and which
jobs need to be re-run. Produces a script for re-running failed jobs.

Lawrence Chiou
20 October 2017
"""

import os

def check_directory(target_directory):
	"""Return a sorted list of the batch files for the jobs that have
	terminated abnormally

	Args:
		target_directory: name of the target directory
	Returns:
		A sorted list of batch files for jobs that have terminated abnormally
	"""
	all_directories = [x[0] for x in os.walk(target_directory)]

	error_files = []
	for directory in all_directories:
		post_files = []
		for file in os.listdir(directory):
			if file.endswith('-ttest.sbatch') or file.endswith('-favg.sbatch'):
				post_files.append(os.path.join(directory, file))
		for file in os.listdir(directory):
			if file.endswith('.sbatch'):
				path_error = os.path.join(directory, '%s.err') \
					% os.path.splitext(file)[0]
				if os.path.exists(path_error):
					if os.stat(path_error).st_size != 0:
						error_files.append(os.path.join(directory, file))
						for post_file in post_files:
							error_files.append(post_file)
				else:
					error_files.append(os.path.join(directory, file))
					for post_file in post_files:
						error_files.append(post_file)

	return sorted(list(set(error_files)))

def make_error(target_directory, path_save):
	"""Writes a shell script for re-running failed jobs in the target
	directory.

	Args:
		target_directory: name of the target directory
		path_save: path to save the script
	Returns:
		None
	"""
	check_directory_out = check_directory(target_directory)

	file = open(path_save, 'w')
	file.write('#!/bin/bash\n\n')

	counter = 1	
	dependency_off = True
	dependency_string_0 = '--dependency=afterany'
	dependency_string = dependency_string_0
	for item in check_directory_out:
		if item.endswith('-favg.sbatch'):
			dependency_off = False
		if dependency_off:
			dependency_string += ':${j%s:20}' % counter
			file.write('j%s=$(sbatch %s)\n' % (counter, item))
		else:
			if dependency_string == dependency_string_0:
				file.write('j%s=$(sbatch %s)\n' % (counter, item))
			else:
				file.write('j%s=$(sbatch %s %s)\n' \
					% (counter, dependency_string, item))
			if item.endswith('-ttest.sbatch'):
				dependency_off = True
				dependency_string = dependency_string_0
		counter += 1

	file.close()