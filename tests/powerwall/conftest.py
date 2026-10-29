"""Run the coroutine tests moved from aiopowerwall without pytest-asyncio."""

import asyncio
import inspect

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    """Run an ``async def`` test in a fresh event loop."""
    if not inspect.iscoroutinefunction(pyfuncitem.obj):
        return None
    funcargs = pyfuncitem.funcargs
    kwargs = {name: funcargs[name] for name in pyfuncitem._fixtureinfo.argnames}
    asyncio.run(pyfuncitem.obj(**kwargs))
    return True
