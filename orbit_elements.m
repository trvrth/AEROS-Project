function [a_scalar, e_scalar, e_vec] = orbit_elements(r, v, mu)
    h = cross(r, v);
    r_norm_scalar = norm(r);
    v_norm_scalar = norm(v);
    
    % To find Semi-Major Axis
    orbit_energy = (v_norm_scalar^2)/2 - mu / r_norm_scalar;
    a_scalar = -mu / (2 * orbit_energy);

    % Eccentricity vector
    e_vec = (cross(v, h) / mu) - (r / r_norm_scalar);
    e_scalar = norm(e_vec);
    
end
