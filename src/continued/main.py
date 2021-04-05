#!/usr/bin/env python3

from typing import Any, Callable

import functools

import trio
import trio_asyncio

from .gui import loop as gui_loop
from .journal import loop as journal_loop


def _trio_asyncio_wrapper(func: Callable) -> Callable:

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:

        async with trio_asyncio.open_loop():
            return await func(*args, **kwargs)

    return wrapper


@_trio_asyncio_wrapper
async def loop() -> None:

    async with trio.open_nursery() as nursery:

        loop_completed = await nursery.start(gui_loop)

        nursery.start_soon(journal_loop)

        await loop_completed.wait()

        nursery.cancel_scope.cancel()
