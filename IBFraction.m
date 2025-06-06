function out = IBFraction(R_A, d, theta)

% R_A is asteroid body radius
% d is distance between spacecraft and asteroid
% theta is ion beam divergence angle

F = min([1 R_A/(d*tan(theta))]);
out = F;

return