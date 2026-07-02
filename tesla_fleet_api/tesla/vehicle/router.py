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
from tesla_fleet_api.exceptions import TeslaFleetError

PrimaryT = TypeVar("PrimaryT")
FallbackT = TypeVar("FallbackT")

# A health check may be a static bool, a sync callable returning bool, or an
# async callable returning bool. When omitted the router attempts the primary
# directly and fails over to the fallback on exception (no up-front probe).
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

    - Present and callable on *both* -> the primary is attempted (subject to an
      explicit health check) with automatic failover to the fallback.
    - Present only on the fallback -> the fallback is called (no health gate).
    - Present only on the primary -> the primary is called.
    - Present on neither -> :class:`AttributeError`.

    Non-callable attributes (e.g. ``vin``) resolve to the primary's value when
    present, otherwise the fallback's.

    Dispatch to a both-present callable performs *per-command* failover: the
    primary is attempted first and, if it raises any exception (a connection
    failure or a mid-command transport error such as a write/notify failure or a
    disconnect), the same call is automatically retried on the fallback with the
    same arguments. The error only propagates when the fallback also fails.

    .. warning::

        Because a failed primary call is replayed on the fallback, a
        *non-idempotent* command (e.g. ``honk_horn``, ``actuate_trunk``,
        ``door_unlock``, ``charge_start``) that fails *mid-flight* — after the
        primary may have already partially applied it — can be **double-executed**
        when it is retried on the fallback. This is an accepted, deliberate
        tradeoff of per-command failover. Callers that need exactly-once
        semantics for non-idempotent commands should gate dispatch with an
        explicit health check (so a failing primary skips the primary entirely
        rather than replaying on the fallback) or call the underlying
        :attr:`primary`/:attr:`fallback` instances directly.

    The health check may be provided as a ``bool``, a sync callable, or an async
    callable returning ``bool``. When an explicit check evaluates ``False`` the
    primary is skipped entirely and the call routes straight to the fallback;
    when it evaluates ``True`` the primary is attempted with the same
    fall-back-on-exception behaviour. When omitted (the default) the primary is
    attempted directly with fall-back-on-exception and no up-front probe.

    Dispatch is implemented via :meth:`__getattr__`, which does **not** proxy
    special/dunder methods (Python looks those up on the type, not the instance).
    In particular ``async with VehicleRouter(...)`` does *not* enter the primary's
    async context manager, so a :class:`VehicleBluetooth` primary's BLE connection
    lifecycle (``__aenter__``/``__aexit__``) is not managed by the router — its
    commands still auto-connect on send, but explicit connect/disconnect must be
    done by reaching through :attr:`primary`.

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

    async def is_healthy(self) -> bool:
        """Resolve an explicit health check to a bool.

        When no explicit check is configured the router does not probe up front —
        it attempts the primary and fails over on exception — so this reports
        ``True`` in that case.
        """
        health = self._health
        if health is None:
            return True
        if isinstance(health, bool):
            return health
        return bool(await _maybe_await(health()))

    def _dispatch(
        self,
        name: str,
        primary_attr: Callable[..., Any],
        fallback_attr: Callable[..., Any],
    ) -> Callable[..., Awaitable[Any]]:
        """Build an async wrapper with per-command failover for a shared method."""

        async def _routed(*args: Any, **kwargs: Any) -> Any:
            if self._health is not None and not await self.is_healthy():
                return await _maybe_await(fallback_attr(*args, **kwargs))
            try:
                return await _maybe_await(primary_attr(*args, **kwargs))
            except (Exception, TeslaFleetError) as e:  # noqa: BLE001 - any primary failure -> fallback
                LOGGER.debug("Primary call %r failed, routing to fallback: %s", name, e)
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
