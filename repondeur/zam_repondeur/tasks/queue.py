import logging
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional

import transaction
from huey.api import Huey, PeriodicTask, Task, TaskWrapper
from transaction.interfaces import IDataManager
from zope.interface import implementer

logger = logging.getLogger(__name__)


class State(Enum):
    INIT = 0
    NO_WORK = 1
    COMMITTED = 2
    ABORTED = 3
    TPC_NONE = 11
    TPC_BEGIN = 12
    TPC_VOTED = 13
    TPC_COMMITED = 14
    TPC_FINISHED = 15
    TPC_ABORTED = 16


class TransactionalHuey(Huey):
    """
    A huey task queue that tries to play well with transactions

    - allows enqueing tasks only if the whole transaction succeeds
    - runs each task inside an individual transaction in workers
    """

    def __init__(self, *, transactional_enqueue: bool = True, **kwargs: Any) -> None:
        """
        The `transactional_enqueue` parameter is kept as True for the webapp as
        we are in a context where the transaction is tied to the request but
        in case of a worker, we want the scheduler to issue it immediatly and
        thus set the parameter to False.
        """
        super().__init__(**kwargs)
        self.transactional_enqueue = transactional_enqueue

    def enqueue(self, task: Any) -> None:
        logger.debug("Enqueue task %r", task)

        # If we're in immediate mode (typically during tests), then we run the task now
        # (in the current transaction).
        if self.immediate:
            logger.debug("Executing task immediately")
            self.really_enqueue(task)
            return

        # Schedule the task immediately or when the transaction succeeds
        if self.transactional_enqueue:
            logger.debug(
                "Task will be scheduled for execution by a worker"
                " if the transaction succeeds"
            )
            managed_task = ManagedTask(self, task)
            managed_task.join_transaction()
        else:
            logger.debug("Enqueueing task immediately")
            self.really_enqueue(task)

    def really_enqueue(self, task: Any) -> None:
        super().enqueue(task)

    def task(
        self,
        retries: int = 0,
        retry_delay: int = 0,
        priority: Any = None,
        context: bool = False,
        name: Optional[str] = None,
        **kwargs: Any
    ) -> Callable:
        def decorator(func):  # type: ignore
            return TaskWrapper(
                self,
                self._transaction_wrapper(func),
                retries=retries,
                retry_delay=retry_delay,
                default_priority=priority,
                context=context,
                name=name,
                **kwargs
            )

        return decorator

    def periodic_task(
        self,
        validate_datetime: Callable,
        retries: int = 0,
        retry_delay: int = 0,
        priority: Any = None,
        context: bool = False,
        name: Optional[str] = None,
        **kwargs: Any
    ) -> Callable:
        def decorator(func):  # type: ignore
            def method_validate(self, timestamp):  # type: ignore
                return validate_datetime(timestamp)

            return TaskWrapper(
                self,
                self._transaction_wrapper(func),
                context=context,
                name=name,
                default_retries=retries,
                default_retry_delay=retry_delay,
                default_priority=priority,
                validate_datetime=method_validate,
                task_base=PeriodicTask,
                **kwargs
            )

        return decorator

    def _transaction_wrapper(self, func: Callable) -> Callable:
        if isinstance(func, TaskWrapper):
            func = func.func
        if not self.immediate:
            func = self.run_in_transaction(func)
        return func

    @staticmethod
    def run_in_transaction(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with transaction.manager:
                return func(*args, **kwargs)

        return wrapper


@implementer(IDataManager)
class ManagedTask:
    """
    A task that will only be scheduled if the current transaction is committed

    This class implements the Data Manager protocol

    See: https://transaction.readthedocs.io/

    Implementation inspired from repoze.sendmail package (used by pyramid_mailer).

    Limitations: really enqueuing the task is done in the "finish" phase of the
    two-phase commit protocol, so an error at this point could lead to inconsistent
    state. We try to mitigate this by doing a read access to the Huey storage (Redis)
    during the voting phase, which will detect connection errors.
    """

    def __init__(self, huey: Huey, task: Task, transaction_manager: Any = None) -> None:
        logger.debug("Creating managed task %r", task)
        self.huey = huey
        self.task = task
        if transaction_manager is None:
            transaction_manager = transaction.manager
        self.transaction_manager = transaction_manager
        self.transaction = None
        self.state = State.INIT
        self.tpc_phase = 0

    def join_transaction(self, trans: Any = None) -> None:
        """Join the object into a transaction.

        If no transaction is specified, use ``transaction.manager.get()``.

        Raise an error if the object is already in a different transaction.
        """
        if trans is not None:
            logger.debug("Joining transaction %r", trans)
        else:
            logger.debug("Joining current transaction")

        _before = self.transaction

        if trans is not None:
            _after = trans
        else:
            _after = self.transaction_manager.get()

        if _before is not None and _before is not _after:
            if self in _before._resources:
                raise ValueError(
                    "Item is in the former transaction. "
                    "It must be removed before it can be added "
                    "to a new transaction"
                )

        if self not in _after._resources:
            _after.join(self)

        self.transaction = _after

    def _finish(self, final_state: State) -> None:
        if self.transaction is None:
            raise ValueError("Not in a transaction")
        self.state = final_state
        self.tpc_phase = 0

    def commit(self, trans: Any) -> None:
        logger.debug("Committing transaction %r", trans)
        if self.transaction is None:
            raise ValueError("Not in a transaction")
        if self.transaction is not trans:
            raise ValueError("In a different transaction")
        # OK to call ``commit`` w/ TPC underway

    def abort(self, trans: Any) -> None:
        logger.debug("Aborting transaction %r", trans)
        if self.transaction is None:
            raise ValueError("Not in a transaction")
        if self.transaction is not trans:
            raise ValueError("In a different transaction")
        if self.tpc_phase != 0:
            raise ValueError("TPC in progress")

    def sortKey(self) -> str:
        return str(id(self))

    def tpc_begin(self, trans: Any, subtransaction: bool = False) -> None:
        logger.debug("Beginning TPC for transaction %r", trans)
        if self.transaction is None:
            raise ValueError("Not in a transaction")
        if self.transaction is not trans:
            raise ValueError("In a different transaction")
        if self.tpc_phase != 0:
            raise ValueError("TPC in progress")
        if subtransaction:
            raise ValueError("Subtransactions not supported")
        self.tpc_phase = 1

    def tpc_vote(self, trans: Any) -> None:
        logger.debug("Voting TPC for transaction %r", trans)
        if self.transaction is None:
            raise ValueError("Not in a transaction")
        if self.transaction is not trans:
            raise ValueError("In a different transaction")
        if self.tpc_phase != 1:
            raise ValueError("TPC phase error: %d" % self.tpc_phase)

        # Try to access Redis now so that we can detect a problem early
        self.huey.pending_count()

        self.tpc_phase = 2

    def tpc_finish(self, trans: Any) -> None:
        logger.debug("Finishing TPC for transaction %r", trans)
        if self.transaction is None:
            raise ValueError("Not in a transaction")
        if self.transaction is not trans:
            raise ValueError("In a different transaction")
        if self.tpc_phase != 2:
            raise ValueError("TPC phase error: %d" % self.tpc_phase)

        # That's where we really do the work
        self.huey.really_enqueue(self.task)

        self._finish(State.TPC_FINISHED)

    def tpc_abort(self, trans: Any) -> None:
        logger.debug("Aborting TPC for transaction %r", trans)
        if self.transaction is None:
            raise ValueError("Not in a transaction")
        if self.transaction is not trans:
            raise ValueError("In a different transaction")
        if self.tpc_phase == 0:
            raise ValueError("TPC phase error: %d" % self.tpc_phase)
        if self.state is State.TPC_FINISHED:
            raise ValueError("TPC already finished")
        self._finish(State.TPC_ABORTED)
