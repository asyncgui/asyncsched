import string
import asyncsched as asched


async def main(scheduler, apis: asched.PreboundAPIs):
    tasks = await asched.wait_any(
        print_little_by_little(apis, string.ascii_uppercase),
        print_little_by_little(apis, string.digits),
    )
    print("")
    if tasks[0].finished:
        print("Alphabets won.")
    else:
        print("Digits won.")


async def print_little_by_little(apis: asched.PreboundAPIs, msg, *, interval=0.1):
    for c in msg:
        print(c, end=' ')
        await apis.sleep(interval)


if __name__ == '__main__':
    asched.run(main)
