# Tesla Fleet API

Tesla Fleet API is a Python library that provides an interface to interact with Tesla's Fleet API, including signed commands and encrypted local Bluetooth (BLE) communication. It also supports interactions with Teslemetry and Tessie services.

## Features

- Fleet API for vehicles
- Fleet API for energy sites
- Fleet API with signed vehicle commands
- Bluetooth for vehicles
- Teslemetry integration
- Tessie integration

## Installation

You can install the library using pip:

```bash
pip install tesla-fleet-api
```

## Usage

### Authentication

The `TeslaFleetOAuth` class provides methods that help with authenticating to the Tesla Fleet API. Here's a basic example:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetOAuth

async def main():
    async with aiohttp.ClientSession() as session:
        oauth = TeslaFleetOAuth(
            session=session,
            client_id="<client_id>",
            client_secret="<client_secret>",
            redirect_uri="<redirect_uri>",
        )

        # Get the login URL and navigate the user to it
        login_url = oauth.get_login_url(scopes=["openid", "email", "offline_access"])
        print(f"Please go to {login_url} and authorize access.")

        # After the user authorizes access, they will be redirected to the redirect_uri with a code
        code = input("Enter the code you received: ")

        # Exchange the code for a refresh token
        await oauth.get_refresh_token(code)
        print(f"Access token: {oauth.access_token}")
        print(f"Refresh token: {oauth.refresh_token}")
        # Dont forget to store the refresh token so you can use it again later

asyncio.run(main())
```

### Fleet API for Vehicles

The `TeslaFleetApi` class provides methods to interact with the Fleet API for vehicles. Here's a basic example:

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
            data = await api.vehicles.list()
            print(data)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

For more detailed examples, see [Fleet API for Vehicles](docs/fleet_api_vehicles.md).

### Fleet API for Energy Sites

The `EnergySites` class provides methods to interact with the Fleet API for energy sites. Here's a basic example:

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
            energy_sites = await api.energySites.list()
            print(energy_sites)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

For more detailed examples, see [Fleet API for Energy Sites](docs/fleet_api_energy_sites.md).

### Fleet API with Signed Vehicle Commands

The `VehicleSigned` class provides methods to interact with the Fleet API using signed vehicle commands. Here's a basic example:

```python
import asyncio
import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            access_token="<access_token>",
            session=session,
            region="na",
        )

        try:
            vehicle = VehicleSigned(api, "<vin>")
            await vehicle.handshake()
            data = await vehicle.wake_up()
            print(data)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

For more detailed examples, see [Fleet API with Signed Vehicle Commands](docs/fleet_api_signed_commands.md).

### Bluetooth for Vehicles

The `TeslaBluetooth` class provides methods to interact with Tesla vehicles using Bluetooth. Here's a basic example:

```python
import asyncio
from bleak import BleakScanner
from tesla_fleet_api import TeslaBluetooth

async def main():
    scanner = BleakScanner()
    devices = await scanner.discover()
    for device in devices:
        if TeslaBluetooth().valid_name(device.name):
            print(f"Found Tesla vehicle: {device.name}")

asyncio.run(main())
```

For more detailed examples, see [Bluetooth for Vehicles](docs/bluetooth_vehicles.md).

### Teslemetry

The `Teslemetry` class provides methods to interact with the Teslemetry service. Here's a basic example:

```python
import asyncio
import aiohttp
from tesla_fleet_api import Teslemetry
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = Teslemetry(
            access_token="<access_token>",
            session=session,
        )

        try:
            data = await api.vehicles.list()
            print(data)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

For more detailed examples, see [Teslemetry](docs/teslemetry.md).

### Tessie

The `Tessie` class provides methods to interact with the Tessie service. Here's a basic example:

```python
import asyncio
import aiohttp
from tesla_fleet_api import Tessie
from tesla_fleet_api.exceptions import TeslaFleetError

async def main():
    async with aiohttp.ClientSession() as session:
        api = Tessie(
            access_token="<access_token>",
            session=session,
        )

        try:
            data = await api.vehicles.list()
            print(data)
        except TeslaFleetError as e:
            print(e)

asyncio.run(main())
```

For more detailed examples, see [Tessie](docs/tessie.md).
