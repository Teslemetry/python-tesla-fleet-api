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

## Keeping the Connection Alive (`keepalive_interval`)

An idle held BLE link to the vehicle drops on its own after roughly 42 seconds
on average. To hold it open, `VehicleBluetooth` issues a minimal passive GATT
read (of the version characteristic - never a command, never anything signed or
mutating) after `keepalive_interval` seconds without traffic. A single such read
every 20 seconds keeps the link alive about ten times longer.

The keepalive is idle-triggered: any real send or received frame resets the
timer, so an active session never gets extra traffic and the read fires only
during genuine idleness. It is bounded and best-effort - a read that cannot
complete (for example against a sleeping car) is swallowed and never raises into
your code or forces a reconnect, and it never wakes the vehicle or masks a
sleeping car. Link recovery stays owned by the normal reconnect path.

`keepalive_interval` defaults to about 20 seconds and is accepted by the
constructor and by `vehicles.create(...)` / `vehicles.createBluetooth(...)`.
Pass `None` or `0` to disable it.

```python
vehicle = tesla_bluetooth.vehicles.create("<vin>", keepalive_interval=20.0)
# or disable it:
vehicle = tesla_bluetooth.vehicles.create("<vin>", keepalive_interval=None)
```

Tradeoff: because these reads generate link traffic, they keep an already-awake
car awake and defer vehicle sleep. If you want the vehicle to sleep while idle,
disable keepalive or disconnect when you have no work for it.

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

`pair()` waits for the tap-to-approve on the vehicle: it returns as soon as the
whitelist success reply arrives, but also polls whether the key became effective
(every `poll_interval` seconds, default 5) up to an overall `timeout` (default
300 seconds), so it still completes if that one-shot reply is lost to a BLE
reconnect while you walk to the car. It raises `BluetoothTimeout` if neither
confirms in time.

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

`wake_up()` is best-effort over BLE: a `BluetoothUnconfirmedCommand` from the
wake request can be a false negative even when the vehicle wakes successfully
(and still matches `except BluetoothTimeout`). Confirm readiness by retrying a
cheap INFO-domain read, such as `charge_state()`, with backoff. The
infotainment computer can also take longer to become ready than the
vehicle-security computer, so INFO-domain reads immediately after waking should
retry `BluetoothTimeout` with backoff. Keep one BLE connection open across
related commands when possible instead of reconnecting for each command.

`VehicleBluetooth` raises `BluetoothTransportError`, a `TeslaFleetError`
subclass, when the BLE connection, notification setup, or GATT command write
fails before a vehicle response can be awaited. The original transport
exception is available as the exception's `__cause__`; this includes
`bleak.exc.BleakError` and builtin `TimeoutError` from ESPHome proxy connect,
notify, or write timeouts. Catch `TeslaFleetError` to handle both transport
failures and response-wait timeout failures with one library error hierarchy,
or catch `BluetoothTransportError` separately when you need to distinguish a
transport failure - the command never reached the vehicle - from a vehicle
timeout after the command or request was written.

A response-wait timeout for a *mutating* command (RKE/closure actions,
HVAC/media/charging commands, `wake_up()`) raises `BluetoothUnconfirmedCommand`
instead of plain `BluetoothTimeout` - see "Mutating Command Timeouts" below. A
response-wait timeout for anything else (a state read) still raises plain
`BluetoothTimeout`. `BluetoothUnconfirmedCommand` subclasses `BluetoothTimeout`,
so existing `except BluetoothTimeout` handling keeps working; catch
`BluetoothUnconfirmedCommand` separately when you need to tell "the command may
have executed" apart from "nothing happened."

BLE response chunks are reassembled with the same stale-frame behavior as
Tesla's vehicle-command BLE connector: if a partial frame sits idle for more
than one second before the next chunk arrives, the partial frame is discarded
before processing the new chunk. This prevents a dropped chunk from corrupting
the next response, but it does not change command acknowledgement timeouts.

## Mutating Command Timeouts

