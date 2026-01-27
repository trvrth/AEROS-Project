function safePrint(msg, limiter)
% SAFEPRINT Prevents output flooding when using MATLAB Engine.
%   safePrint(msg, limiter) prints `msg` only once every `limiter` calls.
%   Call with limiter = 1 to always print.

    persistent counter
    if isempty(counter)
        counter = 0;
    end

    if nargin < 2 || isempty(limiter)
        limiter = 1;
    end

    counter = counter + 1;
    if counter >= limiter
        fprintf('%s\n', msg);
        counter = 0;
    end
end
