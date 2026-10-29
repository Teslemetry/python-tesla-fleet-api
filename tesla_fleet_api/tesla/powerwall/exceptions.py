"""Typed exceptions raised by aiopowerwall."""

from __future__ import annotations


class PowerwallError(Exception):
    """Base class for all aiopowerwall errors."""


class PowerwallConnectionError(PowerwallError):
    """The Powerwall gateway could not be reached or the request timed out."""

    # tesla_fleet_api's Router fails over to the next backend only on errors
    # marked failover-safe: the local gateway gave no usable answer.
    failover_safe = True


class PowerwallAuthenticationError(PowerwallError):
    """Authentication with the Powerwall failed.

    Raised for HTTP 401/403 from `/api/login/Basic` or for v1r message faults
    that indicate an unregistered or inactive RSA key.
    """

    # tesla_fleet_api's Router fails over to the next backend only on errors
    # marked failover-safe: the local gateway gave no usable answer.
    failover_safe = True


class PowerwallRateLimitError(PowerwallError):
    """The Powerwall returned 429/503 — back off before retrying."""

    # tesla_fleet_api's Router fails over to the next backend only on errors
    # marked failover-safe: the local gateway gave no usable answer.
    failover_safe = True


class PowerwallProtocolError(PowerwallError):
    """The Powerwall returned an unexpected response (bad protobuf, JSON, etc.)."""


class PowerwallFaultError(PowerwallError):
    """A signed v1r request returned a non-NONE message_fault.

    The fault enum name is exposed via :pyattr:`fault`.
    """

    def __init__(self, fault: str, message: str | None = None) -> None:
        self.fault = fault
        super().__init__(message or f"Powerwall returned message fault: {fault}")


class PowerwallCommandError(PowerwallProtocolError):
    """The gateway answered a v1r command with an error status.

    The reply carried ``common.error_response`` (a ``google.rpc.Status``) in
    place of the expected response. The status code and message are exposed
    via :pyattr:`code` and :pyattr:`status_message`.
    """

    def __init__(self, command: str, code: int, status_message: str) -> None:
        self.command = command
        self.code = code
        self.status_message = status_message
        super().__init__(
            f"Powerwall rejected {command}: {status_message or 'no message'} "
            f"(status code {code})"
        )


class PowerwallNotSupportedError(PowerwallCommandError):
    """The gateway firmware does not implement the requested v1r command.

    Raised for status code 12 (``UNIMPLEMENTED``).
    """
