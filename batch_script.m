
        
        clear all; close all; clc;
        
        restoredefaultpath;
        rehash toolboxcache;
        
        try
            rA0 = [-9.167812152058677E+07,2.000205103601552E+08,-4.091805994955202E+07];
            vA0 = [-1.736858965567808E+01,-1.858958976467830E+01,1.043592126645565E+00];
            thrust = 0.235;
            array_num = 3.0;
            sc_num = 2.0;
            dt = 3600.0;
            mass_fuel = 2203.0;
            mass_sc = 5867.0;
            Isp = 4178.0;
            M_A = 6410000000.0;
            R_A = 75.0;
            d = 1000.0;
            theta = 5.0;
            orbit_win = 90.0;
            infront = 1.0;
            
            disp('BATCH: Calling ODE_Handle_GUI with these inputs:');
            disp(rA0);
            disp(vA0);
            
            
            [t_all, r_all, v_all, delr, delT, Z_all, DV_tot, a_all, e_all] = ...
                ODE_Handle_GUI(rA0, vA0, thrust, array_num, sc_num, dt, mass_fuel, mass_sc, ...
                               Isp, M_A, R_A, d, theta, orbit_win, infront, true);
            
            save('batch_output.mat', 't_all','r_all','v_all','delr','delT','Z_all','DV_tot','a_all','e_all');
        
        catch ME
            disp('ERROR in MATLAB batch run:');
            disp(getReport(ME, 'extended'));
            save('batch_output.mat', 'ME');
        end
        