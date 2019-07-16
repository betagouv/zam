import transaction
from huey.storage import MemoryStorage


class TestTransactionalHuey:
    def test_task_is_enqueued_in_normal_mode(self):
        from zam_repondeur.tasks.queue import TransactionalHuey

        huey = TransactionalHuey(storage_class=MemoryStorage)

        assert huey.immediate is False
        assert huey.pending_count() == 0

        called = False

        @huey.task()
        def my_task():
            nonlocal called
            called = True

        with transaction.manager:
            my_task()

        assert called is False
        assert huey.pending_count() == 1

    def test_task_is_executed_in_immediate_mode(self):
        from zam_repondeur.tasks.queue import TransactionalHuey

        huey = TransactionalHuey(storage_class=MemoryStorage, immediate=True)

        assert huey.immediate is True
        assert huey.pending_count() == 0

        called = False

        @huey.task()
        def my_task():
            nonlocal called
            called = True

        my_task()

        assert called is True
        assert huey.pending_count() == 0
