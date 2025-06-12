function [t_all, r_all, v_all, DV_tot, a_all, e_all] = ODE_Handle(rA0, vA0, thrust, array_num, sc_num, dt, mass_fuel, mass_sc, Isp, M_A, R_A, d, theta,orbit_window)

% rA0 and vA0 come from the inital data
% Thrust will stay constant for now
% dt is the stepsize
% array_num is the number of thrusters that are on the spacecraft pointed towards the asteroid
% sc_num is the number of identical space crafts, participating. 
% mass_fuel is the mass of the xenon fuel on board space craft
% mass_sc is the total mass of the space craft including the fuel
% Isp is the specific impulse in seconds
% M_A is the mass of the asteroid (in kilograms)
% R_A is the radius of the asteroid (in meters)
% d is the stand off distance between the space craft and the asteroid (in meters)
% theta is the Ion Beam Divergence Angle (in degrees)
% orbit_window is the window in the orbit that the thrusters will turn on, 0 is perihelion and 180 is aphelion. This number is in degrees. 

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

angle_window = orbit_window;

i_total = 0; % total impulse before dividing by M_A

%DV = F*(thrust*dt)/(M_A + ((thrust/(g*Isp))*dt)); question about why the
%mass flow rate is on the bottom with M_A

% max_step = 1000;
step = 0;
first_loop = true;

fprintf('[t = %6d s] mass_sc = %.2f kg, a_thrust = %.2e km/s^2\n', t_tot, mass_sc, thrust / mass_sc);

%Calculate starting o_angle
[~, ~, e_vec] = orbit_elements(rA0, vA0, mu);

e_unit = e_vec/norm(e_vec);
r_unit = rA0/norm(rA0);

o_angle = acos((dot(e_unit,r_unit))); 
    
o_angle = rad2deg(o_angle);

% Start of the Propagation simulation, runs until the fuel runs out 
while mass_fuel > 0
    fprintf('Angle to perihelion: %.2f°\n', o_angle);

    % Checks angle and applies thrust only at the angle provided
    if o_angle < angle_window

        [~, RV] = ode45(@(t, y) propagate_WT(t, y, mu, thrust*sc_num, M_A, F, mass_sc, d), [0 dt], [rA0; vA0], options);
        fprintf('thrust applied!');
       

        % Updating Mass of the Space Craft and the Fuel
        fuel_used = mdot * dt;

        if fuel_used > mass_fuel
            fuel_used = mass_fuel;  % just use what's left, this prevents fuel going negative
        end

        mass_fuel = mass_fuel - fuel_used;
        mass_sc = mass_sc - fuel_used;

        fprintf('Fuel left: %.2f\n', mass_fuel);

        % Updates ΔV imparted to asteroid
        % DV_dt = F*(thrust*dt)/(M_A + ((thrust/(g*Isp))*dt)); 
        i_total = i_total + F * thrust * dt;
        % DV_step = (F * thrust * dt) / M_A;
        % DV_tot = DV_tot + DV_step;

    else

	    [~, RV] = ode45(@(t, y) propagate_WOT(t, y, mu), [0 dt], [rA0; vA0], options);

    end

    % Updates and Extracts all time steps
    N = size(RV,1);
    r_all = [r_all; RV(:,1:3)];
    v_all = [v_all; RV(:,4:6)]; 

    t_span = linspace(t_tot, t_tot + dt, N)';
    t_all = [t_all; t_span]; % interpolate time steps  + (0:N-1)' * (dt/(N-1))

    [a_step, e_step, e_vec] = orbit_elements(RV(:,1:3), RV(:,4:6), mu);
    a_all = [a_all; a_step];
    e_all = [e_all; e_step];
    
    
    % This updates the angle of the orbit
    r_vec = r_all(end, :)';
    e_vec = e_vec(end, :)';

    e_norm = e_vec/norm(e_vec);
    r_norm = r_vec/norm(r_vec);

    o_angle = acos((dot(e_norm,r_norm))); 
    
    o_angle = rad2deg(o_angle);

   
    % Updating State
	rA0 = RV(end,1:3)';
	vA0 = RV(end,4:6)';

    t_tot = t_tot + dt;

    
    % Debug terms

    if mass_fuel < 0
            break;
    end

    %step = step + 1;

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