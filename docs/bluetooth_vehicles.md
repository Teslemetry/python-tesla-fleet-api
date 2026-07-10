# Bluetooth for Vehicles

This document provides detailed examples for using Bluetooth for vehicles.

## Initialize TeslaBluetooth

The `TeslaBluetooth` class provides methods to interact with Tesla vehicles using Bluetooth. Here's a basic example to initialize the `TeslaBluetooth` class and discover nearby Tesla vehicles:

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

## Create VehicleBluetooth Instance

You can create a `VehicleBluetooth` instance using the `TeslaBluetooth` class. Here's a basic example to create a `VehicleBluetooth` instance and set the private key from a file:

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth

async def main():
    tesla_bluetooth = TeslaBluetooth()
    await tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    vehicle.find_vehicle()
    print(f"Created VehicleBluetooth instance for VIN: {vehicle.vin}")

asyncio.run(main())
```

## Pair Vehicle

You can pair a `VehicleBluetooth` instance using the `pair` method. Here's a basic example to pair a `VehicleBluetooth` instance:

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth

async def main():
    tesla_bluetooth = TeslaBluetooth()
    device = await tesla_bluetooth.find_vehicle()
    private_key = await tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    await vehicle.pair()
    print(f"Paired with VehicleBluetooth instance for VIN: {vehicle.vin}")

asyncio.run(main())
```

## Wake Up Vehicle

You can wake up a `VehicleBluetooth` instance using the `wake_up` method. Here's a basic example to wake up a `VehicleBluetooth` instance:

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth
from tesla_fleet_api.exceptions import BluetoothTimeout, TeslaFleetError

async def main():
    tesla_bluetooth = TeslaBluetooth()
    device = await tesla_bluetooth.find_vehicle()
    private_key = await tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    try:
        await vehicle.wake_up()
    except BluetoothTimeout:
        pass
    except TeslaFleetError as e:
        print(e)
    print(f"Sent wake request to VehicleBluetooth instance for VIN: {vehicle.vin}")

