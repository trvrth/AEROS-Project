function [a, e, e_vec, a_scalar, e_scalar] = orbit_elements(r, v, mu)
    h = cross(r, v);
    r_norm = sqrt(sum(r.^2, 2)); % norm function did not work for this
    v_norm = sqrt(sum(v.^2, 2));

    r_norm_scalar = norm(r); % norm function did not work for this
    v_norm_scalar = norm(v);
    
    % == Vectorized ==

    % To find Semi-Major Axis
    orbit_energy = (v_norm.^2)/2 - mu ./ r_norm;
    a = -mu ./ (2 * orbit_energy);
    
    % Eccentricity vector
    e_vec = (cross(v, h) ./ mu) - (r ./ r_norm);
    e = sqrt(sum(e_vec.^2, 2));

    
    % == Scalar ==
    
    % To find Semi-Major Axis
    orbit_energy = (v_norm_scalar^2)/2 - mu / r_norm_scalar;
    a_scalar = -mu / (2 * orbit_energy);

    % Eccentricity vector
    e_vec_scalar = (cross(v, h) / mu) - (r / r_norm_scalar);
    e_scalar = norm(e_vec_scalar);

end
