# My Web Frameworks Benchmarks Results

## Disclaimer

Just a simple benchmark to compare the overhead of some web frameworks.
Not representative of real world usage,
don't take it too seriously and always do your own benchmarks.

## Methodology

For benchmarking I used laptop with Intel Core i5-7300hq and 24GB RAM for running
web frameworks and MacBook Air M1 with 16GB RAM for running wrk.
As database server I used Raspberry Pi 4B with 2GB RAM 😀, running Postgres 17,
database was stored on tmpfs in RAM.

All machines were connected via 1Gbps ethernet cable.
Throughput checked with `iperf3` was around 940Mbps.

<details>
    <summary>iperf3 results</summary>

```
[nix-shell:~/web_benchmarks]$ iperf -c 192.168.99.1
Connecting to host 192.168.99.1, port 5201
[  5] local 192.168.99.2 port 63217 connected to 192.168.99.1 port 5201
[ ID] Interval           Transfer     Bitrate
[  5]   0.00-1.01   sec   115 MBytes   958 Mbits/sec
[  5]   1.01-2.00   sec   114 MBytes   956 Mbits/sec
[  5]   2.00-3.00   sec   111 MBytes   936 Mbits/sec
[  5]   3.00-4.01   sec   113 MBytes   947 Mbits/sec
[  5]   4.01-5.00   sec   111 MBytes   937 Mbits/sec
[  5]   5.00-6.00   sec   113 MBytes   946 Mbits/sec
[  5]   6.00-7.00   sec   112 MBytes   939 Mbits/sec
[  5]   7.00-8.01   sec   110 MBytes   926 Mbits/sec
[  5]   8.01-9.00   sec   114 MBytes   959 Mbits/sec
[  5]   9.00-10.01  sec   111 MBytes   932 Mbits/sec
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate
[  5]   0.00-10.01  sec  1.10 GBytes   944 Mbits/sec                  sender
[  5]   0.00-10.01  sec  1.10 GBytes   941 Mbits/sec                  receiver

iperf Done.
```
</details>

Frameworks not limited by RAM or CPU, if framework can use multiple threads
I set it to use all available threads (4 in case of my laptop).

To collect cpu and memory usage I used `monitor.sh` script that just dumps docker stats to a file.

wrk was run with 8 threads, because it's the number of threads that my MacBook Air M1 has.
Connections number is 64. While running wrk CPU usage was never at 100%, so wrk was not a bottleneck.

## Results

Participants:

