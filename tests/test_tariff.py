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

    def test_empty_bare_dict_raises(self):
        with self.assertRaises(InvalidResponse):
            unwrap_tariff_v2({})

    def test_unrelated_bare_dict_raises(self):
        with self.assertRaises(InvalidResponse):
            unwrap_tariff_v2({"unexpected": True})

    def test_enveloped_empty_tariff_raises_via_response_envelope(self):
        # The minimal-shape check must apply identically on every
        # extraction path, not just the bare-object fallback - an empty
        # `{}` nested under a recognized envelope is still malformed.
        with self.assertRaises(InvalidResponse):
            unwrap_tariff_v2({"response": {"tariff_content_v2": {}}})

    def test_enveloped_empty_tariff_raises_via_tou_settings_envelope(self):
        with self.assertRaises(InvalidResponse):
            unwrap_tariff_v2({"tou_settings": {"tariff_content_v2": {}}})

    def test_empty_tariff_raises_via_top_level_key(self):
        with self.assertRaises(InvalidResponse):
            unwrap_tariff_v2({"tariff_content_v2": {}})


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


class LeapDaySeasonTests(TestCase):
    def _tariff(self):
        periods = {
            "ALL": {
                "periods": [{"fromDayOfWeek": 0, "toDayOfWeek": 0, "toHour": 24 * 7}]
            }
        }
        return {
            "currency": "AUD",
            "energy_charges": {"Leap": {"rates": {"ALL": 0.2}}},
            "seasons": {
                "Leap": _season_geometry(2, 29, 3, 31, periods),
            },
        }

    def test_non_leap_year_clamps_active_season_start(self):
        now = datetime(2026, 3, 1, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)

        self.assertIsNotNone(result)
        self.assertEqual(result.current_start, datetime(2026, 2, 28, tzinfo=TZ))

    def test_non_leap_february_28_is_covered(self):
        now = datetime(2026, 2, 28, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)

        self.assertIsNotNone(result)
        self.assertEqual(result.buy.season_name, "Leap")

    def test_adjacent_sell_season_clamps_next_start(self):
        tariff = self._tariff()
        tariff["seasons"] = {
            "ALL": _season_geometry(
                1,
                1,
                12,
                31,
                {
                    "ALL": {
                        "periods": [
                            {
                                "fromDayOfWeek": 0,
                                "toDayOfWeek": 0,
                                "toHour": 24 * 14,
                            }
                        ]
                    }
                },
            )
        }
        tariff["sell_tariff"] = {
            "energy_charges": {"Leap": {"rates": {"ALL": 0.1}}},
            "seasons": {
                "Leap": _season_geometry(
                    2,
                    29,
                    3,
                    31,
                    {"ALL": {"periods": [{"toDayOfWeek": 6, "toHour": 24}]}},
                )
            },
        }
        now = datetime(2026, 2, 20, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(tariff, now)

        self.assertIsNotNone(result)
        self.assertEqual(result.next_change, datetime(2026, 2, 28, tzinfo=TZ))


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


class SparsePeriodTests(TestCase):
    """A tariff whose single TOU period doesn't cover the whole day (a gap
    outside 06:00-09:00) must end the current period at its own actual
    end, not carry the rate forward to whatever period starts next
    elsewhere in the grid."""

    def _tariff(self):
        return {
            "currency": "AUD",
            "energy_charges": {"ALL": {"rates": {"MORNING": 0.20}}},
            "seasons": {
                "ALL": {
                    "fromMonth": 1,
                    "fromDay": 1,
                    "toMonth": 12,
                    "toDay": 31,
                    "tou_periods": {
                        "MORNING": {
                            "periods": [{"toDayOfWeek": 6, "fromHour": 6, "toHour": 9}]
                        },
                    },
                }
            },
        }

    def test_next_change_is_the_periods_own_end_not_the_next_days_start(self):
        now = datetime(2026, 7, 20, 7, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.period_name, "MORNING")
        self.assertEqual(result.current_start, datetime(2026, 7, 20, 6, 0, tzinfo=TZ))
        self.assertEqual(result.next_change, datetime(2026, 7, 20, 9, 0, tzinfo=TZ))

    def test_outside_the_period_no_rate_resolves(self):
        # A moment in the gap (09:00-06:00 the next day) is not covered by
        # any period, so the whole tariff resolves to nothing rather than
        # the stale MORNING rate.
        now = datetime(2026, 7, 20, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNone(result)

    def test_upcoming_advances_through_a_gap_to_the_next_days_period(self):
        # A 48-hour horizon must not stop at the first gap - it should
        # surface an explicit unresolved gap segment and then continue on
        # to tomorrow's (and the day after's) MORNING period.
        now = datetime(2026, 7, 20, 7, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now, horizon_hours=48)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.upcoming)
        starts_and_names = [(p.start, p.buy.period_name) for p in result.upcoming]
        self.assertEqual(
            starts_and_names,
            [
                (datetime(2026, 7, 20, 6, 0, tzinfo=TZ), "MORNING"),
                (datetime(2026, 7, 20, 9, 0, tzinfo=TZ), None),
                (datetime(2026, 7, 21, 6, 0, tzinfo=TZ), "MORNING"),
                (datetime(2026, 7, 21, 9, 0, tzinfo=TZ), None),
                (datetime(2026, 7, 22, 6, 0, tzinfo=TZ), "MORNING"),
            ],
        )
        gap_period = result.upcoming[1]
        self.assertIsNone(gap_period.buy.price)
        self.assertIsNone(gap_period.sell.price)
        self.assertEqual(gap_period.end, datetime(2026, 7, 21, 6, 0, tzinfo=TZ))
        self.assertGreaterEqual(result.upcoming[-1].end, now + timedelta(hours=48))

    def test_upcoming_covers_a_multi_day_gap_weekend_only_period(self):
        # A period active only on weekends leaves a 5-day gap (Mon-Fri) -
        # the walk must skip straight across it to the *following*
        # weekend, not just the next calendar day.
        tariff = {
            "currency": "AUD",
            "energy_charges": {"ALL": {"rates": {"WEEKEND": 0.1}}},
            "seasons": {
                "ALL": {
                    "fromMonth": 1,
                    "fromDay": 1,
                    "toMonth": 12,
                    "toDay": 31,
                    "tou_periods": {
                        "WEEKEND": {
                            "periods": [{"fromDayOfWeek": 5, "toDayOfWeek": 6}]
                        },
                    },
                }
            },
        }
        # 2026-07-25 is a Saturday - inside the WEEKEND period.
        now = datetime(2026, 7, 25, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(tariff, now, horizon_hours=24 * 10)

        self.assertIsNotNone(result)
        self.assertEqual(result.buy.price, 0.1)
        self.assertIsNotNone(result.upcoming)
        weekend_starts = [
            p.start for p in result.upcoming if p.buy.period_name == "WEEKEND"
        ]
        self.assertEqual(
            weekend_starts,
            [
                datetime(2026, 7, 25, tzinfo=TZ),
                datetime(2026, 7, 26, tzinfo=TZ),
                datetime(2026, 8, 1, tzinfo=TZ),
                datetime(2026, 8, 2, tzinfo=TZ),
            ],
        )
        gap_segment = next(
            p for p in result.upcoming if p.start == datetime(2026, 7, 27, tzinfo=TZ)
        )
        self.assertIsNone(gap_segment.buy.price)
        self.assertEqual(gap_segment.end, datetime(2026, 8, 1, tzinfo=TZ))


class UncoveredSeasonGapTests(TestCase):
    """A tariff whose only season covers part of the year (a real gap the
    rest of the year, e.g. a Summer-only plan) must let `upcoming` skip
    across the uncovered months to the season's next start, or clip
    cleanly to the horizon deadline when the season never resumes within
    it - never silently stop early."""

    def _tariff(self):
        return {
            "currency": "AUD",
            "energy_charges": {"Summer": {"rates": {"ALL": 0.4}}},
            "seasons": {
                "Summer": _season_geometry(
                    6, 1, 7, 31, {"ALL": {"periods": [{"toDayOfWeek": 6}]}}
                ),
            },
        }

    def test_gap_clips_to_deadline_when_season_never_resumes_in_horizon(self):
        now = datetime(2026, 7, 29, 12, 0, tzinfo=TZ)
        deadline = now + timedelta(hours=24 * 20)
        result = get_tariff_periods(self._tariff(), now, horizon_hours=24 * 20)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.upcoming)
        self.assertEqual(result.upcoming[-1].end, deadline)
        self.assertIsNone(result.upcoming[-1].buy.price)

    def test_gap_reaches_next_seasons_start_within_a_longer_horizon(self):
        now = datetime(2026, 7, 29, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now, horizon_hours=24 * 365)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.upcoming)
        next_summer = next(
            p
            for p in result.upcoming
            if p.buy.season_name == "Summer" and p.start.year == 2027
        )
        self.assertEqual(next_summer.start, datetime(2027, 6, 1, tzinfo=TZ))
        self.assertEqual(next_summer.buy.price, 0.4)


