import pytest


@pytest.fixture
def executor():
    from concurrent.futures import ThreadPoolExecutor
    return ThreadPoolExecutor()


def test_return_value(executor):
    from asyncsched import run

    async def main(scheduler, apis):
        r = await apis.run_in_executor(executor, lambda: 'Hello')
        assert r == 'Hello'

    task = run(main, pulse_interval=0.01)
    assert task.finished


def test_the_caller_is_resumed_in_the_same_thread(executor):
    from threading import get_ident
    from asyncsched import run

    async def main(scheduler, apis):
        before = get_ident()
        r = await apis.run_in_executor(executor, lambda: None)
        after = get_ident()
        assert before == after

    task = run(main, pulse_interval=0.01)
    assert task.finished


def test_the_callee_runs_in_a_different_thread(executor):
    from threading import get_ident
    from asyncsched import run

    async def main(scheduler, apis):
        caller_id = get_ident()

        def func():
            callee_id = get_ident()
            assert caller_id != callee_id

        await apis.run_in_executor(executor, func)

    task = run(main, pulse_interval=0.01)
    assert task.finished


def test_thread_ends_before_the_next_pulse(executor):
    import time
    from asyncsched import run

    async def main(scheduler, apis):
        await apis.run_in_executor(executor, lambda: time.sleep(0.1))

    task = run(main, pulse_interval=0.2)
    assert task.finished


def test_thread_ends_after_the_next_pulse(executor):
    import time
    from asyncsched import run

    async def main(scheduler, apis):
        await apis.run_in_executor(executor, lambda: time.sleep(0.2))

    task = run(main, pulse_interval=0.1)
    assert task.finished
