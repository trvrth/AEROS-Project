
M_A = 528e9; % 528 billion kilograms 
g = 0.00980665; % km/s^2
mu = 1.32712E+11; % km^3/s^2
mass_sc = 5000; % total mass of the space craft (including fuel)
mass_fuel_sc = 2500; % mass of xenon on space craft
Isp = 4170; % seconds (Max Throttle of Next-C)
Thrust = 237e-3; % Newtons of Force (Thrust)
dt = 36000; % step size
Array_Num = 6; % number of thrusters firing towards the asteroid. 

tol = 1e-12; % acceptable tolerance
options = odeset('RelTol', tol, 'AbsTol', tol); % ODE45 options

Asteroid_Radius = 390; % 780 meter diameter 
Standoff_Distance = 10; % pretty close from asteroid surface
Ion_Beam_Divergence_Angle = 22; % In degrees

EarthIC = [6.82500E+07; 1.30864E+08; 1.81329E+04; -2.67639E+01; 1.38981E+01; -9.22794E-04];
DidymosIC = [-2.39573E+08; -2.35661E+08;  9.54384E+06; 1.24732E+01; -9.74427E+00; -8.78661E-01]; % Initial Conditions

F = IBFraction(Asteroid_Radius, Standoff_Distance, Ion_Beam_Divergence_Angle);

% ODE45 Propagation of Earth and Didymos with no force, then the ODE_Handle
% of Didymos with Ion Force. 
[Earth_t, Earth_RV] = ode45(@(t, y) propagate_WOT(t, y, mu), 0:dt:7e7, EarthIC, options);
[Didymos_t, Didymos_RV] = ode45(@(t, y) propagate_WOT(t, y, mu), 0:dt:7e7, DidymosIC, options);
[t, r, v, DV_total, a, e] = ODE_Handle(DidymosIC(1:3), DidymosIC(4:6), Thrust, Array_Num, dt, mass_fuel_sc, mass_sc, Isp, M_A, Asteroid_Radius, Standoff_Distance, Ion_Beam_Divergence_Angle);

% Combines r and v into RV so it can be easily plotted in 3D.
RV = [r v];

% Plotting the 3D view of the orbits (the orbits are very close to one another)

figure;
hold on;
view(3)
axis equal;
xlabel('X'); ylabel('Y'); zlabel('Z');
title('Didymos Trajectory');

plot3(Earth_RV(:,1), Earth_RV(:,2), Earth_RV(:,3), 'b'); 
plot3(Didymos_RV(:,1), Didymos_RV(:,2), Didymos_RV(:,3), 'r');
plot3(RV(:,1), RV(:,2), RV(:,3), 'g');
legend('Earth', 'Without Thrust', 'With Thrust');

% Plotting the Semi Major Axis and Eccentricity Change over time due to Ion
% Beam

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

% Output total ΔV and operating time
delta_a_m = (a(end) - a(1)) * 1e3;
fprintf('Change in semi-major axis: %.3f meters\n', delta_a_m);
fprintf('Total ΔV imparted: %.6e km/s\n', DV_total);
fprintf('Operation time: %.2f days\n', t(end) / 86400);