asyncio.run(main())
```

`wake_up()` is best-effort over BLE: a `BluetoothTimeout` from the wake request
can be a false negative even when the vehicle wakes successfully. Confirm
readiness by retrying a cheap INFO-domain read, such as `charge_state()`, with
backoff. The infotainment computer can also take longer to become ready than
the vehicle-security computer, so INFO-domain reads immediately after waking
should retry `BluetoothTimeout` with backoff. Keep one BLE connection open
across related commands when possible instead of reconnecting for each command.

`VehicleBluetooth` raises `BluetoothTransportError`, a `TeslaFleetError`
subclass, when the BLE connection, notification setup, or GATT command write
fails before a vehicle response can be awaited. The original transport
exception is available as the exception's `__cause__`; this includes
`bleak.exc.BleakError` and builtin `TimeoutError` from ESPHome proxy connect,
notify, or write timeouts. Catch `TeslaFleetError` to handle both transport
failures and response-wait `BluetoothTimeout` failures with one library error
hierarchy, or catch `BluetoothTransportError` separately when you need to
distinguish a transport failure from a vehicle timeout.

BLE response chunks are reassembled with the same stale-frame behavior as
Tesla's vehicle-command BLE connector: if a partial frame sits idle for more
than one second before the next chunk arrives, the partial frame is discarded
before processing the new chunk. This prevents a dropped chunk from corrupting
the next response, but it does not change command acknowledgement timeouts.

## Mutating Command Timeouts

A `BluetoothTimeout` from a mutating BLE command is inconclusive, not proof that
the command failed. The vehicle can apply the command even when its
acknowledgement does not reach the client. For commands that change vehicle
state, snapshot the relevant state before acting and verify the outcome with a
follow-up state read after any timeout.

VCSEC actuations, such as RKE, closure, and wake requests, return as soon as
their terminal acknowledgement arrives because no data frame follows it. If that
acknowledgement is lost, they use a shorter response timeout than reads; the
timeout is still inconclusive and should be handled with the same verify-by-state
pattern.

Do not blind-retry non-idempotent commands, such as media toggles, volume steps,
or schedule add/remove operations, on timeout alone. The signed-command retry
inside the library can also re-send an identical command after a WAIT status or
epoch/token fault, so verify by absolute state rather than by counting command
attempts.

### Opt-in state verification (`verify_commands`)

Construct a `VehicleBluetooth` with `verify_commands=True` (also accepted by
`vehicles.create(...)` / `vehicles.createBluetooth(...)`, default off) to have
the class resolve that ambiguity for you. Verification runs only on a timeout,
so the normal path - which returns as soon as the terminal ack arrives - keeps
its speed and pays no extra read; the prover read happens only in the ambiguous
case.

When a mutating command times out and its expected post-state can be derived
from its own arguments, the same held connection reads the mapped prover state
and either returns a normal success result (`{"response": {"result": True,
"reason": ""}}`) when the state matches or re-raises the `BluetoothTimeout` when
it does not. The read rides the existing connection and never wakes the vehicle;
if an infotainment prover cannot be read because the car is asleep, the original
timeout is re-raised.

Commands whose outcome cannot be derived or read - true toggles, relative volume
steps, and ack-only actions such as `flash_lights()` or `trigger_homelink()` -
re-raise the timeout unchanged, exactly as with verification off. Currently
verified commands and their provers:

| Command | Prover | Confirmed when |
| --- | --- | --- |
| `door_lock()` / `door_unlock()` | `vehicle_state()` | lock state matches |
| `set_charge_limit(percent)` | `charge_state()` | `charge_limit_soc` matches |
| `set_charging_amps(amps)` | `charge_state()` | `charging_amps` matches |
| `adjust_volume(volume)` | `media_state()` | `audio_volume` matches |
| `set_temps(driver, passenger)` | `climate_state()` | both temp settings match |
| `auto_conditioning_start()` / `auto_conditioning_stop()` | `climate_state()` | `is_climate_on` matches |

The VCSEC lock prover is readable while the vehicle is asleep; the infotainment
provers require the vehicle awake. This feature does not change behavior for any
command not in the table, and it is inert unless `verify_commands=True`.

## Climate Commands

Bluetooth vehicles support the same signed climate command methods as
`VehicleSigned`, including `auto_conditioning_start()`,
`auto_conditioning_stop()`, `set_temps()`, `set_climate_keeper_mode()`,
`set_cabin_overheat_protection()`, `set_cop_temp()`,
`set_bioweapon_mode()`, `set_preconditioning_max()`,
`set_recirculation()`, the remote seat heater/cooler methods, and the
remote steering-wheel heat methods.

Remote seat and steering-wheel comfort commands can be rejected by the vehicle
with `cabin comfort remote settings not enabled` when
`climate_state().remote_heater_control_enabled` is false. That field is a
read-only vehicle setting; the library has no command to enable it.

## Charging Commands

`VehicleBluetooth` inherits the signed-command charging surface. The following
commands send over BLE:

- `charge_start()`
- `charge_stop()`
- `charge_standard()`
- `charge_max_range()`
- `charge_port_door_open()`
- `charge_port_door_close()`
- `set_charge_limit(percent)`
- `set_charging_amps(charging_amps)`
- `set_scheduled_charging(enable, time)`
- `set_scheduled_departure(...)`
- `add_charge_schedule(...)`
- `remove_charge_schedule(id)`
- `batch_remove_charge_schedules(home, work, other)`
- `add_precondition_schedule(...)`
- `remove_precondition_schedule(id)`
- `batch_remove_precondition_schedules(home, work, other)`

`set_scheduled_charging()` and `set_scheduled_departure()` both update the
vehicle's shared `scheduled_charging_mode`. Disabling one mode while the other
is active can turn scheduled charging/departure off entirely, so callers that
toggle either setting should read `charge_state()` first and restore the prior
mode and fields when preserving the other schedule matters.

For signed commands, `set_scheduled_departure()` sends `enable`,
`departure_time`, weekday/all-week recurrence choices, and
`end_off_peak_time`. Its `preconditioning_enabled` and
`off_peak_charging_enabled` arguments are accepted for API compatibility but do
not map to fields in the vehicle's signed-command protobuf.

`charge_standard()` is not treated as a no-op by all vehicles: if the current
charge limit already equals `charge_limit_soc_std`, the vehicle may reject the
command with `already_standard`.

Avoid actuating `charge_port_door_open()` or `charge_port_door_close()` against
a plugged-in vehicle unless someone can reseat the cable if needed.

## Navigation, Dashcam, and Power Commands

`VehicleBluetooth` can send the signed navigation, dashcam, and power-mode
commands over BLE:

- `navigation_request(value)`
- `navigation_gps_request(lat, lon, order)`
- `navigation_sc_request(order)`
- `navigation_waypoints_request(waypoints)`
- `navigation_gps_destination_request(lat, lon, destination, order)`
- `dashcam_save_clip()`
- `flash_lights()`
- `set_keep_accessory_power_mode(on)`
- `set_low_power_mode(on)`

For the GPS navigation methods, `order` is the Tesla/protobuf remote-nav order
integer: `1` replaces the trip, `2` prepends a stop, and `3` appends a stop.
These commands are ACK-only over BLE; the library returns the vehicle's command
acknowledgement, but there is no separate BLE state prover for the navigation
destination, dashcam clip save, flash-lights action, or power-mode toggle.

## Open/Close Individual Doors (Bluetooth Only)

The individual door closure commands are Bluetooth-only and are not available via Fleet API signed commands.
`open_*_door()` unlatches the selected door. `close_*_door()` only means the
vehicle accepted the close request; on vehicles without reliable powered door
close support, the door may remain physically ajar until someone pushes it
shut. Do not rely on an automated open-then-close cycle without checking
`closures_state()` or getting physical confirmation.

Available commands:

- `open_front_driver_door()`
- `close_front_driver_door()`
- `open_front_passenger_door()`
- `close_front_passenger_door()`
- `open_rear_driver_door()`
- `close_rear_driver_door()`
- `open_rear_passenger_door()`
- `close_rear_passenger_door()`

Example:

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth

async def main():
    tesla_bluetooth = TeslaBluetooth()
    await tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    await vehicle.connect()
    await vehicle.open_front_driver_door()
    await vehicle.disconnect()

asyncio.run(main())
```

