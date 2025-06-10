function out = propagate_WT(~, input, mu, thrust, M_A, F)

    r = input(1:3);
    v = input(4:6);
     
    r_norm = norm(r); % r needs to be normalized to get the actual r value, r in this code is the r vector. (lecture 1)
    v_norm = norm(v);
    
    a_asteroid = -mu / r_norm^3 * r;
   
    %bottom of lecture 2, gives double dot r vector which is acceleration of the body.
  
    a_thrust = F * thrust / M_A * v/v_norm; % km/s^2
    
    
    a_total = a_asteroid + a_thrust; % added together bc they are applied in the same direction

    out = [v ; a_total];

end