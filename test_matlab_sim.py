import subprocess
import scipy.io
import numpy as np
import os
import traceback


def main():
    try:
        print("Preparing batch MATLAB script...")

        # ========================
        # 1. Write the MATLAB batch script
        # ========================
        matlab_script = r"""
        try
            disp('MATLAB batch script started.');

            M_A = 6410000000.0;
            R_A = 75.0;
            target_id = '2024 PDC25';
            start_date = '2032-07-05';
            stop_date  = '2032-07-06';
            step_size  = '1d';

            thrust = 0.235;
            array_num = 3.0;
            sc_num = 2.0;
            dt = 3600.0;
            mass_fuel = 2203.0;
            mass_sc = 5867.0;
            Isp = 4178.0;
            d = 1000.0;
            theta = 5.0;
            orbit_win = 180.0;
            infront = 1.0;

            % --------------- GET INITIAL STATE ---------------
            state_vec = get_horizons_rv(target_id, start_date, stop_date, step_size);
            rA0 = state_vec(1:3);
            vA0 = state_vec(4:6);

            % --------------- RUN ODE HANDLE ------------------
            [t_all, r_all, v_all, delr, delT, Z_all, DV_tot, a_all, e_all] = ...
                ODE_Handle_GUI( ...
                    rA0, vA0, thrust, array_num, sc_num, dt, mass_fuel, mass_sc, ...
                    Isp, M_A, R_A, d, theta, orbit_win, infront, true );

            save('batch_output.mat', ...
                    't_all', 'r_all', 'v_all', 'delr', ...
                    'delT', 'Z_all', 'DV_tot', 'a_all', 'e_all');

            disp('MATLAB batch completed successfully.');
        catch ME
            disp('ERROR in MATLAB batch run:');
            disp(getReport(ME, 'extended'));
            save('batch_output.mat', 'ME');
        end
        """

        with open("batch_script.m", "w") as f:
            f.write(matlab_script)

        print("Running MATLAB in batch mode...")

        # ========================
        # 2. Run MATLAB in batch using subprocess
        # ========================
        result = subprocess.run(
            ["matlab", "-batch", "batch_script"],
            text=True,
            capture_output=True
        )

        print("MATLAB output:")
        print(result.stdout)
        print("MATLAB errors:")
        print(result.stderr)

        # ========================
        # 3. Load results saved to batch_output.mat
        # ========================
        if not os.path.exists("batch_output.mat"):
            print("❌ No output file produced.")
            return

        data = scipy.io.loadmat("batch_output.mat")

        if "ME" in data:
            print("\n❌ MATLAB reported an exception:")
            print(data["ME"])
            return
        
        z = data["Z_all"]
        a = data["a_all"]
        t_all = data["t_all"].flatten()
        delT = data["delT"]
        DV = data["DV_tot"]

        print("\n✅ Batch simulation completed.")
        print("Change in semi-major axis: ", (a[-1] - a[1]))
        print("Total Deflection (zeta): ", z[-1])
        print("Total Delta V Imparted: ", DV[-1] * 1000000, "mm/s")
        print("Total Change in Period (delta T): ", delT[-1], "s")
        print("Total Time: ", t_all[-1]/86400, "days")
        print("Total Time: ", t_all[-1]/86400/365.5, "years")

    except Exception as e:
        print("\n❌ Python exception:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