## Get Vehicle Data

You can get data from a `VehicleBluetooth` instance using the individual state
reader methods. Each reader sends one BLE vehicle-data request and returns the
typed protobuf state from the signed-command reply.

```python
import asyncio
from tesla_fleet_api import TeslaBluetooth

async def main():
    tesla_bluetooth = TeslaBluetooth()
    device = await tesla_bluetooth.find_vehicle()
    private_key = await tesla_bluetooth.get_private_key("path/to/private_key.pem")
    vehicle = tesla_bluetooth.vehicles.create("<vin>")
    charge_state = await vehicle.charge_state()
    print(f"Battery level for VIN {vehicle.vin}: {charge_state.battery_level}")

asyncio.run(main())
```

Available BLE state readers:

- `vehicle_state()`
- `charge_state()`
- `climate_state()`
- `drive_state()`
- `location_state()`
- `closures_state()`
- `charge_schedule_state()`
- `preconditioning_schedule_state()`
- `tire_pressure_state()`
- `media_state()`
- `media_detail_state()`
- `software_update_state()`
- `parental_controls_state()`

For explicit composite requests, use `vehicle_data(endpoints)` with
`BluetoothVehicleData` values:

```python
from tesla_fleet_api import BluetoothVehicleData

data = await vehicle.vehicle_data([BluetoothVehicleData.CHARGE_STATE])
```

Unlike `VehicleFleet.vehicle_data()`, the BLE `vehicle_data()` method requires
an explicit `endpoints` list and returns a `VehicleData` protobuf message, not a
REST JSON `dict`. Prefer the individual state readers, or a single explicit
endpoint, because requesting multiple endpoints together can exceed the
vehicle's signed-command response-size cap and raise
`TeslaFleetMessageFaultResponseSizeExceedsMTU`.

## Media Commands

`VehicleBluetooth` inherits the signed media commands from `Commands`, so media
control methods use the same BLE signed-command transport as other INFO-domain
commands:

- `adjust_volume(volume)`
- `media_volume_up()`
- `media_volume_down()`
- `media_toggle_playback()`
- `media_next_track()`
- `media_prev_track()`
- `media_next_fav()`
- `media_prev_fav()`

`adjust_volume(volume)` accepts absolute volume values from `0.0` through
`11.0`, matching the Fleet API command validation.

These commands return the signed-command acknowledgement, not a media-state
diff. For verification, prefer `media_state().audio_volume` and
`media_state().media_playback_status` where they apply. Track identity fields
such as `now_playing_artist`, `now_playing_title`, and the
`media_detail_state()` now-playing fields can be empty for some media sources,
so track/favorite navigation is best verified by the command acknowledgement and
paired with the inverse command when an exact state fingerprint is unavailable.

If a BLE write times out, re-read the relevant state before assuming whether the
command applied. A timeout while waiting for the GATT write response is not
enough to prove either failure or success.

`remote_boombox(sound)` also uses the INFO-domain signed-command transport and
plays through the vehicle external speaker. Use it only when someone is present
to confirm the sound is appropriate for the vehicle's surroundings.
