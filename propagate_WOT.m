function out = propagate_WOT(~, input, mu, mass_sc, standoff, infront)

    r = input(1:3);
    v = input(4:6);
     
    r_norm = norm(r); % r needs to be normalized to get the actual r value, r in this code is the r vector. (lecture 1)
    v_norm = norm(v);

    a_asteroid = -mu / r_norm^3 * r;
    
    % Spacecraft gravity using standoff distance
    standoff = standoff/1000; % to put it in km
    G = 6.67430e-20; % km^3/kg/s^2
    v_unit = v / v_norm;
    r_sc = r + v_unit *standoff;
    r_rel = r_sc - r;
    r_rel_norm = norm(r_rel);
    a_sc = -G * mass_sc / r_rel_norm^3 * r_rel;

    a_total = a_asteroid + infront*(a_sc);

    out = [v ;  a_total];

end