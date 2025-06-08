function out = propagate_2BP(~, input, mu, thrust, M_A, F)

    r = input(1:3);
    v = input(4:6);
     
    r_norm = norm(r); % r needs to be normalized to get the actual r value, r in this code is the r vector. (lecture 1)
    v_norm = norm(v);
    
    if r_norm < 1e-3  % prevent divide by near-zero
        warning('r_norm too small — skipping gravitational force');
        a_asteroid = [0; 0; 0];
    else
        a_asteroid = -mu / r_norm^3 * r;
    end

 %bottom of lecture 2, gives double dot r vector which is acceleration of the body.
    
    if v_norm < 1e-6
        warning('v_norm too small — skipping gravitational force');
        a_thrust = [0;0;0];
    else
        a_thrust = F * thrust / M_A * v/v_norm; % m/s^2
    end
    
    a_total = a_asteroid + a_thrust;

    out = [v ; a_total];

end