"""Tests for :mod:`tesla_fleet_api.tariff`, the pure Tariff V2 rate resolver.

``tests/fixtures/tariff_v2_sample.json`` is a live-shaped Tariff V2 capture
(48 half-hour buy/sell periods, one covering the whole year) modeled on a
real captured tariff, including its two real anomalies:
``toHour: 24`` on the last period of the day, and an empty ``"Winter": {}``
season object. The Home Assistant reference this design ports matching logic
from crashes on the ``toHour: 24`` case (``base_day.replace(hour=24)``); the
regression test below locks in that this resolver does not.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest import TestCase
from zoneinfo import ZoneInfo

from tesla_fleet_api.exceptions import InvalidResponse
from tesla_fleet_api.tariff import get_tariff_periods, unwrap_tariff_v2

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "tariff_v2_sample.json"
TZ = ZoneInfo("Australia/Brisbane")


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def _fixture_tariff() -> dict:
    return copy.deepcopy(unwrap_tariff_v2(_load_fixture()))


class UnwrapTariffV2Tests(TestCase):
    def test_site_info_envelope(self):
        response = _load_fixture()
        tariff = unwrap_tariff_v2(response)
        self.assertEqual(tariff["code"], "POWER_SYNC:FLOW_POWER")

    def test_time_of_use_settings_envelope(self):
        tariff = _fixture_tariff()
        response = {"tou_settings": {"tariff_content_v2": tariff}}
        self.assertEqual(unwrap_tariff_v2(response), tariff)

    def test_bare_object(self):
        tariff = _fixture_tariff()
        self.assertEqual(unwrap_tariff_v2(tariff), tariff)

    def test_null_body_raises(self):
        with self.assertRaises(InvalidResponse):
            unwrap_tariff_v2(None)

    def test_malformed_shape_raises(self):
        with self.assertRaises(InvalidResponse):
            unwrap_tariff_v2({"response": {"nope": True}})


class FixtureTests(TestCase):
    """Cover the live-shaped fixture's own anomalies."""

    def setUp(self):
        self.tariff = _fixture_tariff()

    def test_toHour_24_end_of_day_resolves_and_does_not_crash(self):
        # 23:45 Monday falls in PERIOD_23_30 (23:30 -> 24:00), the exact
        # entry the HA reference crashes on via `base_day.replace(hour=24)`.
        now = datetime(2026, 7, 20, 23, 45, tzinfo=TZ)
        result = get_tariff_periods(self.tariff, now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.period_name, "PERIOD_23_30")
        # The period rolls into next-day midnight.
        self.assertEqual(
            result.next_change,
            now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1),
        )

    def test_zero_sell_price_is_real_not_missing(self):
        now = datetime(2026, 7, 20, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(self.tariff, now)
        self.assertIsNotNone(result)
        self.assertEqual(result.sell.price, 0.0)
        self.assertIsNotNone(result.sell.period_name)

    def test_nonzero_sell_price_evening_peak(self):
        now = datetime(2026, 7, 20, 17, 45, tzinfo=TZ)
        result = get_tariff_periods(self.tariff, now)
        self.assertIsNotNone(result)
        self.assertEqual(result.sell.price, 0.45)
        self.assertEqual(result.buy.price, 0.42)

    def test_absent_sell_tariff_still_resolves_buy(self):
        tariff = self.tariff
        del tariff["sell_tariff"]
        now = datetime(2026, 7, 20, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(tariff, now)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.buy.price)
        self.assertIsNone(result.sell.price)
        self.assertIsNone(result.sell.period_name)
        self.assertIsNone(result.sell.season_name)

    def test_missing_rate_for_period_returns_none_price(self):
        tariff = self.tariff
        del tariff["energy_charges"]["Summer"]["rates"]["PERIOD_10_00"]
        now = datetime(2026, 7, 20, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(tariff, now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.period_name, "PERIOD_10_00")
        self.assertIsNone(result.buy.price)

    def test_currency_passthrough(self):
        now = datetime(2026, 7, 20, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(self.tariff, now)
        self.assertEqual(result.currency, "AUD")

    def test_no_season_covers_now_returns_none(self):
        tariff = self.tariff
        tariff["seasons"]["Summer"]["fromMonth"] = 1
        tariff["seasons"]["Summer"]["toMonth"] = 1
        tariff["seasons"]["Summer"]["fromDay"] = 1
        tariff["seasons"]["Summer"]["toDay"] = 31
        del tariff["sell_tariff"]
        now = datetime(2026, 7, 20, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(tariff, now)
        self.assertIsNone(result)

    def test_naive_now_raises_value_error(self):
        now = datetime(2026, 7, 20, 10, 0)
        with self.assertRaises(ValueError):
            get_tariff_periods(self.tariff, now)

    def test_horizon_hours_produces_upcoming_periods(self):
        now = datetime(2026, 7, 20, 23, 0, tzinfo=TZ)
        result = get_tariff_periods(self.tariff, now, horizon_hours=2)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.upcoming)
        self.assertGreaterEqual(len(result.upcoming), 3)
        self.assertEqual(result.upcoming[0].buy.period_name, "PERIOD_23_00")


def _season_geometry(from_month, from_day, to_month, to_day, tou_periods):
    return {
        "fromMonth": from_month,
        "fromDay": from_day,
        "toMonth": to_month,
        "toDay": to_day,
        "tou_periods": tou_periods,
    }


class SeasonYearCrossTests(TestCase):
    """A season spanning Oct -> Mar (year-cross) must be selected on both
    sides of the new year boundary."""

    def _tariff(self):
        winter_periods = {
            "ALL": {"periods": [{"toDayOfWeek": 6}]},
        }
        summer_periods = {
            "ON_PEAK": {"periods": [{"toDayOfWeek": 6}]},
        }
        return {
            "currency": "AUD",
            "energy_charges": {
                "Summer": {"rates": {"ON_PEAK": 0.4}},
                "Winter": {"rates": {"ALL": 0.2}},
            },
            "seasons": {
                "Summer": _season_geometry(10, 1, 3, 31, summer_periods),
                "Winter": _season_geometry(4, 1, 9, 30, winter_periods),
            },
        }

    def test_late_december_selects_year_crossing_season(self):
        now = datetime(2026, 12, 20, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.season_name, "Summer")
        self.assertEqual(result.buy.price, 0.4)

    def test_early_january_still_selects_year_crossing_season(self):
        now = datetime(2027, 1, 5, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.season_name, "Summer")

    def test_mid_year_selects_non_crossing_season(self):
        now = datetime(2026, 7, 15, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.season_name, "Winter")
        self.assertEqual(result.buy.price, 0.2)

    def test_season_boundary_delimits_period_and_upcoming(self):
        now = datetime(2026, 3, 31, 23, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now, horizon_hours=2)

        self.assertIsNotNone(result)
        boundary = datetime(2026, 4, 1, tzinfo=TZ)
        self.assertEqual(result.next_change, boundary)
        self.assertIsNotNone(result.upcoming)
        self.assertEqual(result.upcoming[0].end, boundary)
        self.assertEqual(result.upcoming[1].start, boundary)
        self.assertEqual(result.upcoming[1].buy.season_name, "Winter")
        self.assertEqual(result.upcoming[1].buy.price, 0.2)

    def test_season_start_delimits_current_period(self):
        now = datetime(2026, 4, 1, 1, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)

        self.assertIsNotNone(result)
        self.assertEqual(result.current_start, datetime(2026, 4, 1, tzinfo=TZ))


class DayOfWeekWrapTests(TestCase):
    """A period spanning Friday -> Monday (a long-weekend rate) must wrap
    the day-of-week range correctly, applying in full to each day in
    [Fri..Mon] and to no other day."""

    def _tariff(self):
        return {
            "currency": "AUD",
            "energy_charges": {
                "ALL": {
                    "rates": {
                        "LONG_WEEKEND": 0.15,
                        "WEEKDAY": 0.30,
                    }
                }
            },
            "seasons": {
                "ALL": {
                    "fromMonth": 1,
                    "fromDay": 1,
                    "toMonth": 12,
                    "toDay": 31,
                    "tou_periods": {
                        "LONG_WEEKEND": {
                            "periods": [
                                {
                                    "fromDayOfWeek": 4,
                                    "toDayOfWeek": 0,
                                    "fromHour": 0,
                                    "toHour": 24,
                                }
                            ]
                        },
                        "WEEKDAY": {
                            "periods": [
                                {
                                    "fromDayOfWeek": 1,
                                    "toDayOfWeek": 3,
                                    "fromHour": 0,
                                    "toHour": 24,
                                }
                            ]
                        },
                    },
                }
            },
        }

    def test_saturday_is_long_weekend_rate(self):
        # 2026-07-18 is a Saturday, inside the Fri(4)->Mon(0) wrap.
        now = datetime(2026, 7, 18, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.period_name, "LONG_WEEKEND")
        self.assertEqual(result.buy.price, 0.15)

    def test_monday_is_long_weekend_rate_wrapping_from_friday(self):
        # 2026-07-20 is a Monday - the last day of the Fri(4)->Mon(0) wrap.
        now = datetime(2026, 7, 20, 8, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.period_name, "LONG_WEEKEND")

    def test_tuesday_is_weekday_rate(self):
        # 2026-07-21 is a Tuesday - outside the Fri->Mon wrap.
        now = datetime(2026, 7, 21, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.period_name, "WEEKDAY")
        self.assertEqual(result.buy.price, 0.30)


class MidnightCrossingPeriodTests(TestCase):
    """A period whose local window crosses midnight without hitting the
    ``toHour: 24`` special case (e.g. 22:00 -> 06:00 overnight rate)."""

    def _tariff(self):
        return {
            "currency": "AUD",
            "energy_charges": {"ALL": {"rates": {"OVERNIGHT": 0.18, "DAY": 0.32}}},
            "seasons": {
                "ALL": {
                    "fromMonth": 1,
                    "fromDay": 1,
                    "toMonth": 12,
                    "toDay": 31,
                    "tou_periods": {
                        "OVERNIGHT": {
                            "periods": [{"toDayOfWeek": 6, "fromHour": 22, "toHour": 6}]
                        },
                        "DAY": {
                            "periods": [
                                {
                                    "toDayOfWeek": 6,
                                    "fromHour": 6,
                                    "toHour": 22,
                                }
                            ]
                        },
                    },
                }
            },
        }

    def test_just_after_midnight_is_still_overnight(self):
        now = datetime(2026, 7, 20, 1, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.period_name, "OVERNIGHT")
        self.assertEqual(result.buy.price, 0.18)

    def test_just_before_midnight_is_overnight(self):
        now = datetime(2026, 7, 20, 23, 30, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.period_name, "OVERNIGHT")

    def test_daytime_is_day_rate(self):
        now = datetime(2026, 7, 20, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.period_name, "DAY")

    def test_next_change_crosses_midnight_correctly(self):
        now = datetime(2026, 7, 20, 23, 30, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        # OVERNIGHT ends at 06:00 the next calendar day.
        expected = datetime(2026, 7, 21, 6, 0, tzinfo=TZ)
        self.assertEqual(result.next_change, expected)
