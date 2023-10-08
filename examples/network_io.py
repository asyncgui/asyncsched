import requests
import asyncsched as asched


async def repeat_printing_dot(apis: asched.PreboundAPIs, *, interval=.1):
    while True:
        print(".", end=' ')
        await apis.sleep(interval)


async def main(scheduler, apis: asched.PreboundAPIs):
    tasks = await asched.wait_any(
        repeat_printing_dot(apis),  # prints dots just to confirm the main thread is not freezing
        apis.run_in_thread(lambda: requests.get(r"https://httpbin.org/delay/2")),
    )
    res: requests.Response = tasks[1].result
    print(res.headers['Date'])


if __name__ == '__main__':
    asched.run(main)
