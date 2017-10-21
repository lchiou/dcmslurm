function dcmslurm_parsefile(path_parsed, data_in, labels)

    % Parses a loaded MATLAB data file data_in and writes the directory
    % structure (with conditions specified by labels) needed for
    % dcmslurm_estimate. 
    %
    % Args:
    % path_parsed - path to the directory that should contain the parsed files
    %    (the directory is created if it does not already exist)
    % data_in - input MATLAB data file
    % labels - labels for the experimental conditions
    %
    % Returns:
    % None
    %
    % Lawrence Chiou
    % 20 October 2017

    if ~exist(path_parsed, 'dir')
        mkdir(path_parsed)
    end

    cd(path_parsed)
    
    data_in_dim = size(data_in);
    
    for condition = 1:data_in_dim(2)
       
        data_condition = data_in{condition};
        mkdir(labels{condition})
        cd(labels{condition})
        data_condition_dim = size(data_condition);
        
        for subject = 1:data_condition_dim(1)
            filename_subject = strcat('subject_',int2str(subject));
            mkdir(filename_subject)
            cd(filename_subject)
            
            for node = 1:data_condition_dim(3)
                filename_node = strcat(filename_subject, ...
                    strcat('_node_',int2str(node)));
                Y = transpose(data_condition(subject,:,node));
                save(filename_node,'Y')
            end
            cd ..
        end
        cd ..
    end
    
    cd ..
    
    end