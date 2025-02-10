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
    name: str
    start_time: datetime
    end_time: datetime
    latency_avg: float
    latency_max: float
    latency_stdev: float
    latency_stdev_percent: float
    latency_90th: float
    latency_99th: float
    rps_avg: float
    rps_max: float
    rps_stdev: float
    rps_stdev_percent: float
    num_requests: int
    duration_sec: int
    rps: int
    errors: int
    cpu_avg_percent: float
    cpu_median_percent: float
    memory_median_mb: float
    memory_max_mb: float


def main(args):
    with open(args.results_file) as f:
        results = json.load(f)

    by_test_name = parse_results(results)
    images_by_test_name = generate_images(by_test_name)
    generate_readme(by_test_name, images_by_test_name)


def generate_images(benchmarks: dict[str, list[BenchmarkResults]]) -> dict[str, dict[str, str]]:
    shutil.rmtree("results/images", ignore_errors=True)
    makedirs("results/images")

    images_by_test_name = defaultdict(dict)
    for test_name, benchmark_results in benchmarks.items():
        names = [result.name for result in benchmark_results]
        filename_template = f"results/images/{test_name}_{{}}.png"

        rps = [result.rps for result in benchmark_results]
        rps_image = filename_template.format("rps")
        create_chart(names, rps, "Requests per second", rps_image, x_label="RPS (higher is better)")
        images_by_test_name[test_name]["rps"] = rps_image

        latency_avg = [seconds_to_ms(result.latency_avg) for result in benchmark_results]
        latency_avg_image = filename_template.format("latency_avg")
        create_chart(names, latency_avg, "Average latency", latency_avg_image, x_label="ms, lower is better", reverse=False)
        images_by_test_name[test_name]["latency_avg"] = latency_avg_image

        latency_max = [seconds_to_ms(result.latency_max) for result in benchmark_results]
        latency_max_image = filename_template.format("latency_max")
        create_chart(names, latency_max, "Max latency", latency_max_image, x_label="ms, lower is better", reverse=False)
        images_by_test_name[test_name]["latency_max"] = latency_max_image

        latency_90th = [seconds_to_ms(result.latency_90th) for result in benchmark_results]
        latency_90th_image = filename_template.format("latency_90th")
        create_chart(names, latency_90th, "90th percentile latency", latency_90th_image, x_label="ms, lower is better", reverse=False)
        images_by_test_name[test_name]["latency_90th"] = latency_90th_image

        cpu_avg_percent = [round(result.cpu_avg_percent) for result in benchmark_results]
        cpu_avg_percent_image = filename_template.format("cpu_avg_percent")
        create_chart(names, cpu_avg_percent, "Average CPU usage (0-400%)", cpu_avg_percent_image, x_label="%")
        images_by_test_name[test_name]["cpu_avg_percent"] = cpu_avg_percent_image

        cpu_median_percent = [round(result.cpu_median_percent) for result in benchmark_results]
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

def seconds_to_ms(seconds: float) -> int:
    return round(seconds * 1000)


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
    for framework_name, framework_results in results["wrk_results"].items():
        for test_name, test in framework_results.items():
            test_results = test["results"]
            start_time = _parse_datetime(test["test_start_time"])
            end_time = _parse_datetime(test["test_end_time"])
            calculated_stats = _calculate_server_stats(server_stats, start_time, end_time)

            by_test_name.setdefault(test_name, []).append(
                BenchmarkResults(
                    name=framework_name,
                    start_time=start_time,
                    end_time=end_time,
                    latency_avg=test_results["latency_avg"],
                    latency_max=test_results["latency_max"],
                    latency_stdev=test_results["latency_stdev"],
                    latency_stdev_percent=test_results["latency_stdev_percent"],
                    latency_90th=_get_distribution(90, test_results["latency_distributions"]),
                    latency_99th=_get_distribution(99, test_results["latency_distributions"]),
                    rps_avg=test_results["rps_avg"],
                    rps_max=test_results["rps_max"],
                    rps_stdev=test_results["rps_stdev"],
                    rps_stdev_percent=test_results["rps_stdev_percent"],
                    num_requests=test_results["num_requests"],
                    duration_sec=test_results["duration"],
                    rps=test_results["rps"],
                    errors=(
                        test_results["connect_errors"]
                        + test_results["read_errors"]
                        + test_results["write_errors"]
                        + test_results["timeout_errors"]
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


    return {
        "cpu_avg_percent": mean(cpu_data),
        "cpu_median_percent": median(cpu_data),
        "memory_median_mb": median(memory_data),
        "memory_max_mb": max(memory_data),
    }



def _parse_datetime(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")


def _get_distribution(percent: int, distributions: list[dict[str, float]]) -> float:
    for distribution in distributions:
        if distribution["percentage"] == percent:
            return distribution["latency"]
    raise ValueError(f"Percent {percent} not found in distributions")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_file", required=True, type=str, help="File with benchmark results")
    # parser.add_argument("--template_file", required=True, type=str)
    # parser.add_argument("--output", required=True, type=str)
    args = parser.parse_args()
    main(args)
