"""Unit tests for the time-of-use mode setter.

``strategy.TOU_mode`` is a **local-only** string (not exposed by the Tesla
Fleet API). The gateway does not validate it — verified on a Powerwall 3 that a
write of an arbitrary string persists verbatim — so ``set_tou_mode`` is an
intentional pass-through that only guards against an empty/non-string value.
``"economic"`` is the one value confirmed in use.
"""

from __future__ import annotations

import pytest

from tesla_fleet_api.tesla.powerwall import PowerwallClient


@pytest.fixture
def client() -> tuple[PowerwallClient, list[dict]]:
    """A bare client (no transport/session) with write_config captured."""
    pw = PowerwallClient.__new__(PowerwallClient)
    calls: list[dict] = []

    async def fake_write_config(updates: dict) -> None:
        calls.append(dict(updates))

    pw.write_config = fake_write_config  # type: ignore[method-assign]
    return pw, calls


@pytest.mark.parametrize("mode", ["economic", "balanced", "self_consumption"])
async def test_set_tou_mode_passes_string_through(
    client: tuple[PowerwallClient, list[dict]], mode: str
) -> None:
    # Pass-through by design: the gateway itself does not validate the value.
    pw, calls = client
    await pw.set_tou_mode(mode)
    assert calls == [{"strategy.TOU_mode": mode}]


@pytest.mark.parametrize("bad", ["", None, 123])
async def test_set_tou_mode_rejects_empty_or_non_string(
    client: tuple[PowerwallClient, list[dict]], bad: object
) -> None:
    pw, calls = client
    with pytest.raises(ValueError):
        await pw.set_tou_mode(bad)  # type: ignore[arg-type]
    assert calls == []
