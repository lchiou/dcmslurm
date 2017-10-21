function dcmslurm_favg(path_output, label_frq, ...
    subject_first, subject_last)
    
    % Computes the mean free energy for a given range of subjects and condition
    % label_frq. The folder path_parsed contains the files created by
    % dcmslurm_parse. The computed mean is stored in the folder for the
    % condition label_frq.
    %
    % Args:
    % path_output - directory containing the input and output files (must be
    %    the same)
    % label_frq - label for the given experimental condition
    % subject_first - numerical label for first subject
    % subject_last - numerical label for last subject
    %
    %
    % Returns:
    % None
    %
    % Lawrence Chiou
    % 20 October 2017
    
    counter = 0;
    F_total = 0;
    for i = subject_first:subject_last
        str = sprintf('DCMvtu_no_mean_%s_%s.mat', label_frq, num2str(i));
        if exist(fullfile(path_output, str), 'file') == 2
	        load(fullfile(path_output, str), 'F');
	        counter = counter + 1;
            F_total = F_total + F;
        end
    end

	if counter > 0
        Favg = F_total / counter;
        save(fullfile(path_output, sprintf('%s_dcm_Favg.mat',label_frq)), 'Favg');
        save(fullfile(path_output, sprintf('%s_dcm_n.mat',label_frq)), 'counter');
	else
        % returns error message if no subject output files are found
    	fprintf('Sample size is zero - no mean calculated (%s).\n', label_frq)
	end