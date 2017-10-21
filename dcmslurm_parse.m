function dcmslurm_parse(labels, path_raw_file, path_parsed)

	% Loads a MATLAB file and writes the directory structure (with conditions
	% specified by labels) needed for dcmslurm_estimate. 
	%
	% Args:
	% labels - labels for the experimental conditions
    % path_raw_file - path to the MATLAB data file
    % path_parsed - path to the directory that should contain the parsed files
    %    (the directory is created if it does not already exist)
    %
    % Returns:
    % None
    %
    % Lawrence Chiou
    % 20 October 2017

    load(path_raw_file);
    dcmslurm_parsefile(path_parsed, tsAll, labels);