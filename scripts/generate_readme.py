import argparse
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import json
from os import makedirs
from statistics import mean, median
import seaborn as sns
import matplotlib.pyplot as plt
from jinja2 import Environment, PackageLoader, select_autoescape


jinja_env = Environment(
    loader=PackageLoader("generate_readme", ".."),
    autoescape=select_autoescape()
)


@dataclass
class ServerStats:
    time: datetime
    cpu_percent: float
    memory_usage_mb: float


@dataclass
class BenchmarkResults:
    framework: str
    start_time: datetime
    end_time: datetime
    latency_mean_ms: int
    latency_min_ms: int
    latency_max_ms: int
    latency_stdev_ms: int
    latency_percentile_90_ms: int
    latency_percentile_99_ms: int
    duration_sec: int
    requests_num: float
    bytes_received: int
    errors_num: int
    cpu_avg_percent: int
    cpu_median_percent: int
    memory_median_mb: float
    memory_max_mb: float

    @property
    def rps(self) -> int:
        return int(self.requests_num / self.duration_sec)


def generate_images(benchmarks: dict[str, list[BenchmarkResults]]) -> dict[str, dict[str, str]]:
    shutil.rmtree("results/images", ignore_errors=True)
    makedirs("results/images")

    images_by_test_name = defaultdict(dict)
    for test_name, benchmark_results in benchmarks.items():
        names = [result.framework for result in benchmark_results]
        filename_template = f"results/images/{test_name}_{{}}.png"

        rps = [result.rps for result in benchmark_results]
        rps_image = filename_template.format("rps")
        create_chart(names, rps, "Requests per second", rps_image, x_label="RPS (higher is better)")
        images_by_test_name[test_name]["rps"] = rps_image

        latency_avg = [result.latency_mean_ms for result in benchmark_results]
        latency_avg_image = filename_template.format("latency_avg")
        create_chart(names, latency_avg, "Average latency", latency_avg_image, x_label="ms, lower is better", reverse=False)
        images_by_test_name[test_name]["latency_avg"] = latency_avg_image

        latency_max = [result.latency_max_ms for result in benchmark_results]
        latency_max_image = filename_template.format("latency_max")
        create_chart(names, latency_max, "Max latency", latency_max_image, x_label="ms, lower is better", reverse=False)
        images_by_test_name[test_name]["latency_max"] = latency_max_image

        latency_90th = [result.latency_percentile_90_ms for result in benchmark_results]
        latency_90th_image = filename_template.format("latency_90th")
        create_chart(names, latency_90th, "90th percentile latency", latency_90th_image, x_label="ms, lower is better", reverse=False)
        images_by_test_name[test_name]["latency_90th"] = latency_90th_image

        latency_99th = [result.latency_percentile_99_ms for result in benchmark_results]
        latency_99th_image = filename_template.format("latency_99th")
        create_chart(names, latency_99th, "99th percentile latency", latency_99th_image, x_label="ms, lower is better", reverse=False)
        images_by_test_name[test_name]["latency_99th"] = latency_99th_image

        cpu_avg_percent = [result.cpu_avg_percent for result in benchmark_results]
        cpu_avg_percent_image = filename_template.format("cpu_avg_percent")
        create_chart(names, cpu_avg_percent, "Average CPU usage (0-400%)", cpu_avg_percent_image, x_label="%")
        images_by_test_name[test_name]["cpu_avg_percent"] = cpu_avg_percent_image

        cpu_median_percent = [result.cpu_median_percent for result in benchmark_results]
        cpu_median_percent_image = filename_template.format("cpu_median_percent")
        create_chart(names, cpu_median_percent, "Median CPU usage (0-400%)", cpu_median_percent_image, x_label="%")
        images_by_test_name[test_name]["cpu_median_percent"] = cpu_median_percent_image

        memory_median_mb = [result.memory_median_mb for result in benchmark_results]
        memory_median_mb_image = filename_template.format("memory_median_mb")
        create_chart(names, memory_median_mb, "Median memory usage", memory_median_mb_image, x_label="mb, lower is better", reverse=False)
        images_by_test_name[test_name]["memory_median_mb"] = memory_median_mb_image

        memory_max_mb = [result.memory_max_mb for result in benchmark_results]
        memory_max_mb_image = filename_template.format("memory_max_mb")
        create_chart(names, memory_max_mb, "Max memory usage", memory_max_mb_image, x_label="mb, lower is better", reverse=False)
        images_by_test_name[test_name]["memory_max_mb"] = memory_max_mb_image

    return images_by_test_name


