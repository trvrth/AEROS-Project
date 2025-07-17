function [t_all, r_all, v_all, delr, delT, Z_all, DV_tot, a_all, e_all] = ODE_Handle(rA0, vA0, thrust, array_num, sc_num, dt, mass_fuel, mass_sc, Isp, M_A, R_A, d, theta, orbit_window, infront)

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
% infront is a sign variable to indicate whether the spacecraft is infront of or behind the asteroid's motion, changes sign accordingly within propagate functions

global THRUST_ON SIM_MODE SIM_TIME

mu = 1.32712E+11; % km^3/s^2
tol = 1e-12; % acceptable tolerance
options = odeset('RelTol', tol, 'AbsTol', tol); % ODE45 options
g = 0.00980665; % km/s^2

thrust = thrust*array_num/1000; % to convert to kg*km/s^2 (kN) and account for how many thrusters used per space craft

total_thrust = thrust*sc_num; % account for number of space craft

mdot = thrust*2 / (g * Isp); % mass flow rate of the ion thruster per space craft

% B-Plane Deflection Set up
D_time = 277689600; %time until it hits earth from arrival date 7/6/2032 -> 275721360, 

V_A = [2.177274164114799E+01; -3.143978057903817E+01;  1.173156213677415E+01]; % IC for earth at impact date km/s
V_E = [1.628743818010616E+01; -2.473486106579037E+01;  2.142590131803956E-03]; % IC for asteroid at impact date km/s
V_inf = V_A - V_E;
x_hat = cross(V_E, V_inf)/norm(cross(V_E, V_inf));
y_hat = V_inf/norm(V_inf);
z_hat = cross(x_hat, y_hat)/norm(cross(x_hat, y_hat));
T_HCI_B = [x_hat'; y_hat'; z_hat'];
V_E_B = T_HCI_B * V_E;
V_E_B_xz = sqrt((V_E_B(1,1)^2) + (V_E_B(3,1)^2));

% Changes the Mode of Simulation
end_condition_num = 0;
if SIM_MODE == 2
    end_condition_num = SIM_TIME;  % simulate for a specific time
else
    disp("SIM_MODE is until fuel runs out!");
end

% Ion Beam coupling efficiency
% F = IBFraction(R_A, d, theta); commented out for now to verify
F = .95;
fprintf("Beam coupling fraction F = %.3f\n", F);

chunkSize = 10000;
step = 1;
r_all = zeros(chunkSize, 3);
v_all = zeros(chunkSize, 3);
t_all = zeros(chunkSize, 1);
a_all = zeros(chunkSize, 1);
e_all = zeros(chunkSize, 1);
delT = zeros(chunkSize, 1);
Z_all = zeros(chunkSize, 1);

%Calculate starting o_angle
[a0_scalar, e0_scalar, e0_vec] = orbit_elements(rA0, vA0, mu);

e_unit = e0_vec/norm(e0_vec);
r_unit = rA0/norm(rA0);

o_angle = acos((dot(e_unit,r_unit)));   
o_angle = rad2deg(o_angle);


% Set up for Displacement Calculations
T = 2 * pi * sqrt(a0_scalar^3/mu); % period of undeflected orbit

% Intialization
t_tot = 0;
total_thrust_time = 0;
i_total = 0;
r_nom = rA0;
v_nom = vA0;
first_loop = true;
coasting_started = false;
thrust_again = false;
t_thrust_end = 0;
Z_accumulated = 0;
Z_offset = 0;
Z_diff = 0;
grav = 1;
angle_window = orbit_window;

fprintf('[t = %6d s] mass_sc = %.2f kg, a_thrust = %.2e km/s^2\n', t_tot, mass_sc, total_thrust / mass_sc);
% Condition Variable
SIM_ON = true;

% --- Start of the Propagation simulation ---
while SIM_ON

    % fprintf('Time: %.2f days | Fuel left: %.2f kg | Z = %.2f km\n', t_tot/86400, mass_fuel, Z_total);
    fprintf('Angle to perihelion: %.2f°\n', o_angle);

    if o_angle > angle_window
        if ~coasting_started
            coasting_started = true;
            grav = 0;
            t_thrust_end = t_tot;
            fprintf('Coasting started at t = %.2f s\n', t_thrust_end);
        end
    else
        coasting_started = false;
        grav = 1;
    end      
   
    % Checks angle and applies thrust only at the angle provided
    if THRUST_ON && o_angle <= angle_window

        [~, RV] = ode45(@(t, y) propagate_WT(t, y, mu, total_thrust, M_A, F, mass_sc*sc_num, d, grav*infront), [0 dt], [rA0; vA0], options);
        fprintf('thrust applied!');
       

        % Updating Mass of the Space Craft and the Fuel
        fuel_used = mdot * dt;

        if fuel_used > mass_fuel
            dt_actual = mass_fuel / mdot;
        else
            dt_actual = dt;
        end

        % updates mass of singular spacecraft
        fuel_used = mdot * dt_actual;
        mass_fuel = mass_fuel - fuel_used;
        mass_sc = mass_sc - fuel_used; 
        
        if mass_fuel <= 0
            fprintf('Fuel exhausted\n');
            THRUST_ON = false;  % disables thrust globally
        end

        fprintf('Fuel left: %.2f\n', mass_fuel);

        total_thrust_time = total_thrust_time + dt_actual;

        % Updates ΔV imparted to asteroid
        i_total = i_total + F * total_thrust * dt_actual;

    else

	    [~, RV] = ode45(@(t, y) propagate_WOT(t, y, mu, mass_sc*sc_num, d, grav*infront), [0 dt], [rA0; vA0], options);
        dt_actual = dt;
    end

    % Updating State
	rA0 = RV(end,1:3)';
	vA0 = RV(end,4:6)';

    t_tot = t_tot + dt_actual; % might need to come back to this for orbit window

    if step > size(r_all, 1)
        r_all(end+1:end+chunkSize, :) = 0;
        v_all(end+1:end+chunkSize, :) = 0;
        t_all(end+1:end+chunkSize, 1) = 0;
        a_all(end+1:end+chunkSize, 1) = 0;
        e_all(end+1:end+chunkSize, 1) = 0;
        delT(end+1:end+chunkSize, 1) = 0;
        Z_all(end+1:end+chunkSize, 1) = 0;
    end

    % Updates and Extract time step for thrusted/simulation propagation
    r_all(step,:) = RV(end,1:3);
    v_all(step,:) = RV(end,4:6); 

    t_all(step,:) =  t_tot; % time steps

    [a_step, e_step, e_vec] = orbit_elements(rA0, vA0, mu);
    a_all(step,:) = a_step;
    e_all(step,:) = e_step;
    
    % This updates the angle of the orbit
    r_vec = r_all(step, :)';
    e_unit = e_vec/norm(e_vec);
    r_unit = r_vec/norm(r_vec);
    o_angle = acosd((dot(e_unit,r_unit))); 
    
    % Nominal Propagation
    [~, RV_nom] = ode45(@ (t,y) propagate(t, y, mu), [0 dt], [r_nom; v_nom], options);
    
    r_nom_all(step, :) =  RV_nom(end, 1:3);
    v_nom_all(step, :) =  RV_nom(end, 4:6);
    r_nom = RV_nom(end,1:3)';
    v_nom =  RV_nom(end, 4:6)';


    % Updates Displacement of asteroid from original positions
    b = real(a0_scalar * sqrt(1 - e0_scalar^2)); % semi-minor axis
    x = (a0_scalar^2 - b^2);
    C = real(pi * (a0_scalar + b) * (1 + (3*x^2)/(10 + sqrt(4-(3*x^2))))); % circumference of undeflected orbit

    af_step = a_step;
    dela_step = af_step - a0_scalar;
    delr_step = 1.5 * C * (dela_step/a0_scalar) * (1/T);


       % B-Plane Deflection
    if coasting_started
        % Time since thrust ended (elapsed coasting time)
        t_since_thrust = t_tot - t_thrust_end;
        Delta_T_total = (2 * pi * sqrt(af_step^3 / mu)) - T;
        delT(step,:) = Delta_T_total;
        fprintf("Delta T: %.3e s\n", delT(step));

        Z_total_coast = Delta_T_total * (t_since_thrust / T) * V_E_B_xz;

        Z_all(step) = Z_accumulated + Z_total_coast;
    
        fprintf('Coasting deflection at t=%.2f s: %.3f km\n', t_tot, Z_all(step));
        Z_offset = Z_all(step);
        thrust_again = true;
    else
        Delta_T_total = (2 * pi * sqrt(af_step^3/mu)) - T;
        delT(step,:) = Delta_T_total;
        fprintf("Delta T: %.3e s\n", delT(step));
        
        D_remaining = max(D_time - t_tot, 0);
        Z_total = Delta_T_total*(D_remaining/T)*V_E_B_xz;
        if thrust_again
            Z_diff = Z_offset - Z_total;
            thrust_again = false;
        end
        Z_all(step) = Z_total + Z_diff;
        Z_accumulated = Z_all(step,:);
        fprintf('B-Plane Deflection: %.3f km\n', Z_all(step));
    end
    
    % Updating Step
    step = step + 1;
   
    % Sim runs until fuel runs out
    if SIM_MODE == 1
        if (mass_fuel <= 0)
            SIM_ON = false;
        end
    end

    % Sim runs until time runs out
    if SIM_MODE == 2
 
        if t_tot > end_condition_num
            disp("sim ending b/c of time constraint")
            SIM_ON = false;
        end

    end
    
    % if Z_all(end) >= 7370
    %     disp("sim ending b/c deflection reached")
    %     fprintf('B-Plane Deflection: %.3f km\n', Z_all(end));
    %     break
    % end

    % if t_tot >= 60048000  % For Low it is 65318400, For 50th it is 60048000,For Heavy its 86313600
    %     disp("sim ending b/c the world has ended")
    %     break
    % end

    if first_loop
    fprintf('Initial a_thrust: %.3e km/s²\n', total_thrust / (mass_sc*sc_num));
    fprintf('Initial mdot: %.3e kg/s\n', mdot);
    fprintf('Initial fuel: %.2f kg\n', mass_fuel);
    fprintf('Initial mass_sc: %.2f kg\n', mass_sc);
    first_loop = false;
    end

end

% Array Truncation
r_all = r_all(1:step-1, :);
v_all = v_all(1:step-1, :);
t_all = t_all(1:step-1, 1);
a_all = a_all(1:step-1, 1);
e_all = e_all(1:step-1, 1);
delT  = delT(1:step-1, 1);
Z_all = Z_all(1:step-1, 1);

% Finds Displacement of asteroid, over time
delr = delr_step * t_all(end,1);

% Find total ΔV imparted on asteroid
DV_tot = i_total / (M_A);


% D_remaining = D_time-t_tot;
% Z_total = Delta_T*(D_remaining/T)*V_E_B_xz
D_remaining = max(D_time - t_tot, 0);
Z_total = delT(end)*(D_remaining/T)*V_E_B_xz;
fprintf('B-Plane Deflection Coasting END: %.3f km\n', Z_total);


% % Verification calculation of max ideal delta V (Print Out)
fprintf("I_total: %.3f \n", i_total);
fprintf("Total Thrust Time (days): %.3f \n",  total_thrust_time/86400);
return