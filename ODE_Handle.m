function out = ODE_Handle(rA0, vA0, DV, thrust, t_final)

mu = 1.32712E+11;
tol = 1e-12; % acceptable tolerance
options = odeset('RelTol', tol, 'AbsTol', tol); % ODE45 options

dt = 10000; % step size in seconds
t_tot = 0;

for i = 1:t_final

	[~ , RV] = ode45(@propagate_2BP, [0 dt], [rA0; vA0], options, mu, thrust);
	r_Af = RV(1:3);
    v_Af = RV(4:6);
	r_A0 = r_Af;
	v_A0 = v_Af + DV;
	t_tot = t_tot + dt;

end

out = (t_tot);

return