function sim_menu()
    clc;

    global THRUST_ON SIM_MODE SIM_TIME SC_POS

    % Asks if thrust is active
    thrust_choice = menu('Is there thrust on the asteroid?', 'Yes', 'No');

    if thrust_choice == 1
        THRUST_ON = true;
        % Thrust is ON: Ask how to run simulation
        sim_choice = menu('Choose simulation condition:','Run until fuel runs out', 'Run for a specified time');

        SIM_MODE = sim_choice;
            
            
        if sim_choice == 2
           
            answer = inputdlg('Enter total simulation time (seconds):', 'Simulation Duration', [1 35], {'1000'});
            
            if isempty(answer)
                disp('Simulation cancelled');
                return;
            end
            
            SIM_TIME = str2double(answer{1});

            if isnan(SIM_TIME) || SIM_TIME <= 0
                error('Invalid simulation time');
            end
            
            disp(['Running simulation with thrust for ', num2str(SIM_TIME), ' seconds...']);
            
        end

        ans_infront = menu("Where is the Spacecraft Relative to the Asteroid's motion:", 'In Front (ahead)', 'Behind (trailing)');
        SC_POS = (ans_infront == 2);  % true if behind

    elseif thrust_choice == 2

        THRUST_ON = false;
        disp('Running simulation without thrust...');

        ans_infront = menu("Where is the Spacecraft Relative to the Asteroid's motion:", 'In Front (ahead)', 'Behind (trailing)');
        SC_POS = (ans_infront == 2);  % true if behind
        SIM_MODE = 2;
            
            
        if SIM_MODE == 2
           
            answer = inputdlg('Enter total simulation time (seconds):', 'Simulation Duration', [1 35], {'3.156e+7'});
            
            if isempty(answer)
                disp('Simulation cancelled');
                return;
            end
            
            SIM_TIME = str2double(answer{1});

            if isnan(SIM_TIME) || SIM_TIME <= 0
                error('Invalid simulation time');
            end
            
            disp(['Running simulation with thrust for ', num2str(SIM_TIME), ' seconds...']);
            
        end

    else
        disp('No selection made. Simulation cancelled.');
    end
end