"""Tests for firmware_compare/firmware_at_least — dotted numeric firmware comparison.

Ported from Home Assistant core PR #175745, which fixed lexicographic string
comparisons (e.g. ``vehicle.firmware >= "2024.44.25"``) that misorder
week-based Tesla firmware versions such as "2025.10" sorting below "2025.9".
"""

from unittest import TestCase

from tesla_fleet_api import firmware_at_least, firmware_compare


class FirmwareCompareTests(TestCase):
    def test_lexicographic_bug_case(self) -> None:
        # "2025.10" < "2025.9" as plain strings, but 2025.10 is newer.
        self.assertEqual(firmware_compare("2025.10", "2025.9"), 1)
        self.assertEqual(firmware_compare("2025.9", "2025.10"), -1)

    def test_equal_versions(self) -> None:
        self.assertEqual(firmware_compare("2024.8", "2024.8"), 0)
        self.assertEqual(firmware_compare("2024.44.25", "2024.44.25"), 0)

    def test_partial_version_comparisons(self) -> None:
        self.assertEqual(firmware_compare("2025.14", "2025.2.6"), 1)
        self.assertEqual(firmware_compare("2025.2.6", "2025.14"), -1)
        self.assertEqual(firmware_compare("2024.44.25", "2024.8"), 1)
        self.assertEqual(firmware_compare("2024.8", "2024.44.25"), -1)

    def test_missing_trailing_components_treated_as_zero(self) -> None:
        self.assertEqual(firmware_compare("2024.26", "2024.26"), 0)
        self.assertEqual(firmware_compare("2024.26.0", "2024.26"), 0)
        self.assertEqual(firmware_compare("2024.26", "2024.26.25"), -1)
        self.assertEqual(firmware_compare("2024.26.25", "2024.26"), 1)

    def test_unparseable_firmware_sorts_behind_parseable(self) -> None:
        self.assertEqual(firmware_compare("Unknown", "2024.8"), -1)
        self.assertEqual(firmware_compare("2024.8", "Unknown"), 1)
        self.assertEqual(firmware_compare("Unknown", "Unknown"), 0)
        self.assertEqual(firmware_compare("", "2024.8"), -1)


class FirmwareAtLeastTests(TestCase):
    def test_lexicographic_bug_case(self) -> None:
        self.assertTrue(firmware_at_least("2025.10", "2025.9"))
        self.assertFalse(firmware_at_least("2025.9", "2025.10"))

    def test_equal_versions(self) -> None:
        self.assertTrue(firmware_at_least("2024.8", "2024.8"))
        self.assertTrue(firmware_at_least("2024.44.25", "2024.44.25"))

    def test_partial_version_comparisons(self) -> None:
        self.assertTrue(firmware_at_least("2025.14", "2025.2.6"))
        self.assertFalse(firmware_at_least("2025.2.6", "2025.14"))
        self.assertTrue(firmware_at_least("2024.44.25", "2024.8"))
        self.assertFalse(firmware_at_least("2024.8", "2024.44.25"))

    def test_missing_trailing_components_treated_as_zero(self) -> None:
        self.assertTrue(firmware_at_least("2024.26", "2024.26"))
        self.assertTrue(firmware_at_least("2024.26.0", "2024.26"))
        self.assertFalse(firmware_at_least("2024.26", "2024.26.25"))
        self.assertTrue(firmware_at_least("2024.26.25", "2024.26"))

    def test_streaming_firmware_thresholds_from_ha_pr(self) -> None:
        # Real minimum-version gates used by the Teslemetry HA integration.
        self.assertTrue(firmware_at_least("2024.44.25", "2024.44.25"))
        self.assertFalse(firmware_at_least("2024.44.24", "2024.44.25"))
        self.assertTrue(firmware_at_least("2024.26", "2024.26"))
        self.assertFalse(firmware_at_least("2024.25.99", "2024.26"))

    def test_unparseable_firmware_does_not_meet_minimum(self) -> None:
        self.assertFalse(firmware_at_least("Unknown", "2024.8"))
        self.assertFalse(firmware_at_least("Unknown", "2025.14"))
        self.assertFalse(firmware_at_least("", "2024.8"))
