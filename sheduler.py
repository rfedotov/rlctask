import asyncio, time, random
start_time = time.time()

async def do_stuff_periodically(interval, periodic_function, *args, **kwargs):
    while True:
        print(round(time.time() - start_time, 1), "Starting periodic function")
        await asyncio.gather(
            asyncio.sleep(interval),
            periodic_function(*args, **kwargs),
        )
