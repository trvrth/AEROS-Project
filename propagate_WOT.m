function out = propagate_WOT(~, input, mu)

    r = input(1:3);
    v = input(4:6);
     
    r_norm = norm(r); % r needs to be normalized to get the actual r value, r in this code is the r vector. (lecture 1)
    
    a_asteroid = -mu / r_norm^3 * r;

    out = [v ; a_asteroid];

end