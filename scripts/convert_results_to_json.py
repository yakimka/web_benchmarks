import argparse
import json
import os
from collections import defaultdict
from typing import TypedDict


class LatencyDistribution(TypedDict):
    percentage: int
    latency: float


class WrkResults(TypedDict):
    latency_avg: float
    latency_max: float
    latency_stdev: float
    latency_stdev_percent: float
    rps_avg: float
    rps_max: float
    rps_stdev: float
    rps_stdev_percent: float
    latency_distributions: list[LatencyDistribution]
    num_requests: int
    duration: int
    connect_errors: int
    read_errors: int
    write_errors: int
    timeout_errors: int
    rps: int


class ServerStats(TypedDict):
    time: str
    cpu_percent: float
    memory_usage_mb: float


def main(args):
    results = read_files(args.directory, "txt")
    load_logs = read_files(args.directory, "log")
    wrk_results = {}
    server_stats = []
    for wrk_result in results.values():
        wrk_results.update(parse_results(wrk_result))

    for log in load_logs.values():
        server_stats.extend(parse_server_stats(log))

    with open("results.json", "w") as f:
        f.write(json.dumps({
            "wrk_results": wrk_results,
            "server_stats": server_stats
        }, indent=4))


def parse_results(wrk_result: str) -> dict[str, dict[str, WrkResults]]:
    results = defaultdict(dict)
    lines = wrk_result.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith("Starting tests for "):
            i += 1
            continue
        server_name = line[len("Starting tests for "):].split(" ")[0]

        for line in lines[i:]:
            if line.startswith("Start "):
                _, test_name, test_start_time = line.split(" ")
                wrk_start_i = i + 2
                for j, line in enumerate(lines[wrk_start_i:]):
                    if line.startswith("End test "):
                        test_end_time = line[len("End test "):]
                        results[server_name][test_name] = {
                            "test_name": test_name,
                            "test_start_time": test_start_time,
                            "test_end_time": test_end_time,
                            "results": parse_wrk_results(
                                "\n".join(lines[wrk_start_i:wrk_start_i + j])
                            )
                        }
                        i = wrk_start_i + j
                        break
                else:
                    raise ValueError("End test not found")
        i += 1
    return results


def read_files(directory: str, extension: str) -> dict[str, str]:
    results = {}
    for file in os.listdir(directory):
        if not file.endswith(f".{extension}"):
            continue
        with open(os.path.join(directory, file)) as f:
            results[file] = f.read()
    return results


def parse_wrk_results(results: str) -> WrkResults:
    data = {
        "connect_errors": 0,
        "read_errors": 0,
        "write_errors": 0,
        "timeout_errors": 0,
    }
    lines = results.splitlines()
    for i, line in enumerate(lines):
        clean_line = _remove_multiple_spaces(line)
        if "Latency Distribution" in line:
            latency_distributions = []
            for j, line in enumerate(lines[i + 1:]):
                if "%" not in line:
                    break
                clean_line = _remove_multiple_spaces(line)
                percentage, latency = clean_line.split(" ")
                latency_distributions.append(
                    {"percentage": int(percentage[:-1]), "latency": _parse_time_to_seconds(latency)}
                )
            data["latency_distributions"] = latency_distributions
        elif "Latency" in line:
            _, latency_avg, latency_stdev, latency_max, latency_stdev_percent = clean_line.split(
                " "
            )
            data.update(
                {
                    "latency_avg": _parse_time_to_seconds(latency_avg),
                    "latency_max": _parse_time_to_seconds(latency_max),
                    "latency_stdev": _parse_time_to_seconds(latency_stdev),
                    "latency_stdev_percent": _parse_percents(latency_stdev_percent)
                }
            )
        elif "Req/Sec" in line:
            _, rps_avg, rps_stdev, rps_max, rps_stdev_percent = clean_line.split(" ")
            data.update(
                {
                    "rps_avg": _parse_count(rps_avg),
                    "rps_max": _parse_count(rps_max),
                    "rps_stdev": _parse_count(rps_stdev),
                    "rps_stdev_percent": _parse_percents(rps_stdev_percent)
                }
            )
        elif " requests in " in line:
            num_requests, _, _, duration, *_ = clean_line.replace(",", "").split(" ")
            data.update(
                {
                    "num_requests": int(_parse_count(num_requests)),
                    "duration": int(_parse_time_to_seconds(duration))
                }
            )
        elif "Requests/sec:" in line:
            _, rps = clean_line.split(" ")
            data["rps"] = int(_parse_count(rps))
        elif "Socket errors:" in line:
            parts = clean_line.replace(",", "").split(" ")
            connect_i, read_i, write_i, timeout_i = 3, 5, 7, 9
            data.update(
                {
                    "connect_errors": int(parts[connect_i]),
                    "read_errors": int(parts[read_i]),
                    "write_errors": int(parts[write_i]),
                    "timeout_errors": int(parts[timeout_i])
                }
            )
    return data


def parse_server_stats(log: str) -> list[ServerStats]:
    results = []
    for line in log.splitlines():
        log_time, cpu, memory, _ = line.split(",")
        used_memory, _ = memory.split(" / ")
        results.append(
            {
                "time": log_time,
                "cpu_percent": _parse_percents(cpu),
                "memory_usage_mb": _parse_memory(used_memory)
            }
        )
    return results


def _remove_multiple_spaces(s: str) -> str:
    return " ".join(s.strip().split())


def _parse_time_to_seconds(text: str) -> float:
    if text.endswith("ms"):
        return float(text[:-2]) / 1000
    elif text.endswith("us"):
        return float(text[:-2]) / 1_000_000
    elif text.endswith("s"):
        return float(text[:-1])
    else:
        raise ValueError("Time format not recognized")


def _parse_count(text: str) -> float:
    if text[-1].isdigit():
        return float(text)
    elif text.endswith("k"):
        return float(text[:-1]) * 1000
    else:
        raise ValueError("Count format not recognized")


def _parse_percents(text: str) -> float:
    if not text.endswith("%"):
        raise ValueError("Percent format not recognized")
    return float(text[:-1])

def _parse_memory(text: str) -> float:
    if text.endswith("MiB"):
        return float(text[:-3])
    else:
        raise ValueError("Memory format not recognized")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str, help="Directory containing the results")
    args = parser.parse_args()
    main(args)
