# Tessie

Tessie is a service that provides additional telemetry data for Tesla vehicles. This document provides detailed examples of how to use the Tessie class in the Tesla Fleet API library.

## Initialization

To use the Tessie class, you need to initialize it with an aiohttp ClientSession and an access token.

```python
import asyncio
import aiohttp
from tesla_fleet_api import Tessie

async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

asyncio.run(main())
```

## Get Scopes

The `scopes` method retrieves the Tesla scopes associated with the account.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        response = await tessie.scopes()
        print(response)

asyncio.run(main())
```

## List Vehicles

The `list_vehicles` method retrieves the list of vehicles associated with the account.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        # List all vehicles
        response = await tessie.list_vehicles()
        print(response)

        # List only active vehicles
        response = await tessie.list_vehicles(only_active=True)
        print(response)

asyncio.run(main())
```

## Get Vehicle State

The `state` method retrieves the state of a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.state(vin)
        print(response)

asyncio.run(main())
```

## Get Battery Data

The `battery` method retrieves the battery data of a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.battery(vin)
        print(response)

asyncio.run(main())
```

## Get Battery Health Data

The `battery_health` method retrieves the battery health data of a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.battery_health(vin)
        print(response)

asyncio.run(main())
```

## Get All Battery Health Data

The `all_battery_health` method retrieves the battery health data of all vehicles associated with the account.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        response = await tessie.all_battery_health()
        print(response)

asyncio.run(main())
```

## Get Historical Vehicle States

The `states` method retrieves historical vehicle states within a timeframe.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.states(vin, start=1700000000, end=1700100000, results=10)
        print(response)

asyncio.run(main())
```

## Get Vehicle Location

The `location` method retrieves coordinates, address, and saved location of a specific vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.location(vin)
        print(response)

asyncio.run(main())
```

## Get Firmware Alerts

The `firmware_alerts` method retrieves the list of firmware-generated alerts for a vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.firmware_alerts(vin)
        print(response)

asyncio.run(main())
```

## Get Map Image

The `map` method retrieves a map image of the vehicle's location.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.map(vin, width=800, height=600, zoom=15)
        print(response)

asyncio.run(main())
```

## Get Consumption Since Charge

The `consumption_since_charge` method retrieves energy use data since the last charge.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.consumption_since_charge(vin)
        print(response)

asyncio.run(main())
```

## Get Weather

The `weather` method retrieves the weather forecast around the vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.weather(vin)
        print(response)

asyncio.run(main())
```

## Get Drives

The `drives` method retrieves historical drive records.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.drives(vin, start=1700000000, end=1700100000)
        print(response)

asyncio.run(main())
```

## Get Drive Path

The `path` method retrieves the driving route during a specified timeframe.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.path(vin, start=1700000000, end=1700100000)
        print(response)

asyncio.run(main())
```

## Get Charges

The `charges` method retrieves charging history for a vehicle.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.charges(vin, start=1700000000, end=1700100000)
        print(response)

asyncio.run(main())
```

## Get Charging Invoices

The `charging_invoices` method retrieves charging costs for all vehicles.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        response = await tessie.charging_invoices()
        print(response)

asyncio.run(main())
```

## Get Idle Periods

The `idles` method retrieves idle periods when the vehicle was inactive.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.idles(vin, start=1700000000, end=1700100000)
        print(response)

asyncio.run(main())
```

## Get Last Idle State

The `last_idle_state` method retrieves the latest idle period data.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vin = "<vin>"

        response = await tessie.last_idle_state(vin)
        print(response)

asyncio.run(main())
```

## Vehicle Commands

Vehicle-specific commands are accessed through a `TessieVehicle` instance, created via `tessie.vehicles.create(vin)`.

```python
async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
        )

        vehicle = tessie.vehicles.create("<vin>")
```

### Wake

```python
        response = await vehicle.wake()
        print(response)
```

### Lock/Unlock

```python
        response = await vehicle.lock()
        print(response)

        response = await vehicle.unlock()
        print(response)
```

### Trunks

```python
        response = await vehicle.activate_front_trunk()
        print(response)

        response = await vehicle.activate_rear_trunk()
        print(response)
```

### Tonneau

```python
        response = await vehicle.open_tonneau()
        print(response)

        response = await vehicle.close_tonneau()
        print(response)
```

### Windows

```python
        response = await vehicle.vent_windows()
        print(response)

        response = await vehicle.close_windows()
        print(response)
```

### Sunroof

```python
        response = await vehicle.vent_sunroof()
        print(response)

        response = await vehicle.close_sunroof()
        print(response)
```

### Climate

