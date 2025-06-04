% Variables:
mu = 1.32712E+11; % (km^3)/(s^2), this is the G*(m)
thrust_mag = 1e-7;
ssize = 10000; % step size in seconds
tol = 1e-12; % acceptable tolerance
options = odeset('RelTol', tol, 'AbsTol', tol); % ODE45 options

%% Part 1: Plotting Orbits

% Table Values (Intial Conditions): [x y z vx vy vz]

EarthIC = [6.82500E+07; 1.30864E+08; 1.81329E+04; -2.67639E+01; 1.38981E+01; -9.22794E-04];

DidymosIC = [-2.39573E+08; -2.35661E+08;  9.54384E+06; 1.24732E+01; -9.74427E+00; -8.78661E-01];

%DARTIC = [6.82409E+07; 1.30854E+08; 1.52197E+04; -3.06997E+01; 8.11796E+00; 3.95772E+00];
DARTIC = DidymosIC;

% Time Range
Earth_t = 0:ssize:7e7;
Didymos_t = 0:ssize:7e7;
DART_t = 0:ssize:2.6e7;

%created function script called propagate_2BP.m, is basic function that
%splits the table values into two useable variables, r and v. Then
%calculates the acceleration through the formula at the bottom of lecture
%2, a = -mu/r^3 * rv, rv(being the r vector)
[Earth_t,Earth_RV] = ode45(@propagate_2BP, Earth_t, EarthIC, options, mu, 0);
[Didymos_t, Didymos_RV] = ode45(@propagate_2BP, Didymos_t, DidymosIC, options, mu, 0);
[Didymos_t_aft, Didymos_RV_aft] = ode45(@propagate_2BP, Didymos_t, DidymosIC, options, mu, thrust_mag);
%[DART_t, DART_RV] = ode45(@propagate_2BP, DART_t, DARTIC, options, mu, 0);

% Plotting Orbits
figure; % can add color to each plotted line, using 'b', 'r', 'g', etc.
plot3(Earth_RV(:,1), Earth_RV(:,2), Earth_RV(:,3), 'b'); 
hold on;
plot3(Didymos_RV(:,1), Didymos_RV(:,2), Didymos_RV(:,3), 'r');
hold on;
%plot3(DART_RV(:,1), DART_RV(:,2), DART_RV(:,3), 'g');
%hold on;

% Plot Labels

title('Earth and Didymos Orbits');
legend('Earth', 'Didymos');
xlabel('X (km)');
ylabel('Y (km)');
zlabel('Z (km)');
axis equal;
grid on;
hold off;

%% Part 2: Didymos Magnitude Vector Plot Before and After Force

% Have to use, : , for rows b/c there is 7001 entries for each column.
Dd_p_mag = vecnorm(Didymos_RV(:,1:3), 2, 2); % 1:3 is x y z
Dd_v_mag = vecnorm(Didymos_RV(:,4:6), 2, 2); % 4:6 is vx vy vz
Dd_a_mag = zeros(size(Didymos_t));
for i = 1:length(Didymos_t) % many rows so have to do for loop to get to each
    r = Didymos_RV(i, 1:3);
    r_norm = norm(r);
    Dd_a = -mu/(r_norm^3) * r; % this is to find acceleration of Didymos
    Dd_a_mag(i) = norm(Dd_a); % normalizes acceleration for each index
end

Dd_p_mag_aft = vecnorm(Didymos_RV_aft(:,1:3), 2, 2); % 1:3 is x y z
Dd_v_mag_aft = vecnorm(Didymos_RV_aft(:,4:6), 2, 2); % 4:6 is vx vy vz
Dd_a_mag_aft = zeros(size(Didymos_t_aft));
for i = 1:length(Didymos_t_aft) % many rows so have to do for loop to get to each
    r = Didymos_RV_aft(i, 1:3);
    r_norm = norm(r);
    Dd_a = -mu/(r_norm^3) * r; % this is to find acceleration of Didymos
    Dd_a_mag_aft(i) = norm(Dd_a); % normalizes acceleration for each index
end

figure;
% subplot makes a grid of plots based off that first number in it, and the
% last number is the position of each respective subplot.
subplot(3,2,1);
plot(Didymos_t, Dd_p_mag);
ylabel ('||r|| (km)');
title('Didymos Magnitude Plots Before')
grid on;

subplot(3,2,3);
plot(Didymos_t, Dd_v_mag);
ylabel('||v|| (km/s)');
grid on;

subplot(3,2,5);
plot(Didymos_t, Dd_a_mag);
xlabel('Time (days)');
ylabel('||a|| (km/s^2)');
grid on;

subplot(3,2,2);
plot(Didymos_t_aft, Dd_p_mag_aft);
ylabel ('||r|| (km)');
title('Didymos Magnitude Plots After')
grid on;

subplot(3,2,4);
plot(Didymos_t_aft, Dd_v_mag_aft);
ylabel('||v|| (km/s)');
grid on;

subplot(3,2,6);
plot(Didymos_t_aft, Dd_a_mag_aft);
xlabel('Time (days)');
ylabel('||a|| (km/s^2)');
grid on;

%% Part 3: Final State of Didymos after 70,000 seconds
format short
Didymos_final_position = Didymos_RV(end, 1:3)
Didymos_final_velocity = Didymos_RV(end, 4:6)

%% Didymos Before and After Being Acted on By Force
figure;
plot3(Didymos_RV(:,1), Didymos_RV(:,2), Didymos_RV(:,3), 'r');
hold on;
plot3(Didymos_RV_aft(:,1), Didymos_RV_aft(:,2), Didymos_RV_aft(:,3), 'r--');
hold on;
plot3(Earth_RV(:,1), Earth_RV(:,2), Earth_RV(:,3), 'b'); 
hold on;
legend('Without Force', 'With Force', 'Earth');
xlabel('X (km)');
ylabel('Y (km)');
zlabel('Z (km)');
axis equal;
title('Didymos Orbit With and Without Continuous Force Acted Upon It');
grid on;