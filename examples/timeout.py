from string import ascii_letters
import asyncsched as asched


async def main(scheduler, apis: asched.PreboundAPIs):
    async with apis.move_on_after(3) as bg_task:
        for c in ascii_letters:
            print(c, end=' ')
            await apis.sleep(.1)
    if bg_task.finished:
        print("TIMEOUT!!")
    else:
        print("COMPLETED")


if __name__ == '__main__':
    asched.run(main)