class InactiveSellPeriodTests(TestCase):
    def _tariff(self, sell_season=None):
        all_day = {
            "ALL": {
                "periods": [{"fromDayOfWeek": 0, "toDayOfWeek": 0, "toHour": 24 * 7}]
            }
        }
        morning = {
            "MORNING": {"periods": [{"toDayOfWeek": 6, "fromHour": 6, "toHour": 9}]}
        }
        season = {
            "fromMonth": 1,
            "fromDay": 1,
            "toMonth": 12,
            "toDay": 31,
        }
        return {
            "currency": "AUD",
            "energy_charges": {"ALL": {"rates": {"ALL": 0.25}}},
            "seasons": {"ALL": {**season, "tou_periods": all_day}},
            "sell_tariff": {
                "energy_charges": {"ALL": {"rates": {"MORNING": 0.1}}},
                "seasons": {"ALL": {**(sell_season or season), "tou_periods": morning}},
            },
        }

    def test_inactive_sell_rate_uses_adjacent_sell_boundaries(self):
        now = datetime(2026, 7, 20, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)

        self.assertIsNotNone(result)
        self.assertIsNone(result.sell.price)
        self.assertEqual(result.current_start, datetime(2026, 7, 20, 9, 0, tzinfo=TZ))
        self.assertEqual(result.next_change, datetime(2026, 7, 21, 6, 0, tzinfo=TZ))

    def test_upcoming_enters_next_sell_window(self):
        now = datetime(2026, 7, 20, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now, horizon_hours=24)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.upcoming)
        self.assertEqual(result.upcoming[0].end, datetime(2026, 7, 21, 6, 0, tzinfo=TZ))
        self.assertEqual(result.upcoming[1].sell.price, 0.1)

    def test_uncovered_sell_season_uses_next_season_start(self):
        sell_season = {
            "fromMonth": 7,
            "fromDay": 25,
            "toMonth": 7,
            "toDay": 31,
        }
        now = datetime(2026, 7, 20, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(sell_season), now)

        self.assertIsNotNone(result)
        self.assertIsNone(result.sell.price)
        self.assertEqual(result.next_change, datetime(2026, 7, 25, tzinfo=TZ))

    def test_uncovered_sell_season_uses_previous_season_end(self):
        sell_season = {
            "fromMonth": 7,
            "fromDay": 25,
            "toMonth": 7,
            "toDay": 31,
        }
        now = datetime(2026, 8, 2, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(sell_season), now)

        self.assertIsNotNone(result)
        self.assertIsNone(result.sell.price)
        self.assertEqual(result.current_start, datetime(2026, 8, 1, tzinfo=TZ))


