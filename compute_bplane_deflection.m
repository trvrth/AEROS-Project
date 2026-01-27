function [B_T, B_R, B_total] = compute_bplane_deflection(r_nom, v_nom, r_def, v_earth)
% COMPUTE_BPLANE_DEFLECTION
% Projects the deflection vector onto the Earth-centered B-plane.
%
% Inputs:
%   r_nom   - [3x1 or 1x3] Nominal asteroid position [km]
%   v_nom   - [3x1 or 1x3] Nominal asteroid velocity [km/s]
%   r_def   - [3x1 or 1x3] Deflected asteroid position [km]
%   v_def   - [3x1 or 1x3] Deflected asteroid velocity [km/s]
%   r_earth - [3x1 or 1x3] Earth's position [km]
%   v_earth - [3x1 or 1x3] Earth's velocity [km/s]
%
% Outputs:
%   B_T     - B-plane projection along T-axis [km]
%   B_R     - B-plane projection along R-axis [km]
%   B_total - Total magnitude of deflection in B-plane [km]

    % Ensure column vectors
    r_nom = r_nom(:);
    v_nom = v_nom(:);
    r_def = r_def(:);
    v_earth = v_earth(:);

    % 1. Compute approach velocity vector
    V_inf = v_nom - v_earth;
    S_hat = V_inf / norm(V_inf);

    % 2. Construct B-plane axes
    K_hat = [0; 0; 1];  % Ecliptic north

    % Handle edge case if V_inf nearly aligned with K_hat
    T_hat = cross(S_hat, K_hat);
    if norm(T_hat) < 1e-6
        K_hat = [1; 0; 0];  % Switch to a non-parallel axis
        T_hat = cross(S_hat, K_hat);
    end
    T_hat = T_hat / norm(T_hat);
    R_hat = cross(T_hat, S_hat);  % Right-handed system
    R_hat = R_hat / norm(R_hat);

    % 3. Compute position offset vector
    delta_r = r_def - r_nom;

    % 4. Project onto B-plane axes
    B_T = dot(delta_r, T_hat);
    B_R = dot(delta_r, R_hat);
    B_total = norm([B_T; B_R]);
end