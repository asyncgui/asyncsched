# asyncsched

Async library for the `sched` module from the Python standard library.

```python
import requests
import asyncsched as asch


async def main(scheduler, apis: asch.PreboundAPIs):
    # Waits for 2 seconds.
    await apis.sleep(2)

    # Creates a new thread, runs a function inside it, then waits for the completion of that function.
    task = await apis.run_in_thread(lambda: requests.get(r"https://httpbin.org/delay/2")),
    res: requests.Response = task.result
    print(res.headers['Date'])

    # Repeats printing 'Hello' but gives up on 5 seconds.
    async with apis.move_on_after(5):
        while True:
            print("Hello")
            await apis.sleep(.1)

    # Waits for either of 'async_func_1()' or 'async_func_2()' to complete.
    tasks = await asch.wait_any(async_func_1(), async_func_2(), )
    if tasks[0].finished:
        print("'async_func_1()' has completed.")
    else:
        print("'async_func_2()' has completed.")


if __name__ == '__main__':
    asch.run(main)
```

## Installation

```text
poetry add git+https://github.com/asyncgui/asyncsched
poetry add git+ssh://github.com/asyncgui/asyncsched
pip install "asyncsched @ git+ssh://git@github.com/asyncgui/asyncsched"
pip install "asyncsched @ git+https://github.com/asyncgui/asyncsched"
```

## Tested on

- CPython 3.9
- CPython 3.10
- CPython 3.11
