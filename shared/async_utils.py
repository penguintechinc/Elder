"""Async utility functions for Elder application.

Provides helpers for running blocking PyDAL operations in async context using thread pools.
Python 3.12 optimizations with asyncio TaskGroups for structured concurrency.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Callable, Any, TypeVar, ParamSpec

# Thread pool for blocking operations (PyDAL database calls)
_executor = ThreadPoolExecutor(max_workers=20, thread_name_prefix="pydal_")

# Type hints for better IDE support
P = ParamSpec('P')
T = TypeVar('T')


async def run_in_threadpool(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """
    Run a blocking function in the thread pool.

    This is essential for PyDAL operations since PyDAL is synchronous but we want
    to use async Flask endpoints for better concurrency.

    Args:
        func: The blocking function to run
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call

    Example:
        >>> db = current_app.db
        >>> count = await run_in_threadpool(lambda: db(db.organizations).count())
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, lambda: func(*args, **kwargs))


def to_thread(func: Callable[P, T]) -> Callable[P, asyncio.Task[T]]:
    """
    Decorator to automatically run a sync function in a thread pool.

    Use this to wrap blocking database operations for async endpoints.

    Example:
        >>> @to_thread
        >>> def get_user_count(db):
        >>>     return db(db.identities).count()
        >>>
        >>> count = await get_user_count(db)
    """
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await run_in_threadpool(func, *args, **kwargs)
    return wrapper


async def run_parallel(*tasks) -> list[Any]:
    """
    Run multiple async tasks in parallel and return all results.

    Uses asyncio.gather for simple parallel execution.

    Args:
        *tasks: Async tasks to run in parallel

    Returns:
        List of results in the same order as tasks

    Example:
        >>> count_task = run_in_threadpool(lambda: db(db.organizations).count())
        >>> rows_task = run_in_threadpool(lambda: db(db.organizations).select())
        >>> count, rows = await run_parallel(count_task, rows_task)
    """
    return await asyncio.gather(*tasks)


class AsyncTaskGroup:
    """
    Python 3.12 asyncio TaskGroup wrapper for structured concurrency.

    Provides better error handling and automatic task cancellation on exceptions.

    Example:
        >>> async with AsyncTaskGroup() as tg:
        >>>     count_task = tg.create_task(
        >>>         run_in_threadpool(lambda: db(db.organizations).count())
        >>>     )
        >>>     rows_task = tg.create_task(
        >>>         run_in_threadpool(lambda: db(db.organizations).select())
        >>>     )
        >>> count = count_task.result()
        >>> rows = rows_task.result()
    """

    def __init__(self):
        self._tg = None

    async def __aenter__(self):
        self._tg = asyncio.TaskGroup()
        return await self._tg.__aenter__()

    async def __aexit__(self, *args):
        return await self._tg.__aexit__(*args)


async def batch_execute(items: list, func: Callable, batch_size: int = 10) -> list:
    """
    Execute a function on a list of items in batches.

    Useful for bulk operations that shouldn't overwhelm the thread pool.

    Args:
        items: List of items to process
        func: Async function to call for each item
        batch_size: Number of items to process concurrently

    Returns:
        List of results in the same order as items

    Example:
        >>> async def fetch_entity(entity_id):
        >>>     return await run_in_threadpool(lambda: db.entities[entity_id])
        >>>
        >>> entity_ids = [1, 2, 3, 4, 5]
        >>> entities = await batch_execute(entity_ids, fetch_entity, batch_size=2)
    """
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await asyncio.gather(*[func(item) for item in batch])
        results.extend(batch_results)
    return results


def shutdown_thread_pool():
    """
    Gracefully shutdown the thread pool.

    Call this during application shutdown to clean up threads.
    """
    _executor.shutdown(wait=True)
