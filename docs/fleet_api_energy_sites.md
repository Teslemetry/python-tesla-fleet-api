# Fleet API for Energy Sites

This document provides detailed examples for using the Fleet API for energy sites.

## Create an Energy Site

The `TeslaFleetApi` class provides methods to interact with the Fleet API for energy sites. First, create an `EnergySite` instance using the energy site ID (which can be found via `api.products()`):

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            data = await energy_site.site_info()
            print(data)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Backup Reserve

You can adjust the backup reserve for a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            backup_reserve_response = await energy_site.backup(backup_reserve_percent=20)
            print(backup_reserve_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Backup History

You can get the backup (off-grid) event history of a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            backup_history_response = await energy_site.backup_history(period="day")
            print(backup_history_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Charge History

You can get the charging history of a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            charge_history_response = await energy_site.charge_history(start_date="2022-01-01", end_date="2022-01-31")
            print(charge_history_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Energy History

You can get the energy measurements of a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            energy_history_response = await energy_site.energy_history(period="day")
            print(energy_history_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Grid Import/Export

You can allow or disallow charging from the grid and exporting energy to the grid for a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            grid_import_export_response = await energy_site.grid_import_export(disallow_charge_from_grid_with_solar_installed=True)
            print(grid_import_export_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Live Status

You can get the live status of a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            live_status_response = await energy_site.live_status()
            print(live_status_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Off-Grid Vehicle Charging Reserve

You can adjust the off-grid vehicle charging backup reserve for a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            off_grid_vehicle_charging_reserve_response = await energy_site.off_grid_vehicle_charging_reserve(off_grid_vehicle_charging_reserve_percent=10)
            print(off_grid_vehicle_charging_reserve_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Operation Mode

You can set the operation mode for a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            operation_mode_response = await energy_site.operation(default_real_mode="self_consumption")
            print(operation_mode_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Site Info

You can get information about a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            site_info_response = await energy_site.site_info()
            print(site_info_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Storm Mode

You can update the storm watch participation for a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            storm_mode_response = await energy_site.storm_mode(enabled=True)
            print(storm_mode_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Time of Use Settings

You can update the time of use settings for a specific energy site using its ID:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)
            time_of_use_settings_response = await energy_site.time_of_use_settings(settings={"tou_settings": {"tariff_content_v2": {}}})
            print(time_of_use_settings_response)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

## Device Commands

Energy gateways (Powerwalls, etc.) support gRPC commands sent via `POST /api/1/energy_sites/{id}/command`. These are undocumented Tesla API endpoints that communicate directly with the gateway hardware. All device command methods require the `energy_cmds` scope.

### Available Commands

| Method | Category | Description |
|--------|----------|-------------|
| `get_system_info()` | Common | Firmware version, device type, part number, serial number, DIN |
| `get_networking_status()` | Common | WiFi, Ethernet, and cellular connectivity status |
| `wifi_scan()` | Common | Scan for available WiFi networks |
| `get_device_cert()` | Common | Device certificate (subject, issuer, validity) |
| `list_authorized_clients()` | Authorization | Paired keys with roles, state, and verification |
| `get_signed_commands_public_key()` | Authorization | Gateway's public key for signed commands |
| `get_backup_events()` | TEG | Backup event history (may timeout on some firmware) |
| `schedule_backup_event()` | TEG | Schedule a manual backup event |
| `cancel_backup_event()` | TEG | Cancel a scheduled backup event |

### Example

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            energy_site = api.energySites.create(12345)

            # Get gateway system information
            system_info = await energy_site.get_system_info()
            print(system_info)

            # Get networking status
            networking = await energy_site.get_networking_status()
            print(networking)

            # List authorized clients (paired keys)
            clients = await energy_site.list_authorized_clients()
            print(clients)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```
