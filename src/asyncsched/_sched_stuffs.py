__all__ = ('run', 'PreboundAPIs', )

from typing import Any, Literal
from collections.abc import Callable, Awaitable
from contextlib import AbstractAsyncContextManager

from sched import scheduler
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

import asyncgui as ag
from asyncgui import ISignal, IBox, Cancelled, Task


async def sleep(s: scheduler, priority, duration):
    sig = ISignal()
    event = s.enter(duration, priority, sig.set)
    try:
        await sig.wait()
    except Cancelled:
        s.cancel(event)
        raise


def move_on_after(s: scheduler, priority, timeout) -> AbstractAsyncContextManager[Task]:
    return ag.wait_any_cm(sleep(s, priority, timeout))


def _wrapper(s: scheduler, priority, func, box):
    '''A wrapper function used by the threading APIs'''
    ret = None
    exc = None
    try:
        ret = func()
    except Exception as e:
        exc = e
    finally:
        s.enter(0, priority, box.put, (ret, exc, ))


async def run_in_thread(s: scheduler, priority, func: Callable[[], Any], *, daemon: Literal[None, True, False]=None):
    box = IBox()
    Thread(
        name='asyncsched.run_in_thread',
        target=_wrapper, daemon=daemon, args=(s, priority, func, box, ),
    ).start()
    ret, exc = (await box.get())[0]
    if exc is None:
        return ret
    raise exc


async def run_in_executor(s: scheduler, priority, executor: ThreadPoolExecutor, func: Callable[[], Any]):
    box = IBox()
    future = executor.submit(_wrapper, s, priority, func, box)
    try:
        ret, exc = (await box.get())[0]
    except Cancelled:
        future.cancel()
        raise
    assert future.done()
    if exc is None:
        return ret
    raise exc


class PreboundAPIs:
    '''
    You should not directly instantiate this class.
    '''

    async def sleep(self, duration):
        '''
        Waits for a specified ``duration``.

        .. code-block::

            await apis.sleep(duration)
        '''

    def move_on_after(timeout) -> AbstractAsyncContextManager[Task]:
        '''
        :func:`trio.move_on_after` equivalent.

        .. code-block::

            async with apis.move_on_after(timeout) as bg_task:
                ...
            if bg_task.finished:
                print("with-block was cancelled due to a timeout")
            else:
                print("with-block completed.")
        '''

    async def run_in_thread(self, func: Callable[[], Any], *, daemon: Literal[None, True, False]=None):
        '''
        Creates a new thread, runs a function inside it, then waits for the completion of the function.

        .. code-block::

            return_value = await apis.run_in_thread(func)
        '''

    async def run_in_executor(self, executor: ThreadPoolExecutor, func: Callable[[], Any]):
        '''
        Runs a function within a :class:`concurrent.futures.ThreadPoolExecutor`, and waits for the completion of the
        function.

        .. code-block::

            executor = ThreadPoolExecutor()
            ...
            return_value = await apis.run_in_executor(executor, func)
        '''


async def _pulse(sleep, interval):
    while True:
        await sleep(interval)


def run(main_func: Callable[[scheduler, PreboundAPIs], Awaitable], *, priority=10, pulse_interval=1.) -> Task:
    from functools import partial

    s = scheduler()
    apis = PreboundAPIs()
    apis.sleep = partial(sleep, s, priority)
    apis.move_on_after = partial(move_on_after, s, priority)
    apis.run_in_thread = partial(run_in_thread, s, priority)
    apis.run_in_executor = partial(run_in_executor, s, priority)

    root_task = ag.start(ag.wait_any(
        _pulse(partial(sleep, s, priority + 10), pulse_interval),
        main_task := Task(main_func(s, apis)),
    ))
    s.run()
    return main_task
