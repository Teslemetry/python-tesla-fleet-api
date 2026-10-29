"""Unit tests for the operation-mode setter.

``default_real_mode`` is a plain top-level string in ``config.json`` with no
scaling — verified on a Powerwall 3 gateway that a local v1r write of
``self_consumption`` / ``autonomous`` / ``backup`` sticks and reads back
verbatim.
"""

from __future__ import annotations

import pytest

from tesla_fleet_api.tesla.powerwall import OPERATION_MODES, PowerwallClient


def test_operation_modes_are_the_three_known_values() -> None:
    assert OPERATION_MODES == ("self_consumption", "autonomous", "backup")


@pytest.fixture
def client() -> tuple[PowerwallClient, list[dict]]:
    """A bare client (no transport/session) with write_config captured.

    ``set_operation_mode`` only calls ``self.write_config``, so we skip
    ``__init__`` (which would load an RSA key) and stub that one method.
    """
    pw = PowerwallClient.__new__(PowerwallClient)
    calls: list[dict] = []

    async def fake_write_config(updates: dict) -> None:
        calls.append(dict(updates))

    pw.write_config = fake_write_config  # type: ignore[method-assign]
    return pw, calls


@pytest.mark.parametrize("mode", ["self_consumption", "autonomous", "backup"])
async def test_set_operation_mode_writes_default_real_mode(
    client: tuple[PowerwallClient, list[dict]], mode: str
) -> None:
    pw, calls = client
    await pw.set_operation_mode(mode)
    assert calls == [{"default_real_mode": mode}]


@pytest.mark.parametrize("bad", ["", "Self_Consumption", "off", "selfconsumption"])
async def test_set_operation_mode_rejects_unknown(
    client: tuple[PowerwallClient, list[dict]], bad: str
) -> None:
    pw, calls = client
    with pytest.raises(ValueError):
        await pw.set_operation_mode(bad)
    assert calls == []
