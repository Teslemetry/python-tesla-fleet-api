"""Unit tests for the local-Powerwall key-ownership merge contract.

`merge_local_into_cloud` is a plain function, independent of `Router`
dispatch - see docs/energy_local_control.md's "Merge contract" section.
"""

import unittest

from tesla_fleet_api.router import (
    LOCAL_LIVE_STATUS_KEYS,
    LOCAL_SITE_INFO_KEYS,
    merge_live_status,
    merge_local_into_cloud,
    merge_site_info,
)


class TestMergeLocalIntoCloud(unittest.TestCase):
    def test_local_none_returns_cloud_values(self) -> None:
        cloud = {"solar_power": 100, "grid_power": 50, "generator_power": 0}
        result = merge_local_into_cloud(cloud, None, LOCAL_LIVE_STATUS_KEYS)
        self.assertEqual(result, cloud)

    def test_owned_key_present_in_local_is_overlaid(self) -> None:
        cloud = {"solar_power": 100, "grid_power": 50}
        local = {"solar_power": 200}
        result = merge_local_into_cloud(cloud, local, LOCAL_LIVE_STATUS_KEYS)
        self.assertEqual(result["solar_power"], 200)
        self.assertEqual(result["grid_power"], 50)

    def test_owned_key_absent_from_local_keeps_cloud_value(self) -> None:
        cloud = {"solar_power": 100, "grid_power": 50}
        local: dict = {"solar_power": 200}
        result = merge_local_into_cloud(cloud, local, LOCAL_LIVE_STATUS_KEYS)
        self.assertEqual(result["grid_power"], 50)

    def test_falsy_but_present_local_value_is_overlaid(self) -> None:
        cloud = {"grid_power": 999}
        local = {"grid_power": 0}
        result = merge_local_into_cloud(cloud, local, LOCAL_LIVE_STATUS_KEYS)
        self.assertEqual(result["grid_power"], 0)

    def test_falsy_bool_local_value_is_overlaid(self) -> None:
        cloud = {"island_status": "on_grid"}
        local = {"island_status": False}
        result = merge_local_into_cloud(cloud, local, LOCAL_LIVE_STATUS_KEYS)
        self.assertEqual(result["island_status"], False)

    def test_owned_key_present_with_none_keeps_cloud_value(self) -> None:
        cloud = {"solar_power": 100, "grid_power": 50}
        local = {"solar_power": None, "grid_power": 75}
        result = merge_local_into_cloud(cloud, local, LOCAL_LIVE_STATUS_KEYS)
        self.assertEqual(result["solar_power"], 100)
        self.assertEqual(result["grid_power"], 75)

    def test_local_keys_outside_owned_set_are_ignored(self) -> None:
        cloud = {"solar_power": 100}
        local = {"solar_power": 200, "some_unowned_field": "surprise"}
        result = merge_local_into_cloud(cloud, local, LOCAL_LIVE_STATUS_KEYS)
        self.assertNotIn("some_unowned_field", result)

    def test_does_not_mutate_inputs(self) -> None:
        cloud = {"solar_power": 100}
        local = {"solar_power": 200}
        cloud_copy = dict(cloud)
        local_copy = dict(local)
        result = merge_local_into_cloud(cloud, local, LOCAL_LIVE_STATUS_KEYS)
        self.assertEqual(cloud, cloud_copy)
        self.assertEqual(local, local_copy)
        self.assertIsNot(result, cloud)

    def test_returns_new_dict_when_local_is_none(self) -> None:
        cloud = {"solar_power": 100}
        result = merge_local_into_cloud(cloud, None, LOCAL_LIVE_STATUS_KEYS)
        self.assertIsNot(result, cloud)

    def test_site_info_keys(self) -> None:
        cloud = {"backup_reserve_percent": 20, "default_real_mode": "self_consumption"}
        local = {"backup_reserve_percent": 30}
        result = merge_local_into_cloud(cloud, local, LOCAL_SITE_INFO_KEYS)
        self.assertEqual(result["backup_reserve_percent"], 30)
        self.assertEqual(result["default_real_mode"], "self_consumption")


class TestMergeLiveStatus(unittest.TestCase):
    def test_matches_generic_call_with_live_status_keys(self) -> None:
        cloud = {"solar_power": 100, "grid_power": 50}
        local = {"solar_power": 200, "some_unowned_field": "surprise"}
        expected = merge_local_into_cloud(cloud, local, LOCAL_LIVE_STATUS_KEYS)
        result = merge_live_status(cloud, local)
        self.assertEqual(result, expected)
        self.assertEqual(result["solar_power"], 200)
        self.assertEqual(result["grid_power"], 50)
        self.assertNotIn("some_unowned_field", result)

    def test_local_none_passthrough(self) -> None:
        cloud = {"solar_power": 100}
        self.assertEqual(merge_live_status(cloud, None), cloud)


class TestMergeSiteInfo(unittest.TestCase):
    def test_matches_generic_call_with_site_info_keys(self) -> None:
        cloud = {"backup_reserve_percent": 20, "default_real_mode": "self_consumption"}
        local = {"backup_reserve_percent": 30}
        expected = merge_local_into_cloud(cloud, local, LOCAL_SITE_INFO_KEYS)
        result = merge_site_info(cloud, local)
        self.assertEqual(result, expected)
        self.assertEqual(result["backup_reserve_percent"], 30)
        self.assertEqual(result["default_real_mode"], "self_consumption")

    def test_local_none_passthrough(self) -> None:
        cloud = {"backup_reserve_percent": 20}
        self.assertEqual(merge_site_info(cloud, None), cloud)


if __name__ == "__main__":
    unittest.main()
