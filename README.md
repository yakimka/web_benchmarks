# My Web Frameworks Benchmarks Results

## Disclaimer

Just a simple benchmark to compare the overhead of some web frameworks.
Not representative of real world usage,
don't take it too seriously and always do your own benchmarks.


## Methodology

For benchmarking I used laptop with Intel Core i5-7300hq for running web frameworks and
MacBook Air M1 for running wrk.

Frameworks not limited by RAM or CPU, if framework can use multiple threads
I set it to use all available threads (4 in case of my laptop).

To collect cpu and memory usage I used `monitor.sh` script that just dumps docker stats to a file.

