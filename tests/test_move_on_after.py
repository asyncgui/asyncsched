def test_with_block_exits_due_to_a_timeout():
    from asyncsched import run

    async def main(scheduler, apis):
        async with apis.move_on_after(0.01) as bg_task:
            await apis.sleep(0.02)
        assert bg_task.finished

    task = run(main)
    assert task.finished


def test_with_block_completes():
    from asyncsched import run

    async def main(scheduler, apis):
        async with apis.move_on_after(0.02) as bg_task:
            await apis.sleep(0.01)
        assert not bg_task.finished

    task = run(main)
    assert task.finished
