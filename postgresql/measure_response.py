import asyncio
import os
import time
from statistics import mean, median

import asyncpg


async def measure(pool):
    measurements = []
    for i in range(1100):
        start = time.monotonic()
        async with pool.acquire() as conn:
            await conn.fetch(
                'SELECT * FROM users WHERE id = $1',
                1,
            )
            await conn.fetch(
                'SELECT * FROM devices LIMIT 10',
            )
        end = time.monotonic()
        if i >= 100:
            measurements.append(end - start)
    return measurements


async def setup_pool():
    return await asyncpg.create_pool(
        user="postgres",
        password="postgres",
        database="postgres",
        host=os.getenv("POSTGRES_HOST", "localhost"),
    )


async def main():
    pool = await setup_pool()
    measurements = await measure(pool)
    measurements_ms = [m * 1000 for m in measurements]
    print(f"Mean: {mean(measurements_ms)}")
    print(f"Median: {median(measurements_ms)}")
    print(f"Max: {max(measurements_ms)}")
    print(f"Min: {min(measurements_ms)}")


if __name__ == "__main__":
    asyncio.run(main())
