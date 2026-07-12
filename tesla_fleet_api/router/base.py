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
from tesla_fleet_api.exceptions import BluetoothUnconfirmedCommand, TeslaFleetError

PrimaryT = TypeVar("PrimaryT")
SecondaryT = TypeVar("SecondaryT")

# A health check may be a static bool, a sync callable returning bool, or an
# async callable returning bool. When omitted the router attempts the primary
# directly and fails over to the next backend on exception (no up-front probe).
HealthCheck = Union[bool, Callable[[], bool], Callable[[], Awaitable[bool]]]


async def _maybe_await(value: Any) -> Any:
    """Await ``value`` if it is awaitable, otherwise return it unchanged."""
    if inspect.isawaitable(value):
        return await value
    return value


class Router(Generic[PrimaryT, SecondaryT]):
    """Routes method calls across an ordered list of backends, tried in order.

    Composes two or more instances that share a common method surface (e.g. a
    :class:`VehicleBluetooth` primary and a cloud ``TeslemetryVehicle`` secondary,
    or a local energy site and a cloud ``TeslemetryEnergySite`` secondary). The
    first two backends are the required *primary* and *secondary*; any number of
    additional backends may follow and are tried, in order, after them. Method
    calls are dispatched dynamically:

    - Present and callable on one or more backends -> the first such backend (in
      order) is attempted (the first backend subject to an optional health check)
      with automatic failover down the chain to the remaining backends that also
      have the method.
    - Present on no backend -> :class:`AttributeError`.

    Non-callable attributes (e.g. ``vin``) resolve to the value of the first
    backend that has them.

    Dispatch to a callable performs *per-command* failover: the backends that
    expose the method are attempted in order, and if one raises any exception
    other than ``BluetoothUnconfirmedCommand`` (a connection failure or a
    provably pre-submission transport error such as notify setup or GATT
    characteristic resolution failure), the same call is automatically retried
    on the next backend that has it, with the same arguments. The error only
    propagates when every applicable backend fails, in which case the last error
    is raised. Each attempted backend emits a ``DEBUG`` log line with the routed
    command name, backend class, and success/error result.

    .. warning::

        Because a failed call is replayed on the next backend, a
        *non-idempotent* command (e.g. ``honk_horn``, ``actuate_trunk``,
        ``door_unlock``, ``charge_start``) that fails *mid-flight* — after a
        backend may have already partially applied it — can be **double-executed**
        (or executed more than once across a longer chain) when it is retried on
        the next backend. This is an accepted, deliberate tradeoff of per-command
        failover. Callers that need exactly-once semantics for non-idempotent
        commands should gate dispatch with an explicit health check (so a failing
        primary skips the primary entirely rather than replaying down the chain)
        or call the underlying backends directly.

    ``BluetoothUnconfirmedCommand`` (a lost ack for a mutating BLE command
    already written to the vehicle - see that exception's docstring) is the
    one exception per-command failover deliberately does **not** replay: the
    command may already have executed, so trying the next backend would risk
    double-executing it. It propagates to the caller unchanged instead of
    triggering failover, on any backend in the chain.

    The health check may be provided as a ``bool``, a sync callable, or an async
    callable returning ``bool``. It gates **only the first backend** (the
    primary): when an explicit check evaluates ``False`` the primary is skipped
    entirely and the call routes to the remaining backends; when it evaluates
    ``True`` the primary is attempted with the same fall-through-on-exception
    behaviour. When omitted (the default) the primary is attempted directly with
    fall-through-on-exception and no up-front probe. Backends after the primary
    are always reached purely through per-command failover — there is deliberately
    no per-backend health matrix.

    Dispatch is implemented via :meth:`__getattr__`, which does **not** proxy
    special/dunder methods (Python looks those up on the type, not the instance).
    In particular ``async with Router(...)`` does *not* enter a backend's async
    context manager, so a :class:`VehicleBluetooth` primary's BLE connection
    lifecycle (``__aenter__``/``__aexit__``) is not managed by the router — its
    commands still auto-connect on send, but explicit connect/disconnect must be
    done by reaching through :attr:`primary` (or :attr:`backends`).

    The class is deliberately unbound over its two type parameters and
    entity-agnostic so the same pattern can wrap vehicles or energy sites; the
    :class:`VehicleRouter` and :class:`EnergySiteRouter` subclasses are thin
    entity-specific names over it.
    """

    _backends: tuple[Any, ...]
    _health: HealthCheck | None

    def __init__(
        self,
        primary: PrimaryT,
        secondary: SecondaryT,
        *more_backends: Any,
        health: HealthCheck | None = None,
    ):
        # The two-argument ``Router(primary, secondary, health=...)`` form is
        # preserved exactly; additional positional backends extend the chain.
        self._backends = (primary, secondary, *more_backends)
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
        targets: list[tuple[Any, Callable[..., Any]]],
    ) -> Callable[..., Awaitable[Any]]:
        """Build an async wrapper with per-command failover down ``targets``.

        ``targets`` is the ordered list of ``(backend, callable_attr)`` pairs for
        every backend that exposes ``name`` as a callable.
        """

        async def _routed(*args: Any, **kwargs: Any) -> Any:
            start = 0
            # The health check gates only the primary, and only when there is
            # another backend to route to. ``targets[0]`` is the primary iff the
            # primary itself exposes this method.
            if (
                self._health is not None
                and len(targets) > 1
                and targets[0][0] is self._backends[0]
                and not await self.is_healthy()
            ):
                start = 1

            last_exc: BaseException | None = None
            for backend, attr in targets[start:]:
                try:
                    result = await _maybe_await(attr(*args, **kwargs))
                except BluetoothUnconfirmedCommand as e:
                    # The command may have already executed on this backend;
                    # replaying it on the next one risks double-executing it.
                    # Surface the ambiguity to the caller instead of failing over.
                    LOGGER.debug(
                        "command=%s backend=%s result=unconfirmed error=%s: %s",
                        name,
                        type(backend).__name__,
                        type(e).__name__,
                        e,
                    )
                    raise
                except (Exception, TeslaFleetError) as e:  # noqa: BLE001 - any failure -> next backend
                    last_exc = e
                    LOGGER.debug(
                        "command=%s backend=%s result=error error=%s: %s",
                        name,
                        type(backend).__name__,
                        type(e).__name__,
                        e,
                    )
                    continue
                LOGGER.debug(
                    "command=%s backend=%s result=success", name, type(backend).__name__
                )
                return result
            # The loop always runs at least once (``start`` only advances past
            # the primary when a later backend remains), so a failure here means
            # every applicable backend raised.
            assert last_exc is not None
            raise last_exc

        _routed.__name__ = name
        _routed.__qualname__ = f"{type(self).__name__}.{name}"
        return _routed

    def __getattr__(self, name: str) -> Any:
        # __getattr__ is only reached when normal lookup fails. Guard the private
        # attributes so an access before __init__ completes raises rather than
        # recursing infinitely through this method.
        if name in ("_backends", "_health"):
            raise AttributeError(name)

        backends = self._backends
        having = [b for b in backends if hasattr(b, name)]

        if not having:
            raise AttributeError(
                f"{type(self).__name__!r} routes to none of its "
                f"{len(backends)} backends "
                f"({', '.join(type(b).__name__ for b in backends)}) for {name!r}"
            )

        # Non-callable attributes resolve to the first backend that has them.
        first_attr = getattr(having[0], name)
        if not callable(first_attr):
            return first_attr

        targets = [(b, attr) for b in having if callable(attr := getattr(b, name))]
        return self._dispatch(name, targets)

    @property
    def backends(self) -> tuple[Any, ...]:
        """The ordered backends calls are routed across."""
        return self._backends

    @property
    def primary(self) -> PrimaryT:
        """The primary instance calls are routed to when healthy."""
        return self._backends[0]

    @property
    def secondary(self) -> SecondaryT:
        """The second backend, tried when the primary is unhealthy or fails."""
        return self._backends[1]
