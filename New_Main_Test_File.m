
M_A = 528e9; % 528 billion kilograms 
g = 0.00980665; % km/s^2
mu = 1.32712E+11; % km^3/s^2
mass_sc = 5000; % total mass of the space craft (including fuel)
mass_fuel_sc = 2500; % mass of xenon on space craft
Isp = 4170; % seconds (Max Throttle of Next-C)
Thrust = 237e-3; % Newtons of Force (Thrust)
dt = 36000; % step size
t_op = 365.5*24*60*60; % total amount of seconds in a year of operation

tol = 1e-12; % acceptable tolerance
options = odeset('RelTol', tol, 'AbsTol', tol); % ODE45 options

Asteroid_Radius = 390; % 780 meter diameter 
Standoff_Distance = 10; % pretty close from asteroid surface
Ion_Beam_Divergence_Angle = 22; % In degrees

EarthIC = [6.82500E+07; 1.30864E+08; 1.81329E+04; -2.67639E+01; 1.38981E+01; -9.22794E-04];
DidymosIC = [-2.39573E+08; -2.35661E+08;  9.54384E+06; 1.24732E+01; -9.74427E+00; -8.78661E-01]; % Initial Conditions

% ssize = t_op/dt;

F = IBFraction(Asteroid_Radius, Standoff_Distance, Ion_Beam_Divergence_Angle);

% for i = 1:ssize
%     DV_step = F*(Thrust*dt)/(M_A + ((Thrust/(g*Isp))*dt));
%     DV_total = DV_total + DV_step;
% end

[Earth_t, Earth_RV] = ode45(@(t, y) propagate_2BP(t, y, mu, 0, M_A, F), 0:dt:7e7, EarthIC, options);
[Didymos_t, Didymos_RV] = ode45(@(t, y) propagate_2BP(t, y, mu, 0, M_A, F), 0:dt:7e7, DidymosIC, options);
[t, r, v, DV_total] = ODE_Handle(DidymosIC(1:3), DidymosIC(4:6), Thrust, dt, mass_fuel_sc, mass_sc, Isp, M_A, Asteroid_Radius, Standoff_Distance, Ion_Beam_Divergence_Angle);


RV = [r v];

figure;
hold on;
axis equal;
xlabel('X'); ylabel('Y'); zlabel('Z');
title('Didymos Trajectory');

plot3(RV(:,1), RV(:,2), RV(:,3), 'r--');
% plot3(Earth_RV(:,1), Earth_RV(:,2), Earth_RV(:,3), 'b'); 
% plot3(Didymos_RV(:,1), Didymos_RV(:,2), Didymos_RV(:,3), 'r');


% Output total ΔV and operating time
fprintf('Total ΔV imparted: %.6e km/s\n', DV_total);
fprintf('Operation time: %.2f days\n', t(end) / 86400);

