function dcmslurm_ttest(path_output, label_frq, ...
    subject_first, subject_last, p_crit)
    
    % Displays statistically significant weights for DCM output parameters. The
    % statistically significant weights are saved in path_output. (t-testing
    % should be used as a preliminary measure only.)
    %
    % Args:
    % path_output - directory containing the input and output files (must be
    %    the same)
    % label_frq - label for the given experimental condition
    % subject_first - numerical label for first subject
    % subject_last - numerical label for last subject
    % p_crit - critical p-value
    %
    % Returns:
    % None
    %
    % Lawrence Chiou
    % 20 October 2017
    
    Ep_A_dim = [0, 0];
    counter = 0;
    data_cell = {};

    for i = subject_first:subject_last
        
        str = sprintf('DCMvtu_no_mean_%s_%s.mat', label_frq, num2str(i));

        if exist(fullfile(path_output, str), 'file') == 2
	        load(fullfile(path_output, str), 'Ep');
	        counter = counter + 1;

	        Ep_A_dim = size(Ep.A);
            if i == subject_first
                data_cell = cell(Ep_A_dim(1), Ep_A_dim(2));
            end
            for j = 1:Ep_A_dim(1)
                for k = 1:Ep_A_dim(2)
                    data_cell{j,k}{end+1} = Ep.A(j,k); %#ok<AGROW>
                end
            end
        end
    end

	if counter > 0
		p_vals = zeros(Ep_A_dim(1), Ep_A_dim(2));
        means = zeros(Ep_A_dim(1), Ep_A_dim(2));
        means_crit = zeros(Ep_A_dim(1), Ep_A_dim(2));
        
		p_vals_dim = size(p_vals);
        for j = 1:p_vals_dim(1)
            for k = 1:p_vals_dim(2)
   				[h,p] = ttest(cell2mat(data_cell{j,k})); %#ok<ASGLU>
        		p_vals(j,k) = p;
            end
        end
        
        for j = 1:Ep_A_dim(1)
            for k = 1:Ep_A_dim(2)
                means(j,k) = mean(cell2mat(data_cell{j,k}));
                if isnan(p_vals(j,k)) == false
                    if p_vals(j,k) < p_crit
                        means_crit(j,k) = means(j,k);
                    end
                end
            end
        end

        save(fullfile(path_output, sprintf('%s_dcm_pvals.mat', label_frq)), ...
            'p_vals');
        save(fullfile(path_output, sprintf('%s_dcm_means.mat', label_frq)), ...
            'means');
    	save(fullfile(path_output, sprintf('%s_dcm_means_crit_%s.mat', ...
            label_frq, num2str(p_crit))), 'means_crit');
	else
        % returns error message if no subject output files are found
    	fprintf('Sample size is zero - no tests performed (%s, p = %d).\n', ...
            label_frq, p_crit)
	end
