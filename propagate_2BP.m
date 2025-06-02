function out = propagate_2BP(~, input, mu, thrust_mag)

    r = input(1:3);
    v = input(4:6);
     
    r_norm = norm(r); % r needs to be normalized to get the actual r value, r in this code is the r vector. (lecture 1)
    v_norm = norm(v);
    
    a_asteroid = -mu/r_norm^3 * r; %bottom of lecture 2, gives double dot r vector which is acceleration of the body.
    if v_norm == 0
        a_thrust = [0;0;0]
    else
    a_thrust = thrust_mag * v/norm(v);
    end

    out = [v ; a_asteroid + a_thrust];
end