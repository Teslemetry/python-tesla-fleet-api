from __future__ import annotations

import inspect
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    TypeVar,
    Union,
)

from tesla_fleet_api.const import LOGGER

PrimaryT = TypeVar("PrimaryT")
FallbackT = TypeVar("FallbackT")

# A health check may be a static bool, a sync callable returning bool, or an
# async callable returning bool. When omitted the router derives a default from
# the primary instance (see ``_default_health``).
HealthCheck = Union[bool, Callable[[], bool], Callable[[], Awaitable[bool]]]


async def _maybe_await(value: Any) -> Any:
    """Await ``value`` if it is awaitable, otherwise return it unchanged."""
    if inspect.isawaitable(value):
        return await value
    return value


class VehicleRouter(Generic[PrimaryT, FallbackT]):
    """Routes method calls to a primary instance when healthy, else a fallback.

    Composes an ordered pair of vehicle instances that share a common method
    surface (e.g. a :class:`VehicleBluetooth` primary and a cloud
    :class:`VehicleFleet`/``TeslemetryVehicle`` fallback). Method calls are
    dispatched dynamically:

    - Present and callable on *both* -> the health check decides: primary when
      healthy, otherwise fallback.
    - Present only on the fallback -> the fallback is called (no health gate).
    - Present only on the primary -> the primary is called.
    - Present on neither -> :class:`AttributeError`.

    Non-callable attributes (e.g. ``vin``) resolve to the primary's value when
    present, otherwise the fallback's.

    The health check may be provided as a ``bool``, a sync callable, or an async
    callable returning ``bool``. When omitted, a default is derived from the
    primary that treats "can establish a Bluetooth connection" as healthy and
    routes to the fallback on any connection failure. The default feature-detects
    its health signal, so it is not hard-wired to Bluetooth: a primary without a
    recognised connection signal is simply treated as always healthy.

    The class is deliberately unbound over its two type parameters so the same
    pattern can later wrap a pair of energy site classes.
    """

    _primary: PrimaryT
    _fallback: FallbackT
    _health: HealthCheck | None

    def __init__(
        self,
        primary: PrimaryT,
        fallback: FallbackT,
        health: HealthCheck | None = None,
    ):
        self._primary = primary
        self._fallback = fallback
        self._health = health

    async def _default_health(self) -> bool:
        """Derive health from the primary by feature-detecting a connection signal.

        For a Bluetooth primary this attempts ``connect_if_needed()`` and treats a
        successful connection as healthy, returning ``False`` on any connection
        failure so calls route to the fallback. A primary exposing only a
        ``client.is_connected`` flag is judged by that flag. A primary with no
        recognised signal is treated as healthy.
        """
        connect_if_needed = getattr(self._primary, "connect_if_needed", None)
        if callable(connect_if_needed):
            try:
                await _maybe_await(connect_if_needed())
                return True
            except Exception as e:  # noqa: BLE001 - any connection failure -> fallback
                LOGGER.debug("Primary health check failed, routing to fallback: %s", e)
                return False

        client = getattr(self._primary, "client", None)
        if client is not None:
            return bool(getattr(client, "is_connected", False))

        return True

    async def is_healthy(self) -> bool:
        """Resolve the configured (or default) health check to a bool."""
        health = self._health
        if health is None:
            return await self._default_health()
        if isinstance(health, bool):
            return health
        return bool(await _maybe_await(health()))

    def _dispatch(
        self,
        name: str,
        primary_attr: Callable[..., Any],
        fallback_attr: Callable[..., Any],
    ) -> Callable[..., Awaitable[Any]]:
        """Build a health-gated async wrapper for a method on both instances."""

        async def _routed(*args: Any, **kwargs: Any) -> Any:
            if await self.is_healthy():
                return await _maybe_await(primary_attr(*args, **kwargs))
            return await _maybe_await(fallback_attr(*args, **kwargs))

        _routed.__name__ = name
        _routed.__qualname__ = f"{type(self).__name__}.{name}"
        return _routed

    def __getattr__(self, name: str) -> Any:
        # __getattr__ is only reached when normal lookup fails. Guard the private
        # attributes so an access before __init__ completes raises rather than
        # recursing infinitely through this method.
        if name in ("_primary", "_fallback", "_health"):
            raise AttributeError(name)

        primary = self._primary
        fallback = self._fallback
        has_primary = hasattr(primary, name)
        has_fallback = hasattr(fallback, name)

        if not has_primary and not has_fallback:
            raise AttributeError(
                f"{type(self).__name__!r} routes to neither primary "
                f"{type(primary).__name__!r} nor fallback "
                f"{type(fallback).__name__!r} for {name!r}"
            )

        primary_attr = getattr(primary, name) if has_primary else None
        fallback_attr = getattr(fallback, name) if has_fallback else None

        if (
            has_primary
            and has_fallback
            and callable(primary_attr)
            and callable(fallback_attr)
        ):
            return self._dispatch(name, primary_attr, fallback_attr)

        # Only one side has it (pure fall-through), or the shared attribute is not
        # callable. Prefer the primary's value when present.
        if has_primary:
            return primary_attr
        return fallback_attr

    @property
    def primary(self) -> PrimaryT:
        """The primary instance calls are routed to when healthy."""
        return self._primary

    @property
    def fallback(self) -> FallbackT:
        """The fallback instance calls are routed to when the primary is unhealthy."""
        return self._fallback
