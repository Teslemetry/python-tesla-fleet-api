"""Island-mode rules shared by the cloud energy sites and the local Powerwall.

Both paths reach the same grid contactor, so they share one list of refusal
codes and one check of the mode.
"""

from __future__ import annotations

from typing import Any, Final

from tesla_protocol.energy_device import teg_api_pb2

# The two setIslandModeRequest modes that move the contactor: 1 closes it
# (on-grid) and 6 opens it (off-grid). Mode 2 was seen to set a preference
# without moving the contactor; no other mode has a known meaning.
ISLAND_MODES: Final = frozenset({1, 6})

# TEGSetIslandModeResult values meaning the gateway refused the request.
SET_ISLAND_MODE_REJECTIONS: Final = frozenset(
    {
        teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_NOT_READY_FOR_ISLANDING,
        teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_LOAD_DROP_EXPECTED,
        teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_LOW_ENERGY,
        teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_EXCESSIVE_SOLAR,
    }
)


def validate_island_mode(mode: Any, force: Any = None) -> None:
    """Raise ``ValueError`` unless ``mode`` is 1 or 6 and ``force`` is a bool or ``None``.

    There is no coercion: ``"6"``, ``6.0``, ``True`` and ``None`` all raise,
    so a malformed call can never close the contactor when the caller meant
    to open it.
    """
    if type(mode) is bool or not isinstance(mode, int) or mode not in ISLAND_MODES:
        raise ValueError(
            "mode must be EnergyIslandMode.ON_GRID (1) or EnergyIslandMode.OFF_GRID (6)"
        )
    if force is not None and type(force) is not bool:
        raise ValueError("force must be a bool")


def island_mode_rejection(result: Any) -> tuple[int, str] | None:
    """The ``(code, name)`` of a ``REJECTED_*`` result, or ``None`` for anything else.

    Takes the enum's number or its name, because a JSON route may carry
    either. ``ACCEPTED``, ``INVALID`` and values this ``tesla-protocol`` does
    not know return ``None`` rather than being guessed at.
    """
    for code in SET_ISLAND_MODE_REJECTIONS:
        name = teg_api_pb2.TEGSetIslandModeResult.Name(code)
        if (type(result) is int and result == code) or result == name:
            return code, name
    return None