class LongHorizonTests(TestCase):
    def test_upcoming_is_not_silently_truncated(self):
        now = datetime(2026, 7, 20, 0, 0, tzinfo=TZ)
        result = get_tariff_periods(_fixture_tariff(), now, horizon_hours=24 * 210)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.upcoming)
        self.assertGreater(len(result.upcoming), 10_000)
        self.assertGreaterEqual(result.upcoming[-1].end, now + timedelta(days=210))


class CurrentStartAfterSellBoundaryTests(TestCase):
    """When buy and sell schedules differ and both are currently active,
    ``current_start`` must be the LATER of the two period starts - the
    returned (buy, sell) pair is only valid from whichever side began
    most recently, not from whenever the buy period alone started."""

    def _tariff(self):
        return {
            "currency": "AUD",
            "energy_charges": {"ALL": {"rates": {"ALL": 0.30}}},
            "seasons": {
                "ALL": {
                    "fromMonth": 1,
                    "fromDay": 1,
                    "toMonth": 12,
                    "toDay": 31,
                    "tou_periods": {"ALL": {"periods": [{"toDayOfWeek": 6}]}},
                }
            },
            "sell_tariff": {
                "energy_charges": {"ALL": {"rates": {"DAY": 0.05}}},
                "seasons": {
                    "ALL": {
                        "fromMonth": 1,
                        "fromDay": 1,
                        "toMonth": 12,
                        "toDay": 31,
                        "tou_periods": {
                            "DAY": {
                                "periods": [
                                    {"toDayOfWeek": 6, "fromHour": 9, "toHour": 17}
                                ]
                            }
                        },
                    }
                },
            },
        }

    def test_current_start_is_the_later_of_buy_and_sell_starts(self):
        # Buy has been active since 00:00; sell's DAY window only started
        # at 09:00 - the combined pair is only valid from 09:00 on.
        now = datetime(2026, 7, 20, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)

        self.assertIsNotNone(result)
        self.assertEqual(result.current_start, datetime(2026, 7, 20, 9, 0, tzinfo=TZ))


