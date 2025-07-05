clc;
clear;
close all;

%Inputs to program
sim_menu()
global SC_POS

M_A = 6.41e9; % 528 billion kilograms 
g = 0.00980665; % km/s^2
mu = 1.32712E+11; % km^3/s^2
mass_sc = 8863; % total mass of the space craft (including fuel)
mass_fuel_sc = 5199; % mass of xenon on space craft
input_power = 7.78; % in KW, power required for each thruster
Isp = 4178; % seconds (Max Throttle of Next-C)
Thrust = 235e-3; % Newtons of Force (Thrust)
dt = 36000; % step size
Array_Num = 3; % number of thrusters firing towards the asteroid. 
Num_SC = 2; %number of identical space craft.
Orbit_Window = 180; % window of orbit for thrusters to turn on, in degrees. 

tol = 1e-12; % acceptable tolerance
options = odeset('RelTol', tol, 'AbsTol', tol); % ODE45 options

Asteroid_Radius = 278.87; % 780 meter diameter 
Standoff_Distance = 1000; % pretty close from asteroid surface
Ion_Beam_Divergence_Angle = 5; % In degrees

% Initial Conditions (km)
EarthIC = [6.82500E+07; 1.30864E+08; 1.81329E+04; -2.67639E+01; 1.38981E+01; -9.22794E-04];
AsteroidIC = [-9.017346132883599E+07;  2.016178218722010E+08; -4.100642351379222E+07; -1.746107974315678E+01; -1.838532402937617E+01;  1.001923496246683E+00]; 

% Infront Logic
if SC_POS
    Infront = 1; % behind is true
else
    Infront = -1; % infront is false
end

% Allocating IC and Parameters
rA0 = AsteroidIC(1:3, 1);
vA0 = AsteroidIC(4:6, 1);

params = {Thrust, Array_Num, Num_SC, dt, ...
    mass_fuel_sc, mass_sc, Isp, M_A, Asteroid_Radius, Standoff_Distance, ... 
    Ion_Beam_Divergence_Angle, Orbit_Window, Infront};

% Call ODE_Handle
[t, r, v, Delta_R, Delta_T, DV_total, a, e] = ODE_Handle(rA0, vA0, params{:});

% Combines r and v into RV so it can be easily plotted in 3D.
RV = [r v];

% Takes last entrie in r and v to find the final positon and velocity to use as intial conditions to map the final orbit after thrusting.
r_final = r(end,:)';
v_final = v(end,:)';

RV_finalIC = [r_final, v_final];

% ODE45 Propagation of Earth and Asteroid with no force, then the ODE_Handle of Didymos with Ion Force. 
[Earth_t, Earth_RV] = ode45(@(t, y) propagate(t, y, mu), 0:dt:7e7, EarthIC, options);
[Asteroid_t, Asteroid_RV] = ode45(@(t, y) propagate(t, y, mu), 0:dt:7e7, AsteroidIC, options);
[~, final_RV] = ode45(@(t, y) propagate(t, y, mu), 0:dt:7e7, RV_finalIC, options);

% Plotting the 3D view of the orbits (the orbits are very close to one another)

figure;
hold on;
view(3)
axis equal;
xlabel('X'); ylabel('Y'); zlabel('Z');
title('Asteroid Trajectory');

plot3(0, 0, 0, 'yo', 'MarkerSize', 10, 'MarkerFaceColor', 'y', 'DisplayName', 'Sun');

plot3(Earth_RV(:,1), Earth_RV(:,2), Earth_RV(:,3), 'b','DisplayName', 'Earth'); 
plot3(Asteroid_RV(:,1), Asteroid_RV(:,2), Asteroid_RV(:,3), 'r', 'DisplayName', 'Asteroid (No Thrust)', lineWidth=0.1);
plot3(final_RV(:,1), final_RV(:,2), final_RV(:,3), 'g', 'DisplayName', 'Asteroid (With Thrust)', lineWidth=0.1);

legend show;

% Plotting the Displacement, Semi Major Axis, and Eccentricity Change over time due to Ion Beam

% Can add back in once floating point error is resolved in time step displacement calculations
% figure;
% subplot(3,1,1);
% plot(Delta_R(:,1) / 86400, Delta_R(:,2));
% xlabel('Time [days]');
% ylabel('Displacement [km]');
% title('Deflection Displacement over time');
figure;

subplot(2,1,1);
plot(t / 86400, a);
xlabel('Time [days]');
ylabel('Semi-major Axis [km]');
title('Orbital Change Due to Ion Beam');

subplot(2,1,2);
plot(t / 86400, e);
xlabel('Time [days]');
ylabel('Eccentricity');
title('Eccentricity over time');

% Output Semi Major Axis, total ΔV, and operating time
delta_a_m = (a(end) - a(1));
fprintf('Change in semi-major axis: %.3f km\n', delta_a_m);
fprintf('Total Position Difference Distance at the end of Sim: %.3f km\n', Delta_R);
fprintf('Total ΔV imparted: %.3f mm/s\n', DV_total*1e6);
fprintf('Total Change in Period (ΔT): %.3f s\n', Delta_T);
fprintf('Operation time: %.2f days\n', t(end) / 86400);
