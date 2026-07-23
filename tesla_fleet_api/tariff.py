"""Pure, offline resolver for the Tesla Energy Tariff V2 (time-of-use) object.

Consumes the raw ``tariff_content_v2`` object as returned by
``EnergySite.site_info()`` (nested under ``tou_settings``) - there is no
typed model for it elsewhere in this library. Everything here is a pure
function over caller-supplied data: no I/O, no network, no vehicle/VPP
access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Mapping, cast

from tesla_fleet_api.exceptions import InvalidResponse

_MINUTES_PER_DAY = 24 * 60
_MINUTES_PER_WEEK = 7 * _MINUTES_PER_DAY


@dataclass(frozen=True, slots=True)
class TariffRate:
    """One side (buy or sell) of a resolved tariff rate.

    ``price`` is ``None`` only when the rate is genuinely unresolvable
    (missing from the tariff) - a real ``0.0`` price is returned as such.
    """

    price: float | None
    period_name: str | None
    season_name: str | None


@dataclass(frozen=True, slots=True)
class TariffPeriod:
    """One buy/sell rate pair in effect for ``[start, end)``."""

    start: datetime
    end: datetime
    buy: TariffRate
    sell: TariffRate


@dataclass(frozen=True, slots=True)
class TariffResolution:
    """The tariff rate in effect at the moment passed to :func:`get_tariff_periods`."""

    buy: TariffRate
    sell: TariffRate
    current_start: datetime
    next_change: datetime
    currency: str | None
    upcoming: list[TariffPeriod] | None


def unwrap_tariff_v2(response: Any) -> dict[str, Any]:
    """Extract the ``tariff_content_v2`` object from a raw API response.

    Accepts the ``site_info`` read envelope
    (``{"response": {"tariff_content_v2": {...}}}``), the
    ``time_of_use_settings`` write envelope
    (``{"tou_settings": {"tariff_content_v2": {...}}}``), or the bare
    ``tariff_content_v2`` object itself. Raises
    :class:`~tesla_fleet_api.exceptions.InvalidResponse` for a null body or
    any shape that doesn't carry a ``tariff_content_v2`` dict - a malformed
    body is not the same as "no tariff configured".
    """
    if response is None:
        raise InvalidResponse("tariff response body was null")
    if not isinstance(response, dict):
        raise InvalidResponse(repr(response))
    body = cast("dict[str, Any]", response)

    if "tariff_content_v2" in body:
        tariff = body["tariff_content_v2"]
        if isinstance(tariff, dict):
            return cast("dict[str, Any]", tariff)
        raise InvalidResponse(str(body))

    for envelope_key in ("response", "tou_settings"):
        if envelope_key in body:
            inner = body[envelope_key]
            if isinstance(inner, dict) and isinstance(
                cast("dict[str, Any]", inner).get("tariff_content_v2"), dict
            ):
                return cast(
                    "dict[str, Any]", cast("dict[str, Any]", inner)["tariff_content_v2"]
                )
            raise InvalidResponse(str(body))

    # No recognized envelope key present - treat the input as the bare
    # `tariff_content_v2` object itself.
    return body


def get_tariff_periods(
    tariff: Mapping[str, Any],
    now: datetime,
    *,
    horizon_hours: float | None = None,
) -> TariffResolution | None:
    """Resolve the buy/sell tariff rate in effect at ``now``.

    ``tariff`` is the already-unwrapped ``tariff_content_v2`` object (see
    :func:`unwrap_tariff_v2`). ``now`` must be timezone-aware and expressed
    in the site's own local timezone - the tariff object carries no
    timezone of its own, so a naive ``now`` would silently resolve against
    the wrong wall clock; this raises :class:`ValueError` instead.

    Returns ``None`` when no season in the tariff covers ``now``'s date.
    When ``horizon_hours`` is given, ``upcoming`` is populated with every
    buy/sell period between ``now`` and ``now + horizon_hours``.
    """
    if now.tzinfo is None or now.tzinfo.utcoffset(now) is None:
        raise ValueError("now must be timezone-aware")

    resolved = _resolve_at(tariff, now)
    if resolved is None:
        return None

    upcoming: list[TariffPeriod] | None = None
    if horizon_hours is not None:
        upcoming = []
        deadline = now + timedelta(hours=horizon_hours)
        cursor = resolved
        # Bounded defensively against a pathological tariff whose grid never
        # advances; real tariffs resolve a new boundary on every iteration.
        for _ in range(10_000):
            upcoming.append(
                TariffPeriod(
                    start=cursor.current_start,
                    end=cursor.next_change,
                    buy=cursor.buy,
                    sell=cursor.sell,
                )
            )
            if cursor.next_change >= deadline:
                break
            next_resolved = _resolve_at(tariff, cursor.next_change)
            if next_resolved is None:
                break
            cursor = next_resolved

    return TariffResolution(
        buy=resolved.buy,
        sell=resolved.sell,
        current_start=resolved.current_start,
        next_change=resolved.next_change,
        currency=tariff.get("currency"),
        upcoming=upcoming,
    )


@dataclass(frozen=True, slots=True)
class _Resolved:
    buy: TariffRate
    sell: TariffRate
    current_start: datetime
    next_change: datetime


def _resolve_at(tariff: Mapping[str, Any], moment: datetime) -> _Resolved | None:
    today = moment.date()
    now_mow = _minute_of_week(moment)

    buy_season_name, buy_windows, buy_season_dates = _season_windows(
        tariff.get("seasons"), today
    )
    if buy_season_name is None:
        return None
    buy_match = _match_window(buy_windows, now_mow)
    if buy_match is None:
        return None
    buy_period_name = buy_match[0]
    buy_rate = TariffRate(
        price=_lookup_price(
            tariff.get("energy_charges"), buy_season_name, buy_period_name
        ),
        period_name=buy_period_name,
        season_name=buy_season_name,
    )

    sell_rate = TariffRate(price=None, period_name=None, season_name=None)
    sell_windows: list[tuple[str, int, int]] = []
    sell_season_dates: tuple[date, date] | None = None
    sell_tariff = tariff.get("sell_tariff")
    if isinstance(sell_tariff, dict):
        sell_tariff = cast("dict[str, Any]", sell_tariff)
        sell_season_name, sell_windows, sell_season_dates = _season_windows(
            sell_tariff.get("seasons"), today
        )
        if sell_season_name is not None:
            sell_match = _match_window(sell_windows, now_mow)
            if sell_match is not None:
                sell_period_name = sell_match[0]
                sell_rate = TariffRate(
                    price=_lookup_price(
                        sell_tariff.get("energy_charges"),
                        sell_season_name,
                        sell_period_name,
                    ),
                    period_name=sell_period_name,
                    season_name=sell_season_name,
                )

    starts = [start for _, start, _ in buy_windows] + [
        start for _, start, _ in sell_windows
    ]
    since_delta, until_delta = _bracket(now_mow, starts)

    moment_floor = moment.replace(second=0, microsecond=0)
    current_start = moment_floor - timedelta(minutes=since_delta)
    next_change = moment_floor + timedelta(minutes=until_delta)
    for season_dates in (buy_season_dates, sell_season_dates):
        if season_dates is None:
            continue
        season_start, season_end = (
            datetime.combine(boundary, datetime.min.time(), tzinfo=moment.tzinfo)
            for boundary in season_dates
        )
        current_start = max(current_start, season_start)
        next_change = min(next_change, season_end)

    return _Resolved(
        buy=buy_rate,
        sell=sell_rate,
        current_start=current_start,
        next_change=next_change,
    )


def _minute_of_week(moment: datetime) -> int:
    """Monday 00:00 = 0 .. Sunday 23:59 = 10079, matching ``datetime.weekday()``."""
    return moment.weekday() * _MINUTES_PER_DAY + moment.hour * 60 + moment.minute


def _as_int(value: Any, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _season_covers(season: Mapping[str, Any], today: date) -> bool:
    from_month = season.get("fromMonth")
    from_day = season.get("fromDay")
    to_month = season.get("toMonth")
    to_day = season.get("toDay")
    if from_month is None or from_day is None or to_month is None or to_day is None:
        return False
    start = (_as_int(from_month, 0), _as_int(from_day, 0))
    end = (_as_int(to_month, 0), _as_int(to_day, 0))
    point = (today.month, today.day)
    if start <= end:
        return start <= point <= end
    # Year-crossing season (e.g. October -> March).
    return point >= start or point <= end


def _season_windows(
    seasons: Any, today: date
) -> tuple[str | None, list[tuple[str, int, int]], tuple[date, date] | None]:
    """Find the season covering ``today`` and expand its period grid.

    Skips seasons with no ``tou_periods`` (an empty ``{}`` season object is
    legal and present in real tariffs, e.g. an unused "Winter").
    """
    if not isinstance(seasons, dict):
        return None, [], None
    for name, season in cast("dict[str, Any]", seasons).items():
        if not isinstance(season, dict):
            continue
        season = cast("dict[str, Any]", season)
        periods = season.get("tou_periods")
        if not isinstance(periods, dict) or not periods:
            continue
        if _season_covers(season, today):
            return (
                name,
                _expand_periods(cast("dict[str, Any]", periods)),
                _season_dates(season, today),
            )
    return None, [], None


def _season_dates(season: Mapping[str, Any], today: date) -> tuple[date, date]:
    start_month = _as_int(season.get("fromMonth"), 0)
    start_day = _as_int(season.get("fromDay"), 0)
    end_month = _as_int(season.get("toMonth"), 0)
    end_day = _as_int(season.get("toDay"), 0)
    start_fields = (start_month, start_day)
    end_fields = (end_month, end_day)

    if start_fields <= end_fields:
        start_year = end_year = today.year
    elif (today.month, today.day) >= start_fields:
        start_year, end_year = today.year, today.year + 1
    else:
        start_year, end_year = today.year - 1, today.year

    start = date(start_year, start_month, start_day)
    end = date(end_year, end_month, end_day) + timedelta(days=1)
    return start, end


def _expand_periods(tou_periods: Mapping[str, Any]) -> list[tuple[str, int, int]]:
    windows: list[tuple[str, int, int]] = []
    for period_name, period_obj in tou_periods.items():
        if not isinstance(period_obj, dict):
            continue
        entries = cast("dict[str, Any]", period_obj).get("periods")
        if not isinstance(entries, list):
            continue
        for entry in cast("list[Any]", entries):
            if isinstance(entry, dict):
                windows.extend(
                    _expand_entry(period_name, cast("dict[str, Any]", entry))
                )
    return windows


def _expand_entry(
    period_name: str, entry: Mapping[str, Any]
) -> list[tuple[str, int, int]]:
    """Expand one ``periods[]`` entry into a (name, start, end) minute-of-week
    window per day-of-week it applies to.

    Missing fields default per the observed wire format:
    ``fromDayOfWeek``/``fromHour``/``fromMinute`` -> 0, ``toDayOfWeek`` -> 6.
    ``toHour: 24`` / ``toMinute: 60`` occur in real tariffs and mean "next
    midnight" - plain minute-of-day arithmetic rolls them into the next day
    without ever constructing an invalid ``datetime(hour=24)``.
    """
    from_dow = _as_int(entry.get("fromDayOfWeek"), 0)
    to_dow = _as_int(entry.get("toDayOfWeek"), 6)
    from_hour = _as_int(entry.get("fromHour"), 0)
    from_minute = _as_int(entry.get("fromMinute"), 0)
    to_hour = _as_int(entry.get("toHour"), 0)
    to_minute = _as_int(entry.get("toMinute"), 0)

    if from_dow <= to_dow:
        days = list(range(from_dow, to_dow + 1))
    else:
        days = [*range(from_dow, 7), *range(0, to_dow + 1)]

    windows: list[tuple[str, int, int]] = []
    for day in days:
        start = day * _MINUTES_PER_DAY + from_hour * 60 + from_minute
        end = day * _MINUTES_PER_DAY + to_hour * 60 + to_minute
        if end <= start:
            end += _MINUTES_PER_DAY
        windows.append((period_name, start, end))
    return windows


def _window_contains(now_mow: int, start: int, duration: int) -> bool:
    start_mod = start % _MINUTES_PER_WEEK
    end = start_mod + duration
    if start_mod <= now_mow < end:
        return True
    # Week-boundary wrap: a window ending after Sunday midnight is also
    # "this week's" window one week earlier.
    return start_mod <= now_mow + _MINUTES_PER_WEEK < end


def _match_window(
    windows: list[tuple[str, int, int]], now_mow: int
) -> tuple[str, int, int] | None:
    for name, start, end in windows:
        if _window_contains(now_mow, start, end - start):
            return name, start, end
    return None


def _bracket(now_mow: int, starts: list[int]) -> tuple[int, int]:
    """Return (minutes since the most recent boundary, minutes to the next
    strictly-future boundary) across every period-start in ``starts``."""
    mods = sorted({s % _MINUTES_PER_WEEK for s in starts})
    if not mods:
        return 0, _MINUTES_PER_WEEK

    since = _MINUTES_PER_WEEK
    until = _MINUTES_PER_WEEK
    for boundary in mods:
        d_since = now_mow - boundary
        if d_since < 0:
            d_since += _MINUTES_PER_WEEK
        since = min(since, d_since)

        d_until = boundary - now_mow
        if d_until <= 0:
            d_until += _MINUTES_PER_WEEK
        until = min(until, d_until)
    return since, until


def _lookup_price(charges: Any, season_name: str, period_name: str) -> float | None:
    """``charges[season].rates[period]`` with ``season``/``period`` -> ``"ALL"`` fallback.

    Uses key-presence checks throughout, never truthiness - a legal ``0.0``
    price must never be treated as missing.
    """
    if not isinstance(charges, dict):
        return None
    charges = cast("dict[str, Any]", charges)
    rates: dict[str, Any] | None = None
    for key in (season_name, "ALL"):
        block = charges.get(key)
        if isinstance(block, dict) and isinstance(
            cast("dict[str, Any]", block).get("rates"), dict
        ):
            rates = cast("dict[str, Any]", cast("dict[str, Any]", block)["rates"])
            break
    if rates is None:
        return None
    for key in (period_name, "ALL"):
        if key in rates:
            try:
                return float(rates[key])
            except (TypeError, ValueError):
                return None
    return None
