"""Shared utility helpers."""


def _parse_firmware(version: str) -> tuple[int, ...] | None:
    """Parse a dotted numeric firmware string, or None if it doesn't parse."""
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError:
        return None


def firmware_compare(a: str, b: str) -> int:
    """Compare two Tesla firmware versions.

    Tesla firmware versions are dotted, numeric, and week-based (e.g.
    ``2025.14.3``), so comparing them as plain strings misorders results:
    ``"2025.10" < "2025.9"`` as strings, even though ``2025.10`` is the newer
    release. This compares the dotted numeric components pairwise instead.

    Returns 1 if ``a`` is ahead of ``b``, -1 if ``a`` is behind ``b``, and 0
    if they are equal. Versions with fewer components than the other are
    right-padded with zeros, so ``"2024.26"`` compares equal to
    ``"2024.26.0"`` and behind ``"2024.26.25"``. A firmware string that
    doesn't parse as dotted integers (e.g. ``"Unknown"``) sorts behind any
    parseable version, and equal to another unparseable string.
    """
    a_parts = _parse_firmware(a)
    b_parts = _parse_firmware(b)
    if a_parts is None or b_parts is None:
        if a_parts is None and b_parts is None:
            return 0
        return -1 if a_parts is None else 1
    length = max(len(a_parts), len(b_parts))
    a_parts += (0,) * (length - len(a_parts))
    b_parts += (0,) * (length - len(b_parts))
    if a_parts < b_parts:
        return -1
    if a_parts > b_parts:
        return 1
    return 0


def firmware_at_least(firmware: str, minimum: str) -> bool:
    """Return True if a Tesla firmware version is at least a minimum version.

    Thin wrapper around :func:`firmware_compare` for the common "does this
    vehicle's firmware support feature X" check. See ``firmware_compare`` for
    the comparison semantics, including how partial versions and unparseable
    strings (e.g. ``"Unknown"``) are handled.
    """
    return firmware_compare(firmware, minimum) >= 0
