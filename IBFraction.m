function out = IBFraction(R_A, d, theta)

% R_A is asteroid body radius
% d is distance between spacecraft and asteroid
% theta is ion beam divergence angle

out = min([1 R_A/(d*tand(theta))]);

return