function Y_is_nan = dcmslurm_Y_is_nan(Y)
    
    % Determines whether any entires of a matrix are NaN.
    %
    % Args:
    % Y - given matrix
    %
    % Returns:
    % Y_is_nan - true if any entries are NaN; false otherwise.
    %
    % Lawrence Chiou
    % 20 October 2017

	Y_nan = isnan(Y);
	Y_nan_dim = size(Y_nan);
	Y_is_nan = false;
	for j = 1:Y_nan_dim(2)
        if Y_nan(j)
			Y_is_nan = true;
        end
	end