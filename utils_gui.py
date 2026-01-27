"""
utils_gui.py

Trevor Thomas

ENAE 380

Section: 0106

12/14/25

"""

import subprocess
import scipy.io
import numpy as np
import os
import traceback

def run_matlab_batch(
    rA0, vA0,
    thrust, array_num, sc_num, dt,
    mass_fuel, mass_sc, Isp,
    M_A, R_A, d, theta, orbit_win, infront
):
    """
    Generates a MATLAB batch script with the given parameters, runs it,
    and returns a dictionary of results loaded from batch_output.mat.
    """
    try:
        # Converts Python arrays to MATLAB syntax
        def fmt_array(arr):
            return "[" + ",".join(f"{x:.15E}" for x in arr) + "]"

        rA0_str = fmt_array(rA0)
        vA0_str = fmt_array(vA0)
        
        #check to see if format is correct
        print("rA0 ", rA0_str)
        print("vA0 ", vA0_str)
        
        #matlab script
        matlab_script = f"""
        
        clear all; close all; clc;
        
        restoredefaultpath;
        rehash toolboxcache;
        
        try
            rA0 = {rA0_str};
            vA0 = {vA0_str};
            thrust = {thrust};
            array_num = {array_num};
            sc_num = {sc_num};
            dt = {dt};
            mass_fuel = {mass_fuel};
            mass_sc = {mass_sc};
            Isp = {Isp};
            M_A = {M_A};
            R_A = {R_A};
            d = {d};
            theta = {theta};
            orbit_win = {orbit_win};
            infront = {infront};
            
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
        """

        # Write batch script
        with open("batch_script.m", "w") as f:
            f.write(matlab_script)

        # Run MATLAB in batch mode using subprocess with -batch flag
        script_dir = os.path.abspath('.')  # or the full project path
        result = subprocess.run(
        ["matlab", "-batch", f"cd('{script_dir}'); batch_script"],
        capture_output=True, text=True,
        cwd=script_dir
        )
        print(result.stdout)
        if result.stderr:
            print("MATLAB stderr:", result.stderr)

        # Check output
        if not os.path.exists("batch_output.mat"):
            raise FileNotFoundError("batch_output.mat not created by MATLAB.")

        data = scipy.io.loadmat("batch_output.mat") # loads data from .mat file

        if "ME" in data: #if error occurs display RuntimeError with what ME was (like exception)
            raise RuntimeError("MATLAB error occurred:\n" + str(data["ME"]))

        # Flatten arrays for Python
        t_all = data["t_all"].flatten()
        r_all = np.array(data["r_all"])
        v_all = np.array(data["v_all"])
        
        delr   = np.array(data["delr"]).flatten()
        delT   = np.array(data["delT"]).flatten()
        Z_all  = np.array(data["Z_all"]).flatten()
        DV_tot = np.array(data["DV_tot"]).flatten()
        
        a_all  = np.array(data["a_all"]).flatten()
        e_all  = np.array(data["e_all"]).flatten()
        
        # places it into return dictionary
        return dict(
            t_all=t_all,
            r_all=r_all,
            v_all=v_all,
            delr=delr,
            delT=delT,
            Z_all=Z_all,
            DV_tot=DV_tot,
            a_all=a_all,
            e_all=e_all
        )
    except Exception as e: # if error occurs print out error message
        print("Python exception running MATLAB batch:", e)
        traceback.print_exc() #prints full traceback of most recent exception
        return None

