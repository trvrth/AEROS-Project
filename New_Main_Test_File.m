
Thrust = 1e-7;
M_A = 528e9; % 528 billion kilograms 
g = 9.80665; % m/s^2
Isp = 4170; % seconds (Max Throttle of Next-C)
T = 237e-3; % Newtons of Force (Thrust)
dt = 10000; % step size
t_op = 365.5*24*60*60; % total amount of seconds in a year of operation
ssize = t_op/dt;
DV_total = 0;

DidymosIC = [-2.39573E+08; -2.35661E+08;  9.54384E+06; 1.24732E+01; -9.74427E+00; -8.78661E-01];

Asteroid_Radius = 390; % 780 meter diameter 
Standoff_Distance = 10; % pretty close from asteroid surface
Ion_Beam_Divergence_Angle = 20; % In degrees

F = IBFraction(Asteroid_Radius, Standoff_Distance, Ion_Beam_Divergence_Angle);

for i = 1:ssize
    DV_step = F*(T*dt)/(M_A + ((T/(g*Isp))*dt));
    DV_total = DV_total + DV_step;
end

t_total = ODE_Handle(DidymosIC(1:3), DidymosIC(4:6), DV_total, T, dt, ssize);

t_days = t_total/(60*60*24);

t_days

