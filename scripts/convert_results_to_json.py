import argparse
import json
import os
from typing import TypedDict


class WrkResults(TypedDict):
    latency_mean: float
    latency_min: float
    latency_max: float
    latency_stdev: float
    latency_percentile_90: float
    latency_percentile_99: float
    duration: float
    requests_num: float
    bytes_received: float
    errors_status: float
    errors_connect: float
    errors_read: float
    errors_write: float
    errors_timeout: float
    start_time: float
    end_time: float
    framework: str
    path: str


class ServerStats(TypedDict):
    time: str
    cpu_percent: float
    memory_usage_mb: float


CONVERTERS = {
    "path": lambda x: x.split("?")[0].removeprefix("/").strip(),
    "start_time": str,
    "end_time": str,
    "framework": str,
}


def parse_wrk_results(wrk_result: str) -> list[WrkResults]:
    lines = wrk_result.splitlines()
    results = [{}]
    for line in lines:
        if not line:
            results.append({})
            continue
        name, value = line.split(": ")
        converter = CONVERTERS.get(name, float)
        results[-1][name] = converter(value)
    if not results[-1]:
        results.pop()
    return results


def read_files(directory: str, extension: str) -> dict[str, str]:
    results = {}
    for file in os.listdir(directory):
        if not file.endswith(f".{extension}"):
            continue
        with open(os.path.join(directory, file)) as f:
            results[file] = f.read()
    return results


def parse_server_stats(log: str) -> list[ServerStats]:
    results = []
    for line in log.splitlines():
        log_time, cpu, memory, _ = line.split(",")
        used_memory, _ = memory.split(" / ")
        results.append(
            {
                "time": log_time,
                "cpu_percent": _parse_percents(cpu),
                "memory_usage_mb": _parse_memory(used_memory),
            }
        )
    return results


def _parse_percents(text: str) -> float:
    if not text.endswith("%"):
        raise ValueError("Percent format not recognized")
    return float(text[:-1])


def _parse_memory(text: str) -> float:
    text = text.strip()
    if text.endswith("MiB"):
        return float(text[:-3])
    elif text == "0B":
        return 0
    else:
        raise ValueError(f"Memory format not recognized: {text}.")


def main(args):
    results = read_files(args.directory, "txt")
    load_logs = read_files(args.directory, "log")
    wrk_results = []
    server_stats = []
    for wrk_result in results.values():
        wrk_results.extend(parse_wrk_results(wrk_result))

    for log in load_logs.values():
        server_stats.extend(parse_server_stats(log))

    with open(args.output, "w") as f:
        f.write(
            json.dumps(
                {"wrk_results": wrk_results, "server_stats": server_stats}, indent=4
            )
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str, help="Directory containing the results")
    parser.add_argument(
        "--output", type=str, default="results.json", help="Output file"
    )
    args = parser.parse_args()
    main(args)