- [go-stdlib](https://github.com/golang/go): Go stdlib http server, [pgx-v5](https://github.com/jackc/pgx) postgresql driver.
- [uvicorn](https://www.uvicorn.org): ASGI server, uses
    [uvloop](https://github.com/MagicStack/uvloop) and
    [httptools](https://github.com/MagicStack/httptools) for parsing requests,
    [orjson](https://github.com/ijl/orjson) for json serialization and
    [asyncpg](https://github.com/MagicStack/asyncpg) postgresql driver.
- uvicorn-one-worker: same as uvicorn, but with only one worker.
- uvicorn-h11: same as uvicorn, but uses [h11](https://github.com/python-hyper/h11) for http.
- uvicorn-asyncio: same as uvicorn, but uses stdlib asyncio loop.
- uvicorn-stdlib: uvicorn with stdlib asyncio loop, h11 and stdlib json serialization.
- uvicorn-stdlib-one-worker: same as uvicorn-stdlib, but with only one worker.
- uvicorn-pypy: uvicorn with [PyPy](https://pypy.org), h11 and pure Python [psycopg](https://github.com/psycopg/psycopg).
- [fastapi](https://github.com/fastapi/fastapi): fastapi + orjson + asyncpg, every view has async fastapi dependency.
- fastapi-sync-endpoints: same as fastapi, but with sync views, db endpoint is not included in tests.
- fastapi-sync-dependency: same as fastapi, but every endpoint has sync fastapi dependency.
- django-sync-worker: [django](https://github.com/django/django) + [gunicorn](https://github.com/benoitc/gunicorn) with sync worker
- django-gthread-worker: same as django-sync-worker, but with gthread worker
- django-gevent-worker: same as django-sync-worker, but with gevent worker
- django-asgi: django + uvicorn. Using async views.
- [robyn](https://github.com/sparckles/Robyn): robyn + asyncpg
- socketify-async: [socketify.py](https://github.com/cirospaciari/socketify.py) + asyncpg + orjson. Async views.
- socketify-sync: socketify.py + psycopg + orjson. Sync views.
- socketify-async-pypy: socketify.py + psycopg + PyPy. Async views.
- socketify-sync-pypy: socketify.py + psycopg + PyPy. Sync views.
- falcon-wsgi-sync-worker: [falcon](https://github.com/falconry/falcon) + psycopg + orjson + gunicorn with sync worker. WSGI server.
- falcon-wsgi-gthread-worker: same as falcon-wsgi-sync-worker, but with gthread worker.
- falcon-wsgi-gevent-worker: same as falcon-wsgi-sync-worker, but with gevent worker.
- falcon-wsgi-sync-worker-pypy: falcon + psycopg + PyPy + gunicorn with sync worker. WSGI server.
- falcon-wsgi-gthread-worker-pypy: same as falcon-wsgi-sync-worker-pypy, but with gthread worker.
- falcon-wsgi-gevent-worker-pypy: same as falcon-wsgi-sync-worker-pypy, but with gevent worker.
- [laravel](https://github.com/laravel/laravel): standard laravel installation, nginx + php-fpm (all in one container).
- laravel-octane-franken: laravel [octane](https://laravel.com/docs/12.x/octane) with [frankenphp](https://github.com/dunglas/frankenphp)

### Plaintext

Just a simple plaintext response. Dont't expect too much from it,
not representative of real world usage, just a simple overhead comparison.


![results/images/plaintext_rps.png](results/images/plaintext_rps.png)
![results/images/plaintext_cpu_avg_percent.png](results/images/plaintext_cpu_avg_percent.png)

<details>
    <summary>CPU median</summary>

![results/images/plaintext_cpu_median_percent.png](results/images/plaintext_cpu_median_percent.png)
</details>

![results/images/plaintext_memory_median_mb.png](results/images/plaintext_memory_median_mb.png)

<details>
    <summary>Memory max</summary>

![results/images/plaintext_memory_max_mb.png](results/images/plaintext_memory_max_mb.png)
</details>

![results/images/plaintext_latency_avg.png](results/images/plaintext_latency_avg.png)

<details>
    <summary>Latency max</summary>

![results/images/plaintext_latency_max.png](results/images/plaintext_latency_max.png)
</details>

<details>
    <summary>Latency 90th</summary>

![results/images/plaintext_latency_90th.png](results/images/plaintext_latency_90th.png)
</details>

<details>
    <summary>Latency 99th</summary>

![results/images/plaintext_latency_99th.png](results/images/plaintext_latency_99th.png)
</details>


### API

"Api" workload - parse query parameter, header and return them in json response.
Again, not representative of real world usage, just a simple overhead comparison of
framework validation and json serialization.


![results/images/api_rps.png](results/images/api_rps.png)
![results/images/api_cpu_avg_percent.png](results/images/api_cpu_avg_percent.png)

<details>
    <summary>CPU median</summary>

![results/images/api_cpu_median_percent.png](results/images/api_cpu_median_percent.png)
</details>

![results/images/api_memory_median_mb.png](results/images/api_memory_median_mb.png)

<details>
    <summary>Memory max</summary>

![results/images/api_memory_max_mb.png](results/images/api_memory_max_mb.png)
</details>

![results/images/api_latency_avg.png](results/images/api_latency_avg.png)

<details>
    <summary>Latency max</summary>

![results/images/api_latency_max.png](results/images/api_latency_max.png)
</details>

<details>
    <summary>Latency 90th</summary>

![results/images/api_latency_90th.png](results/images/api_latency_90th.png)
</details>

<details>
    <summary>Latency 99th</summary>

![results/images/api_latency_99th.png](results/images/api_latency_99th.png)
</details>



### Database

Database workload - this is more representative of real world usage.
One query to select 1 row by id and another query to select 100 rows.
All data retrieved from database instantiated as some structure
(for example - dataclasses in Python and Struct in Go) and then serialized to json.


![results/images/db_rps.png](results/images/db_rps.png)
![results/images/db_cpu_avg_percent.png](results/images/db_cpu_avg_percent.png)

<details>
    <summary>CPU median</summary>

![results/images/db_cpu_median_percent.png](results/images/db_cpu_median_percent.png)
</details>

![results/images/db_memory_median_mb.png](results/images/db_memory_median_mb.png)

<details>
    <summary>Memory max</summary>

![results/images/db_memory_max_mb.png](results/images/db_memory_max_mb.png)
</details>

![results/images/db_latency_avg.png](results/images/db_latency_avg.png)

<details>
    <summary>Latency max</summary>

![results/images/db_latency_max.png](results/images/db_latency_max.png)
</details>

<details>
    <summary>Latency 90th</summary>

![results/images/db_latency_90th.png](results/images/db_latency_90th.png)
</details>

<details>
    <summary>Latency 99th</summary>

![results/images/db_latency_99th.png](results/images/db_latency_99th.png)
</details>