```python
        response = await vehicle.start_climate()
        print(response)

        response = await vehicle.stop_climate()
        print(response)

        response = await vehicle.set_temperatures(temperature=21.0)
        print(response)

        response = await vehicle.set_seat_heat(seat="front_left", level=3)
        print(response)

        response = await vehicle.set_seat_cool(seat="front_left", level=2)
        print(response)

        response = await vehicle.start_max_defrost()
        print(response)

        response = await vehicle.stop_max_defrost()
        print(response)

        response = await vehicle.start_steering_wheel_heater()
        print(response)

        response = await vehicle.stop_steering_wheel_heater()
        print(response)

        response = await vehicle.tessie_set_cabin_overheat_protection(mode="on")
        print(response)

        response = await vehicle.tessie_set_cop_temp(temperature="low")
        print(response)

        response = await vehicle.tessie_set_bioweapon_mode(enable=True)
        print(response)

        response = await vehicle.tessie_set_climate_keeper_mode(mode=2)
        print(response)
```

### Charging

```python
        response = await vehicle.start_charging()
        print(response)

        response = await vehicle.stop_charging()
        print(response)

        response = await vehicle.set_charge_limit(percent=80)
        print(response)

        response = await vehicle.tessie_set_charging_amps(amps=32)
        print(response)

        response = await vehicle.open_charge_port()
        print(response)

        response = await vehicle.close_charge_port()
        print(response)
```

### Lights and Horn

```python
        response = await vehicle.flash()
        print(response)

        response = await vehicle.honk()
        print(response)
```

### Remote Start and HomeLink

```python
        response = await vehicle.remote_start()
        print(response)

        response = await vehicle.tessie_trigger_homelink()
        print(response)
```

### Sentry Mode

```python
        response = await vehicle.enable_sentry()
        print(response)

        response = await vehicle.disable_sentry()
        print(response)
```

### Valet Mode

```python
        response = await vehicle.enable_valet(pin="1234")
        print(response)

        response = await vehicle.disable_valet(pin="1234")
        print(response)
```

### Guest Mode

```python
        response = await vehicle.enable_guest()
        print(response)

        response = await vehicle.disable_guest()
        print(response)
```

### Speed Limits

```python
        response = await vehicle.set_speed_limit(limit_mph=65)
        print(response)

        response = await vehicle.enable_speed_limit(pin="1234")
        print(response)

        response = await vehicle.disable_speed_limit(pin="1234")
        print(response)

        response = await vehicle.clear_speed_limit_pin(pin="1234")
        print(response)
```

### Software Updates

```python
        response = await vehicle.tessie_schedule_software_update(offset_seconds=3600)
        print(response)

        response = await vehicle.cancel_software_update()
        print(response)
```

### Scheduled Charging

```python
        response = await vehicle.set_scheduled_charging(enable=True, time=360)
        print(response)

        response = await vehicle.tessie_set_scheduled_departure(
            enable=True,
            departure_time=420,
            preconditioning_enabled=True,
        )
        print(response)
```

### Charge Schedules

```python
        response = await vehicle.tessie_add_charge_schedule(
            id=1,
            enabled=True,
            days_of_week="0111110",
            start_time=360,
            end_time=480,
            lat=37.7749,
            lon=-122.4194,
        )
        print(response)

        response = await vehicle.remove_charge_schedule(id=1)
        print(response)
```

### Precondition Schedules

```python
        response = await vehicle.tessie_add_precondition_schedule(
            id=1,
            enabled=True,
            days_of_week="0111110",
            precondition_time=420,
            lat=37.7749,
            lon=-122.4194,
        )
        print(response)

        response = await vehicle.remove_precondition_schedule(id=1)
        print(response)
```

### Share

```python
        response = await vehicle.share(value="123 Main St, City, State")
        print(response)
```

### Boombox

```python
        response = await vehicle.remote_boombox(sound=1)
        print(response)
```

### Power Modes

```python
        response = await vehicle.enable_keep_accessory_power_mode()
        print(response)

        response = await vehicle.disable_keep_accessory_power_mode()
        print(response)

        response = await vehicle.enable_low_power_mode()
        print(response)

        response = await vehicle.disable_low_power_mode()
        print(response)
```

### Driver Management

```python
        response = await vehicle.drivers()
        print(response)

        response = await vehicle.create_invitation(email="user@example.com")
        print(response)

        response = await vehicle.invitations()
        print(response)

        response = await vehicle.revoke_invitation(id=1)
        print(response)

        response = await vehicle.delete_driver(id=1)
        print(response)
```

### Fleet Telemetry

```python
        response = await vehicle.get_fleet_telemetry_config()
        print(response)

        response = await vehicle.set_fleet_telemetry_config(config={"fields": {}})
        print(response)

        response = await vehicle.delete_fleet_telemetry_config()
        print(response)
```

### Data Management

```python
        response = await vehicle.set_drive_tag(start=1700000000, end=1700100000, tag="commute")
        print(response)

        response = await vehicle.set_charge_cost(charge_id=1, cost=12.50, currency="USD")
        print(response)
```

### Vehicle Information

```python
        response = await vehicle.tire_pressure()
        print(response)

        response = await vehicle.vehicle_status()
        print(response)

        response = await vehicle.plate()
        print(response)

        response = await vehicle.update_plate(plate="ABC1234", state="CA")
        print(response)

asyncio.run(main())
```