A `BluetoothUnconfirmedCommand` from a mutating BLE command is unconfirmed, not
proof that the command failed. The vehicle can apply the command even when its
acknowledgement does not reach the client - `door_lock()`/`door_unlock()` have
both been observed to execute despite this exception. For commands that change
vehicle state, snapshot the relevant state before acting and verify the outcome
with a follow-up state read after any timeout. Never blind-retry the same
command, and never replay it on a fallback transport (e.g. a BLE-primary/cloud
fallback router) - the safe response to an unconfirmed outcome is to verify, not
to retry.

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
"reason": ""}}`) when the state matches or re-raises the
`BluetoothUnconfirmedCommand` when it does not. The read rides the existing
connection and never wakes the vehicle; if an infotainment prover cannot be
read because the car is asleep, the unconfirmed command timeout is re-raised.

Commands whose outcome cannot be derived or read - true toggles, relative volume
steps, and ack-only actions such as `flash_lights()` or `trigger_homelink()` -
raise `BluetoothUnconfirmedCommand`, exactly as with verification off. Currently
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

### Skipping the wait (`optimistic`) and defaulting to success (`raise_unconfirmed`)

The full confirmation ladder for a mutating BLE command is: write the GATT
characteristic, wait for the ack, resolve via `verify_commands` on a timeout,
then decide the final outcome. Two more constructor/factory knobs (default off
and default on, respectively - both preserve today's behavior unless set)
shape that last step:

- `optimistic=True` returns success as soon as the GATT write is confirmed,
  skipping the ack wait and `verify_commands` entirely for every mutating
  command. This is pure speed mode: the caller owns any state verification it
  wants afterward. Only a write/transport failure (`BluetoothTransportError`)
  still raises. `ping()` (the one non-mutating infotainment send) is exempt
  and always waits for its real reply.
- `raise_unconfirmed=False` changes what happens only when the ladder is
  exhausted without a definite answer - `verify_commands` is off, has no plan
  for this command, or its prover read itself could not complete (e.g. the
  car is asleep). Instead of raising `BluetoothUnconfirmedCommand`, that
  ambiguous case resolves as a best-effort success
  (`{"response": {"result": True, "reason": ""}}`). A car-side rejection
  carried in an ack, a `verify_commands` state mismatch (the prover read
  completed and does not show the requested value), and write failures are
  unchanged and always raise - this flag converts only the "could not
  determine what happened" outcome.

Commands with no `verify_commands` plan - true toggles, relative volume steps,
and ack-only actions such as `flash_lights()` or `trigger_homelink()` (every
command not in the table above) - have nothing to mismatch against, so under
`raise_unconfirmed=False` a timeout on any of them always resolves best-effort.
Treat those commands as best-effort by design; rely on `verify_commands`'s
table for a reliable, state-backed confirmation on the commands it covers.

```python
vehicle = tesla_bluetooth.vehicles.create(
    "<vin>", optimistic=True
)
# or, to keep waiting for an ack but never raise on an inconclusive outcome:
vehicle = tesla_bluetooth.vehicles.create(
    "<vin>", verify_commands=True, raise_unconfirmed=False
)
```

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

If a BLE command times out after the write, re-read the relevant state before
assuming whether the command applied. A `BluetoothUnconfirmedCommand` is not
enough to prove either failure or success.

`remote_boombox(sound)` also uses the INFO-domain signed-command transport and
plays through the vehicle external speaker. Use it only when someone is present
to confirm the sound is appropriate for the vehicle's surroundings.

## Troubleshooting: Enable Debug Logging

Enable the `tesla_fleet_api` logger at `DEBUG` to see, for every command, which
transport served it and how it ended:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("tesla_fleet_api").setLevel(logging.DEBUG)
```

Each command logs one terse, grep-friendly line:

```
command=RKE_ACTION_LOCK transport=bluetooth result=True reason=
command=set_charge_limit transport=teslemetry result=True reason=
command=mediaPlayAction transport=bluetooth result=error error=BluetoothUnconfirmedCommand: Bluetooth command timed out waiting for an ack after being written to the vehicle; it may have executed anyway.
```

`transport` is `bluetooth`, `fleet`, `teslemetry`, or `tessie`. For BLE signed
commands, `command` is the underlying VCSEC/infotainment field name (e.g.
`RKE_ACTION_LOCK`, `chargingSetLimitAction`), not the Python method name; for
REST commands it is the endpoint's final path segment (e.g. `set_charge_limit`).
For BLE commands run with `verify_commands=True`, a resolved timeout logs a
second line with `verify_commands=resolved` and the confirmed result; an
unresolved timeout logs `verify_commands=unresolved` before the
`BluetoothUnconfirmedCommand` propagates. With `raise_unconfirmed=False`, an
exhausted ladder logs `raise_unconfirmed=False result=success (best-effort)`
instead of propagating that exception. `Router` additionally logs
`command=... backend=<ClassName> result=...` for each backend it tries, or
`result=unconfirmed` when it stops instead of failing over, so a
BLE-primary/cloud-fallback setup shows exactly which backend served each call
and why a failover happened.
