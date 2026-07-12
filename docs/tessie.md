# Tessie

Tessie is a service that provides additional telemetry data for Tesla vehicles.
This document shows the current `Tessie` and `TessieVehicle` surfaces exposed by
this library.

## Initialization

Initialize `Tessie` with an `aiohttp.ClientSession` and access token. The client
also accepts default command options for Tessie vehicle commands.

```python
import asyncio
import aiohttp
from tesla_fleet_api import Tessie


async def main():
    async with aiohttp.ClientSession() as session:
        tessie = Tessie(
            session=session,
            access_token="<access_token>",
            wait_for_completion=True,
            max_attempts=3,
        )


asyncio.run(main())
```

## Troubleshooting: Debug Logging

Enable the `tesla_fleet_api` logger at `DEBUG` to log each Tessie request's
final path segment, `transport=tessie`, and result:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("tesla_fleet_api").setLevel(logging.DEBUG)
```

Responses that are valid JSON but not objects, such as `null`, lists, or
scalars, are returned unchanged and log as `result=success`.

## Top-Level Client Methods

These methods exist on `Tessie` itself.

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

        response = await tessie.scopes()
        print(response)

        response = await tessie.list_vehicles()
        print(response)

        response = await tessie.list_vehicles(only_active=True)
        print(response)

        response = await tessie.all_battery_health()
        print(response)

        response = await tessie.charging_invoices()
        print(response)


asyncio.run(main())
```

## Vehicle Access

Vehicle-specific reads and commands are exposed through `TessieVehicle`, created
via `tessie.vehicles.create(vin)`.

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

        vehicle = tessie.vehicles.create("<vin>")


asyncio.run(main())
```

Most vehicle commands accept optional `wait_for_completion` and
`max_attempts` overrides. If omitted, they use the defaults configured on the
parent `Tessie` client.

## Vehicle Data

Use `state()` or its `vehicle()` alias for cached vehicle-state reads. The
`use_cache` parameter is supported there, but not on `vehicle_status()`.

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

        vehicle = tessie.vehicles.create("<vin>")

        response = await vehicle.state()
        print(response)

        response = await vehicle.state(use_cache=False)
        print(response)

        response = await vehicle.vehicle()
        print(response)

        response = await vehicle.battery()
        print(response)

        response = await vehicle.battery_health()
        print(response)

        response = await vehicle.states(start=1700000000, end=1700100000, results=10)
        print(response)

        response = await vehicle.location()
        print(response)

        response = await vehicle.firmware_alerts()
        print(response)

        response = await vehicle.map(width=800, height=600, zoom=15)
        print(response)

        response = await vehicle.consumption_since_charge()
        print(response)

        response = await vehicle.weather()
        print(response)

        response = await vehicle.drives(start=1700000000, end=1700100000)
        print(response)

        response = await vehicle.path(start=1700000000, end=1700100000)
        print(response)

        response = await vehicle.charges(start=1700000000, end=1700100000)
        print(response)

        response = await vehicle.idles(start=1700000000, end=1700100000)
        print(response)

        response = await vehicle.last_idle_state()
        print(response)


asyncio.run(main())
```

## Vehicle Commands

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

        vehicle = tessie.vehicles.create("<vin>")

        response = await vehicle.wake()
        print(response)

        response = await vehicle.lock()
        print(response)

        response = await vehicle.unlock()
        print(response)

        response = await vehicle.activate_front_trunk()
        print(response)

        response = await vehicle.activate_rear_trunk()
        print(response)

        response = await vehicle.open_tonneau()
        print(response)

        response = await vehicle.close_tonneau()
        print(response)

        response = await vehicle.vent_windows()
        print(response)

        response = await vehicle.close_windows()
        print(response)

        response = await vehicle.vent_sunroof()
        print(response)

        response = await vehicle.close_sunroof()
        print(response)

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

        response = await vehicle.tessie_set_cabin_overheat_protection(on=True)
        print(response)

        response = await vehicle.tessie_set_cop_temp(cop_temp=1)
        print(response)

        response = await vehicle.tessie_set_bioweapon_mode(on=True)
        print(response)

        response = await vehicle.tessie_set_climate_keeper_mode(mode=2)
        print(response)

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

        response = await vehicle.flash()
        print(response)

        response = await vehicle.honk()
        print(response)

        response = await vehicle.remote_start()
        print(response)

        response = await vehicle.tessie_trigger_homelink()
        print(response)

        response = await vehicle.enable_sentry()
        print(response)

        response = await vehicle.disable_sentry()
        print(response)

        response = await vehicle.enable_valet()
        print(response)

        response = await vehicle.disable_valet()
        print(response)

        response = await vehicle.enable_valet(pin="1234")
        print(response)

        response = await vehicle.disable_valet(pin="1234")
        print(response)

        response = await vehicle.enable_guest()
        print(response)

        response = await vehicle.disable_guest()
        print(response)

        response = await vehicle.set_speed_limit(limit_mph=65)
        print(response)

        response = await vehicle.enable_speed_limit(pin="1234")
        print(response)

        response = await vehicle.disable_speed_limit(pin="1234")
        print(response)

        response = await vehicle.clear_speed_limit_pin(pin="1234")
        print(response)

        response = await vehicle.tessie_schedule_software_update(in_seconds=3600)
        print(response)

        response = await vehicle.cancel_software_update()
        print(response)

        response = await vehicle.set_scheduled_charging(enable=True, time=360)
        print(response)

        response = await vehicle.tessie_set_scheduled_departure(
            enable=True,
            departure_time=420,
            preconditioning_enabled=True,
        )
        print(response)

        response = await vehicle.tessie_add_charge_schedule(
            days_of_week="Weekdays",
            enabled=True,
            start_enabled=True,
            end_enabled=True,
            lat=37.7749,
            lon=-122.4194,
            start_time=360,
            end_time=480,
            id=1,
        )
        print(response)

        response = await vehicle.remove_charge_schedule(id=1)
        print(response)

        response = await vehicle.tessie_add_precondition_schedule(
            days_of_week="Weekdays",
            enabled=True,
            lat=37.7749,
            lon=-122.4194,
            precondition_time=420,
            id=1,
        )
        print(response)

        response = await vehicle.remove_precondition_schedule(id=1)
        print(response)

        response = await vehicle.share(value="123 Main St, City, State")
        print(response)

        response = await vehicle.remote_boombox()
        print(response)

        response = await vehicle.remote_boombox(sound=1)
        print(response)

        response = await vehicle.enable_keep_accessory_power_mode()
        print(response)

        response = await vehicle.disable_keep_accessory_power_mode()
        print(response)

        response = await vehicle.enable_low_power_mode()
        print(response)

        response = await vehicle.disable_low_power_mode()
        print(response)

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

        response = await vehicle.get_fleet_telemetry_config()
        print(response)

        response = await vehicle.set_fleet_telemetry_config(config={"fields": {}})
        print(response)

        response = await vehicle.delete_fleet_telemetry_config()
        print(response)

        response = await vehicle.set_drive_tag(
            start=1700000000,
            end=1700100000,
            tag="commute",
        )
        print(response)

        response = await vehicle.set_drive_tag(
            drives=[1, 2],
            tag="commute",
        )
        print(response)

        response = await vehicle.set_charge_cost(
            charge_id=1,
            cost=12.50,
            currency="USD",
        )
        print(response)

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
