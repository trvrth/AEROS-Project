function out = IBFraction(R_A, d, theta)

% R_A is asteroid body radius
% d is distance between spacecraft and asteroid
% theta is ion beam divergence angle

beam_radius = d*tand(theta);
frac = (R_A/beam_radius); % maybe squared bc of area?
out = min([1 frac]);

return