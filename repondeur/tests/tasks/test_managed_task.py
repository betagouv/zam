from unittest.mock import Mock

import pytest
import transaction

from redis.exceptions import ConnectionError
from transaction.interfaces import DoomedTransaction


class FakeHuey:
    def __init__(self, immediate):
        self.immediate = immediate
        self.enqueued = []
        self.pending_count = Mock(return_value=0)

    def really_enqueue(self, task):
        self.enqueued.append(task)


@pytest.fixture
def huey():
    return FakeHuey(immediate=False)


class TestManagedTask:
    def test_managed_task_can_join_the_current_transaction(self, huey):
        from zam_repondeur.tasks.queue import ManagedTask

        with transaction.manager as txn:
            task = object()
            managed_task = ManagedTask(huey, task)
            managed_task.join_transaction()
            assert managed_task in txn._resources
            assert managed_task.transaction is txn

    def test_managed_task_is_enqueud_if_transaction_is_committed(self, huey):
        from zam_repondeur.tasks.queue import ManagedTask

        with transaction.manager:
            task = object()
            managed_task = ManagedTask(huey, task)
            managed_task.join_transaction()

        assert task in huey.enqueued

    def test_managed_task_is_not_enqueud_if_transaction_is_aborted(self, huey):
        from zam_repondeur.tasks.queue import ManagedTask

        with transaction.manager as txn:
            task = object()
            managed_task = ManagedTask(huey, task)
            managed_task.join_transaction()
            txn.abort()

        assert task not in huey.enqueued

    def test_managed_task_is_not_enqueud_if_transaction_is_doomed(self, huey):
        from zam_repondeur.tasks.queue import ManagedTask

        with pytest.raises(DoomedTransaction):
            with transaction.manager as txn:
                task = object()
                managed_task = ManagedTask(huey, task)
                managed_task.join_transaction()
                txn.doom()

        assert task not in huey.enqueued

    def test_redis_connection_error_in_voting_aborts_the_transaction(self, huey):
        from zam_repondeur.tasks.queue import ManagedTask

        huey.pending_count.side_effect = ConnectionError()

        with pytest.raises(ConnectionError):
            with transaction.manager:
                task = object()
                managed_task = ManagedTask(huey, task)
                managed_task.join_transaction()

        assert task not in huey.enqueued

    def test_redis_connection_error_in_finish_aborts_the_transaction(self, huey):
        from zam_repondeur.tasks.queue import ManagedTask

        huey.really_enqueue = Mock(side_effect=ConnectionError())

        with pytest.raises(ConnectionError):
            with transaction.manager:
                task = object()
                managed_task = ManagedTask(huey, task)
                managed_task.join_transaction()

        assert task not in huey.enqueued
