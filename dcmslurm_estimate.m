function dcmslurm_estimate(path_raw, path_parsed, path_output, ...
    save_in_path_parsed, em_steps_max, ...
    matrix_A, matrix_C, matrix_hidden, ...
    label, subject_first, subject_last)
    
    % Fits DCM parameters for subjects in a given range from subject_first to
    % subject_last for a given condition specified by label. The folder
    % path_parsed contains the files created by estimate_dcmslurm_parse.
    % 
    % The folder path_raw contains 'SPM.mat' and 'VOI_M1_1.mat'.
    %
    % The array matrix_hidden specifies the nodes that are hidden (in the
    % matrix if hidden, omitted if not). Hidden nodes must always have indices
    % greater than those of non-hidden nodes.
    %
    % The output is saved in path_output unless save_in_path_parsed is
    % true, in which case the output is saved in path_parsed with the same
    % file structure as the files in path_parsed.
    %
    % Args:
    % path_raw - path to the estimation scripts from SPM
    % path_parsed - path containing the input files to be parsed
    % path_output - output is saved in path_output unless save_in_path_parsed
    %   is zero
    % save_in_path_parsed - 1 if output is saved in path_parsed; 0 otherwise
    % em_steps_max - maximum number of steps to use in the E-M algorithm
    % matrix_A - A matrix (connections). Edges go from columns to rows.
    % matrix_C - C matrix (inputs)
    % matrix_hidden - vector specifying hidden nodes
    % label - string label used in naming the output files
    % subject_first - numerical label for first subject
    % subject_last - numerical label for last subject
    %
    % Returns:
    % None
    %
    % Lawrence Chiou and David Bernal-Casas
    % 20 October 2017

    % directory for the given condition specified by label
    if save_in_path_parsed
        directory_save = fullfile(path_parsed, label);
    else
        directory_save = path_output;
    end
    
    matrix_A_dim = size(matrix_A);
    matrix_C_dim = size(matrix_C);
    matrix_hidden_dim = size(matrix_hidden);
    non_hidden_nodes_num = matrix_C_dim(2) - matrix_hidden_dim(2);

    for i = subject_first:subject_last
        string_subject = sprintf('subject_%s', num2str(i));

        % save in subject's folder if true but path_output if false
        if save_in_path_parsed
            path_save = fullfile(directory_save, string_subject);
        else
            path_save = directory_save;
        end

        clear DCM
 
        load(fullfile(path_raw, 'SPM.mat'));
        load(fullfile(path_raw, 'VOI_M1_1.mat'), 'xY');
        DCM_xY_Original = xY;
        
        Y_is_nan_all = false;   % counter for checking NaN
        
        % load data for non-hidden nodes
        for j = 1:non_hidden_nodes_num
            string_node = sprintf('subject_%s_node_%s.mat', ...
                num2str(i), num2str(j));
            load(fullfile(path_parsed, label, string_subject, string_node), ...
                'Y');
            DCM_xY_Original.y = Y;
            DCM_xY_Original.u = Y;    
            DCM.xY(j) = DCM_xY_Original;
            if dcmslurm_Y_is_nan(Y)
                Y_is_nan_all = true;
            end
        end

        % load data for hidden nodes
        rng(1337)   % set fixed seed
        if matrix_hidden_dim(2) > 0
            for j = non_hidden_nodes_num+1:non_hidden_nodes_num+ ...
                matrix_hidden_dim(2)
                Y = DCM_xY_Original.y + rand(1, length(xY))/10;
                DCM_xY_Original.y = Y;
                DCM_xY_Original.u = Y;
                DCM.xY(j) = DCM_xY_Original;
            end
        end

        % specify DCM options
        DCM.n = matrix_C_dim(2); %length(DCM.xY);
        DCM.v = length(DCM.xY(1).u);

        DCM.Y.dt = SPM.xY.RT;
        DCM.Y.X0 = DCM.xY(1).X0;

        for j = 1:DCM.n
            DCM.Y.y(:,j) = DCM.xY(j).u;
            DCM.Y.name{j} = DCM.xY(j).name;
        end

        DCM.Y.Q = spm_Ce(ones(1,DCM.n) * DCM.v);

        DCM.U.dt =  SPM.Sess.U(1).dt;
        DCM.U.name = [SPM.Sess.U(1,2).name];
        DCM.U.u = [SPM.Sess.U(2).u(33:end,1)];

        DCM.delays = repmat(SPM.xY.RT, matrix_C_dim(2), 1);
        DCM.TE = 0.012;

        DCM.options.nonlinear = 0;
        DCM.options.two_state = 0;
        DCM.options.stochastic = 0;
        DCM.options.analysis = 'CSD';
        DCM.options.nograph = 1; % this command is actually broken in SPM
        DCM.M.nograph = 1; % this one works: no figures and no JVM needed
        DCM.options.nmax = 8;
        DCM.options.Nmax = em_steps_max;
        DCM.options.hidden = matrix_hidden;

        N_A = 1;
        N_B = 1;
        N_C = 1;

        DCM_Fixed_A = zeros(matrix_A_dim(1), matrix_A_dim(2), N_A);
        DCM_Fixed_A(:,:,1) = matrix_A;
        DCM_Fixed_B = zeros(matrix_A_dim(1), matrix_A_dim(2), 1, N_B);
        DCM_Fixed_C = zeros(matrix_C_dim(2), 1, N_C);   
        DCM_Fixed_C(:,:,1) = matrix_C;
        
        if Y_is_nan_all == false
            DCM.a = DCM_Fixed_A(:,:,1);
            DCM.b = DCM_Fixed_B(:,:,:,1);
            DCM.c = DCM_Fixed_C(:,:,1);
            filename_output = sprintf('DCMvtu_no_mean_%s_%s.mat', label, num2str(i));
            DCM.name = filename_output;
            save(fullfile(path_save, filename_output), 'DCM');
            fprintf('\n');
            spm_dcm_fmri_csd(fullfile(path_save, filename_output));
            fprintf('\nSubject %d estimated\n\n', i);
        else
            fprintf('\nIncomplete data for subject %d\n\n', i);
        end
    end