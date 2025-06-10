function [t_all, r_all, v_all, DV_tot, a_all, e_all] = ODE_Handle(rA0, vA0, thrust, array_num, dt, mass_fuel, mass_sc, Isp, M_A, R_A, d, theta)

% rA0 and vA0 come from the inital data
% Thrust will stay constant for now
% dt is the stepsize
% mass_fuel is the mass of the xenon fuel on board space craft
% mass_sc is the total mass of the space craft including the fuel
% Isp is the specific impulse in seconds
% M_A is the mass of the asteroid (in kilograms)
% R_A is the radius of the asteroid (in meters)
% d is the stand off distance between the space craft and the asteroid (in meters)
% theta is the Ion Beam Divergence Angle (in degrees)

mu = 1.32712E+11; % km^3/s^2
tol = 1e-12; % acceptable tolerance
options = odeset('RelTol', tol, 'AbsTol', tol); % ODE45 options
g = 0.00980665; % km/s^2

thrust = thrust*array_num;

thrust = thrust / 1000; % to convert to kg*km/s^2 (kN)

mdot = thrust / (g * Isp); % mass flow rate of the ion thruster

% Ion Beam coupling efficiency
F = IBFraction(R_A, d, theta);
fprintf("Beam coupling fraction F = %.3f\n", F);

t_tot = 0;
DV_tot = 0;

r_all = [];
v_all = [];
t_all = [];
a_all = [];
e_all = [];

i_total = 0; % total impulse before dividing by M_A

DV = F*(thrust*dt)/(M_A + ((thrust/(g*Isp))*dt));

% max_step = 1000;
step = 0;
first_loop = true;

fprintf('[t = %6d s] mass_sc = %.2f kg, a_thrust = %.2e km/s^2\n', t_tot, mass_sc, thrust / mass_sc);

while mass_fuel > 0 % && step < max_step
    

	[~, RV] = ode45(@(t, y) propagate_2BP(t, y, mu, thrust, M_A, F), [0 dt], [rA0; vA0], options);
    
    % Debug can remove soon...
    % if any(isnan(RV(end,:))) || any(isinf(RV(end,:)))
    %     warning('NaN or Inf detected at step %d (t = %d s)', step, t_tot);
    %     break;
    % end

    % r_Af = RV(1:3);
    % v_Af = RV(4:6);
    % 
    % % Saves the Output of Function to be graphed in main file
	% % RV_all = [RV_all; RV];
    % r_all = [r_all; r_Af];
    % v_all = [v_all; v_Af];
    % t_all = [t_all; t_tot];
    
    % Updates and Extracts all time steps
    N = size(RV,1);
    r_all = [r_all; RV(:,1:3)];
    v_all = [v_all; RV(:,4:6)+DV];

    t_span = linspace(t_tot, t_tot + dt, N)';
    t_all = [t_all; t_span]; % interpolate time steps  + (0:N-1)' * (dt/(N-1))

    [a_step, e_step] = orbit_elements(RV(:,1:3), RV(:,4:6), mu);
    a_all = [a_all; a_step];
    e_all = [e_all; e_step];

    r_Af = RV(end,1:3)';
    v_Af = RV(end,4:6)';

    % Updating Mass of the Space Craft and the Fuel
    fuel_used = mdot * dt;
    mass_fuel = mass_fuel - fuel_used;
    mass_sc = mass_sc - fuel_used;

    % Updates ΔV imparted to asteroid
    i_total = i_total + F * thrust * dt;
    % DV_step = (F * thrust * dt) / M_A;
    % DV_tot = DV_tot + DV_step;
   

    % Updating State
	rA0 = r_Af;
	vA0 = v_Af;

    t_tot = t_tot + dt;

    
    % Debug terms

    if mass_fuel < 0
            break;
    end

    step = step + 1;

    if first_loop
    fprintf('Initial a_thrust: %.3e km/s²\n', thrust / mass_sc);
    fprintf('Initial mdot: %.3e kg/s\n', mdot);
    fprintf('Initial fuel: %.2f kg\n', mass_fuel);
    fprintf('Initial mass_sc: %.2f kg\n', mass_sc);
    first_loop = false;
    end

end

DV_tot = F * i_total / (M_A + ((thrust/(g*Isp))*dt)) ;


return