class DstFallBackWallClockTests(TestCase):
    """Walking `upcoming` across a DST fall-back night must keep each
    day's local midnight boundary and weekday-based rate correct - a bug
    that added elapsed wall-clock minutes as if they were UTC-elapsed time
    would drift the local day label across the fold."""

    def _tariff(self):
        return {
            "currency": "AUD",
            "energy_charges": {"ALL": {"rates": {"WD": 0.30, "WE": 0.15}}},
            "seasons": {
                "ALL": {
                    "fromMonth": 1,
                    "fromDay": 1,
                    "toMonth": 12,
                    "toDay": 31,
                    "tou_periods": {
                        "WD": {"periods": [{"fromDayOfWeek": 0, "toDayOfWeek": 4}]},
                        "WE": {"periods": [{"fromDayOfWeek": 5, "toDayOfWeek": 6}]},
                    },
                }
            },
        }

    def test_weekday_boundaries_stay_correct_across_fall_back(self):
        # Sydney's 2026 DST fall-back is 2026-04-05 (Sunday) 03:00 -> 02:00.
        sydney = ZoneInfo("Australia/Sydney")
        now = datetime(2026, 4, 3, 12, 0, tzinfo=sydney)  # Friday
        result = get_tariff_periods(self._tariff(), now, horizon_hours=24 * 5)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.upcoming)
        expected = [
            (datetime(2026, 4, 3, tzinfo=sydney), 4, "WD"),
            (datetime(2026, 4, 4, tzinfo=sydney), 5, "WE"),
            (datetime(2026, 4, 5, tzinfo=sydney), 6, "WE"),
            (datetime(2026, 4, 6, tzinfo=sydney), 0, "WD"),
            (datetime(2026, 4, 7, tzinfo=sydney), 1, "WD"),
        ]
        for period, (start, weekday, period_name) in zip(
            result.upcoming, expected, strict=False
        ):
            self.assertEqual(period.start, start)
            self.assertEqual(period.start.weekday(), weekday)
            self.assertEqual(period.buy.period_name, period_name)
            self.assertEqual(period.end, start + timedelta(days=1))


