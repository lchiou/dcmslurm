function all_results = dcmslurm_aggregate(path_output, subjects, ...
    conditions, n_matrices)
    
    % Given the location of all output files, aggregate all results into a
    % single structure array.
    %
    % Args:
    % path_output - output file name as a string
    % subjects - number of subjects
    % conditions - list containing the labels for the experimental conditions
    % n_matrices - number of output matrices per subject per condition
    %
    % Returns:
    % all_results - structure array containing all output results
    %
    % Lawrence Chiou
    % 20 October 2017

    files = dir(path_output);
    files(1:2) = [];
    dirflags = [files.isdir];
    subfolders = files(dirflags);
    
    cd(path_output)
    all_results(subjects * length(conditions) * n_matrices).F = [];
    counter = 0;
    for i=1:length(subfolders)
        cd(subfolders(i).name)
        subfiles = dir();
        subfiles(1:2) = [];
        for j=1:length(subfiles)
            filename = subfiles(j).name;
            if length(filename) > 15
                if strcmp(filename(1:15), 'DCMvtu_no_mean_')
                    load(filename);
                    counter = counter + 1;
                    filename_split ...
                        = strsplit(filename(1:length(filename)-4), '_');
                    all_results(counter).condition ...
                        = filename_split(length(filename_split)-1);
                    all_results(counter).subject ...
                        = str2double(filename_split(length(filename_split)));
                    all_results(counter).A = Ep.A;
                    all_results(counter).F = F;
                end
            end
        end
        cd ..
    end
    all_results = all_results(1:counter);
end