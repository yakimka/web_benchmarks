--https://github.com/wg/wrk/blob/master/SCRIPTING
framework = os.getenv("NAME")
filename = string.format("results/%s.txt", framework)
start_time = os.date("!%Y-%m-%dT%H:%M:%S")

done = function(summary, latency, requests)
    --  The done() function receives a table containing result data, and two
    --  statistics objects representing the per-request latency and per-thread
    --  request rate. Duration and latency are microsecond values and rate is
    --  measured in requests per second.
    local file = assert(io.open(filename, "a"))
    local end_time = os.date("!%Y-%m-%dT%H:%M:%S")

    file:write("start_time: ", start_time, "\n")
    file:write("path: ", wrk.path, "\n")
    file:write("framework: ", framework, "\n")
    file:write("latency_min: ", latency.min, "\n")
    file:write("latency_max: ", latency.max, "\n")
    file:write("latency_mean: ", latency.mean, "\n")
    file:write("latency_stdev: ", latency.stdev, "\n")
    file:write("latency_percentile_90: ", latency:percentile(90), "\n")
    file:write("latency_percentile_99: ", latency:percentile(99), "\n")
    file:write("duration: ", summary.duration, "\n")
    file:write("requests_num: ", summary.requests, "\n")
    file:write("bytes_received: ", summary.bytes, "\n")
    file:write("errors_status: ", summary.errors.status, "\n")
    file:write("errors_connect: ", summary.errors.connect, "\n")
    file:write("errors_read: ", summary.errors.read, "\n")
    file:write("errors_write: ", summary.errors.write, "\n")
    file:write("errors_timeout: ", summary.errors.timeout, "\n")
    file:write("end_time: ", end_time, "\n\n")

    file:close()
end