class SeasonBoundaryUpcomingWalkTests(TestCase):
    """`upcoming` must re-resolve the season (and thus the price) for each
    future segment, including across more than one season transition
    within the horizon, rather than reusing the season resolved for
    `now`."""

    def _tariff(self):
        return {
            "currency": "AUD",
            "energy_charges": {
                "Spring": {"rates": {"ALL": 0.10}},
                "Summer": {"rates": {"ALL": 0.40}},
                "Autumn": {"rates": {"ALL": 0.20}},
            },
            "seasons": {
                "Spring": _season_geometry(
                    3, 1, 5, 31, {"ALL": {"periods": [{"toDayOfWeek": 6}]}}
                ),
                "Summer": _season_geometry(
                    6, 1, 7, 31, {"ALL": {"periods": [{"toDayOfWeek": 6}]}}
                ),
                "Autumn": _season_geometry(
                    8, 1, 8, 31, {"ALL": {"periods": [{"toDayOfWeek": 6}]}}
                ),
            },
        }

    def test_horizon_spanning_two_season_transitions_prices_each_segment(self):
        # 3 days before Summer starts, horizon reaches 3 days into Autumn -
        # crossing both the Spring->Summer and Summer->Autumn boundaries.
        now = datetime(2026, 5, 29, 12, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now, horizon_hours=24 * 65)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.upcoming)

        seasons_seen = [period.buy.season_name for period in result.upcoming]
        self.assertIn("Spring", seasons_seen)
        self.assertIn("Summer", seasons_seen)
        self.assertIn("Autumn", seasons_seen)

        # Each daily segment resolves its own season/price - a segment
        # anywhere inside Summer must never carry Spring's or Autumn's price.
        for period in result.upcoming:
            if period.buy.season_name == "Summer":
                self.assertEqual(period.buy.price, 0.40)
            elif period.buy.season_name == "Spring":
                self.assertEqual(period.buy.price, 0.10)
            elif period.buy.season_name == "Autumn":
                self.assertEqual(period.buy.price, 0.20)

        # The segment straddling the Spring->Summer boundary switches at
        # exactly that boundary, not one grid-tick later or earlier.
        last_spring = next(
            p for p in reversed(result.upcoming) if p.buy.season_name == "Spring"
        )
        first_summer = next(p for p in result.upcoming if p.buy.season_name == "Summer")
        self.assertEqual(last_spring.end, datetime(2026, 6, 1, tzinfo=TZ))
        self.assertEqual(first_summer.start, datetime(2026, 6, 1, tzinfo=TZ))

        # Likewise for the Summer->Autumn boundary later in the same horizon.
        last_summer = next(
            p for p in reversed(result.upcoming) if p.buy.season_name == "Summer"
        )
        first_autumn = next(p for p in result.upcoming if p.buy.season_name == "Autumn")
        self.assertEqual(last_summer.end, datetime(2026, 8, 1, tzinfo=TZ))
        self.assertEqual(first_autumn.start, datetime(2026, 8, 1, tzinfo=TZ))


class DstBoundaryTests(TestCase):
    """A period boundary that falls on the day of a DST transition must
    keep the intended local wall-clock label (e.g. "changes at 02:30"
    stays 02:30), built directly in the site timezone rather than via
    arithmetic on a UTC instant - the latter would land an hour off."""

    def _tariff(self):
        return {
            "currency": "AUD",
            "energy_charges": {"ALL": {"rates": {"NIGHT": 0.2, "DAY": 0.3}}},
            "seasons": {
                "ALL": {
                    "fromMonth": 1,
                    "fromDay": 1,
                    "toMonth": 12,
                    "toDay": 31,
                    "tou_periods": {
                        "NIGHT": {
                            "periods": [{"toDayOfWeek": 6, "fromHour": 0, "toHour": 2}]
                        },
                        "DAY": {
                            "periods": [{"toDayOfWeek": 6, "fromHour": 2, "toHour": 24}]
                        },
                    },
                }
            },
        }

    def test_boundary_keeps_local_wall_clock_across_spring_forward(self):
        # Sydney's 2026 spring-forward is 2026-10-04 02:00 -> 03:00 local.
        sydney = ZoneInfo("Australia/Sydney")
        now = datetime(2026, 10, 4, 1, 0, tzinfo=sydney)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.period_name, "NIGHT")
        # The NIGHT->DAY boundary is defined at local 02:00, still 02:00
        # even though this calendar day skips straight to 03:00.
        expected = datetime(2026, 10, 4, 2, 0, tzinfo=sydney)
        self.assertEqual(result.next_change.replace(tzinfo=sydney), expected)
        self.assertEqual(result.next_change.hour, 2)


class EmptySeasonRatesFallbackTests(TestCase):
    """When the matched season key exists in `energy_charges` but carries
    no `rates` block (e.g. an unused `"Winter": {}` alongside an `"ALL"`
    default), the price lookup must fall back to `charges["ALL"]` rather
    than resolving to `None`."""

    def _tariff(self):
        return {
            "currency": "AUD",
            "energy_charges": {
                "ALL": {"rates": {"ALL": 0.25}},
                "Winter": {},
            },
            "seasons": {
                "Winter": _season_geometry(
                    1, 1, 12, 31, {"ALL": {"periods": [{"toDayOfWeek": 6}]}}
                ),
            },
        }

    def test_empty_season_rates_falls_back_to_all(self):
        now = datetime(2026, 7, 20, 10, 0, tzinfo=TZ)
        result = get_tariff_periods(self._tariff(), now)
        self.assertIsNotNone(result)
        self.assertEqual(result.buy.season_name, "Winter")
        self.assertEqual(result.buy.price, 0.25)