def generate_readme(benchmarks: dict[str, list[BenchmarkResults]], images_by_test_name: dict[str, dict[str, str]]):
    template = jinja_env.get_template("README.jinja2")
    with open("README.md", "w") as f:
        f.write(template.render(benchmarks=benchmarks, images=images_by_test_name))


def microsecond_to_milliseconds(microseconds: float) -> int:
    return round(microseconds / 1000)


def microsecond_to_seconds(microseconds: float) -> int:
    return round(microseconds / 1_000_000)


def create_chart(names: list[str], values: list[float], title: str, filename: str, x_label: str | None = None, reverse: bool = True):
    items = list(zip(names, values))
    items.sort(key=lambda x: x[1], reverse=reverse)
    sorted_names, sorted_values = zip(*items)

    sns.set_style("darkgrid")
    # sns.set_context("paper")

    plt.figure(figsize=(6, 6))
    barplot = sns.barplot(x=sorted_values, y=sorted_names, orient='h')

    # Add value labels to each bar
    for i, v in enumerate(sorted_values):
        barplot.text(v + 1, i, str(v), va='center')

    plt.title(title)
    if x_label:
        plt.xlabel(x_label)
    # https://stackoverflow.com/questions/1271023/
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    # plt.show()


def parse_results(results: dict) -> dict[str, dict[str, BenchmarkResults]]:
    server_stats = [
        ServerStats(
            time=_parse_datetime(item["time"]),
            cpu_percent=item["cpu_percent"],
            memory_usage_mb=item["memory_usage_mb"]
        )
        for item in results["server_stats"]
    ]

    by_test_name = {}
    for wrk_result in results["wrk_results"]:
        framework = wrk_result["framework"]
        test_name = wrk_result["path"]
        start_time = _parse_datetime(wrk_result["start_time"])
        end_time = _parse_datetime(wrk_result["end_time"])
        calculated_stats = _calculate_server_stats(server_stats, start_time, end_time)

        by_test_name.setdefault(test_name, []).append(
            BenchmarkResults(
                framework=framework,
                start_time=start_time,
                end_time=end_time,
                latency_mean_ms=microsecond_to_milliseconds(wrk_result["latency_mean"]),
                latency_min_ms=microsecond_to_milliseconds(wrk_result["latency_min"]),
                latency_max_ms=microsecond_to_milliseconds(wrk_result["latency_max"]),
                latency_stdev_ms=microsecond_to_milliseconds(wrk_result["latency_stdev"]),
                latency_percentile_90_ms=microsecond_to_milliseconds(wrk_result["latency_percentile_90"]),
                latency_percentile_99_ms=microsecond_to_milliseconds(wrk_result["latency_percentile_99"]),
                duration_sec=microsecond_to_seconds(wrk_result["duration"]),
                requests_num=wrk_result["requests_num"],
                bytes_received=round(wrk_result["bytes_received"]),
                errors_num=int(
                        wrk_result["errors_status"]
                        + wrk_result["errors_connect"]
                        + wrk_result["errors_read"]
                        + wrk_result["errors_write"]
                        + wrk_result["errors_timeout"]
                ),
                **calculated_stats,
            )
        )

    return by_test_name


def _calculate_server_stats(server_stats: list[ServerStats], time_start: datetime, time_end: datetime) -> dict[str, float]:
    cpu_data = []
    memory_data = []
    for item in server_stats:
        if time_start <= item.time <= time_end:
            cpu_data.append(item.cpu_percent)
            memory_data.append(item.memory_usage_mb)

    cpu_data = [1]
    memory_data = [1]
    return {
        "cpu_avg_percent": round(mean(cpu_data)),
        "cpu_median_percent": round(median(cpu_data)),
        "memory_median_mb": median(memory_data),
        "memory_max_mb": max(memory_data),
    }


def _parse_datetime(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")


def main(args):
    with open(args.results_file) as f:
        results = json.load(f)

    by_test_name = parse_results(results)
    images_by_test_name = generate_images(by_test_name)
    generate_readme(by_test_name, images_by_test_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_file", required=True, type=str, help="File with benchmark results")
    # parser.add_argument("--template_file", required=True, type=str)
    # parser.add_argument("--output", required=True, type=str)
    args = parser.parse_args()
    main(args)
