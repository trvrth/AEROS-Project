function state_vec = get_horizons_rv(target_id, stop_date, step_size)
% GET_HORIZONS_RV Queries JPL Horizons and returns the final [x y z vx vy vz] vector.
%
% Inputs:
%   target_id  - e.g., '499' or '2024 PDC'
%   start_date - string, e.g., '2032-Jul-06'
%   stop_date  - string, e.g., '2032-Jul-07'
%   step_size  - e.g., '1 d'
%
% Output:
%   state_vec  - 1x6 vector: [x y z vx vy vz] in [km, km/s]

start_date = stop_date - days(1);
stop_date = datestr(stop_date, 'yyyy-mm-ddTHH:MM:SS');
start_date = datestr(start_date, 'yyyy-mm-ddTHH:MM:SS');

    if isnan(str2double(target_id))
        target_id = ['"', target_id, '"'];  % Add quotes if it's a name
    end

    base_url = 'https://ssd.jpl.nasa.gov/api/horizons.api?';

    query = [
        "format=text", ...
        "COMMAND=" + target_id, ...
        "MAKE_EPHEM=YES"...
        "EPHEM_TYPE=VECTORS", ...
        "CENTER='500@0'", ...
        "START_TIME=" + start_date, ...
        "STOP_TIME=" + stop_date, ...
        "STEP_SIZE=" + step_size, ...
        "REF_PLANE=ECLIPTIC", ...
        "REF_SYSTEM=J2000", ...
        "VEC_TABLE=3", ... % could make this 2 but need to change logic below
        "OUT_UNITS=KM-S", ...
        "VEC_CORR=NONE" ...
    ];

    full_url = base_url + join(query, '&');
    opts = weboptions('Timeout', 60);
    raw = webread(full_url, opts);

    % Split into lines and isolate $$SOE ... $$EOE block
    lines = splitlines(raw);
    i1 = find(contains(lines, '$$SOE'), 1) + 1;
    i2 = find(contains(lines, '$$EOE'), 1) - 1;
    data_lines = lines(i1:i2);

    % We want the last complete state vector in the block
    % Each vector spans 4 lines:
    % Line 1: Julian + date
    % Line 2: X Y Z
    % Line 3: VX VY VZ
    % Line 4: LT, RG, RR (skip)
    for i = numel(data_lines)-2:-4:1
        line_pos = strtrim(data_lines{i});
        line_vel = strtrim(data_lines{i+1});

        % Parse position
        x = sscanf(line_pos, ' X =%f Y =%f Z =%f');
        v = sscanf(line_vel, ' VX=%f VY=%f VZ=%f');

        if numel(x) == 3 && numel(v) == 3
            state_vec = [x; v];
            return;
        end
    end

    error('No valid state vector found in Horizons output.');
end