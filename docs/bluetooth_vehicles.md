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

`get_private_key(path)` loads an existing EC private key or creates a new
unencrypted PEM key file. Newly created key files are created owner-readable
and owner-writable only (`0600`) from the start, with no write-then-chmod
window, and concurrent creators fall back to reading the file that won the
create race.

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

`wake_up()` is best-effort over BLE: with `raise_unconfirmed=True`, a
`BluetoothUnconfirmedCommand` from the wake request can be a false negative
even when the vehicle wakes successfully (and still matches
`except BluetoothTimeout`). Confirm readiness by retrying a cheap INFO-domain
read, such as `charge_state()`, with backoff. The
infotainment computer can also take longer to become ready than the
vehicle-security computer, so INFO-domain reads immediately after waking should
retry `BluetoothTimeout` with backoff. Keep one BLE connection open across
related commands when possible instead of reconnecting for each command.

`VehicleBluetooth` raises `BluetoothTransportError`, a `TeslaFleetError`
subclass, when the BLE connection, notification setup, or GATT characteristic
resolution fails *before any write reaches the backend* - provably before the
command could have reached the vehicle. The original transport exception is
available as the exception's `__cause__`. Catch `TeslaFleetError` to handle
both transport failures and response-wait timeout failures with one library
error hierarchy, or catch `BluetoothTransportError` separately when you need
to distinguish a provable pre-submission failure from a vehicle timeout after
the command or request may have been written.

A GATT write that enters the backend (D-Bus, CoreBluetooth, an ESPHome proxy)
and then fails or times out - `bleak.exc.BleakError`, or builtin `TimeoutError`
from an ESPHome proxy write timeout - is treated as delivery-ambiguous rather
than a transport failure: field measurements show such writes reaching the
vehicle about as often as not, so it raises `BluetoothTimeout` (or, for a
mutating command, `BluetoothUnconfirmedCommand` through the same ladder as a
lost ack - see "Mutating Command Timeouts" below) instead of
`BluetoothTransportError`. A `Router`/`VehicleRouter` primary-fallback chain
(see the top-level README) must not replay a command on this exception, which
is exactly why it is *not* classified as a transport failure.

A response-wait timeout for a *mutating* command (RKE/closure actions,
HVAC/media/charging commands, `wake_up()`) that stays genuinely unresolved is
handled by the `raise_unconfirmed` knob: the default best-effort mode returns a
success-shaped response, while `raise_unconfirmed=True` raises
`BluetoothUnconfirmedCommand` instead of plain `BluetoothTimeout` - see
"Mutating Command Timeouts" below for the `confirmation` and
`raise_unconfirmed` knobs that shape that outcome. A response-wait timeout for
anything else (a state read) still raises plain `BluetoothTimeout`.
`BluetoothUnconfirmedCommand` subclasses `BluetoothTimeout`, so existing
`except BluetoothTimeout` handling keeps working; catch
`BluetoothUnconfirmedCommand` separately when you need to tell "the command may
have executed" apart from "nothing happened." A mutating command *proven* not
to have taken effect - a `confirmation="verify"` read or a mismatching
broadcast that stood at the end of the wait window - raises
`BluetoothCommandFailed` instead, a distinct type a fallback router fails over
on normally (see below).

BLE response chunks are reassembled with the same stale-frame behavior as
Tesla's vehicle-command BLE connector: if a partial frame sits idle for more
than one second before the next chunk arrives, the partial frame is discarded
before processing the new chunk. This prevents a dropped chunk from corrupting
the next response, but it does not change command acknowledgement timeouts.

## Mutating Command Timeouts

A `BluetoothUnconfirmedCommand` from a mutating BLE command is unconfirmed, not
proof that the command failed. It is raised only when `raise_unconfirmed=True`;
with the default `False`, the same still-ambiguous outcome returns a
best-effort success. The vehicle can apply the command even when its
acknowledgement does not reach the client - `door_lock()`/`door_unlock()` have
both been observed to execute despite this exception. Never blind-retry the
same command, and never replay it on a fallback transport (e.g. a
BLE-primary/cloud fallback router) on this exception alone - see "The
confirmation ladder" below for how the library resolves this for you, and
"Skipping the wait" for the constructor knobs that control how hard it tries.

VCSEC actuations, such as RKE, closure, and wake requests, return as soon as
their terminal acknowledgement arrives because no data frame follows it. If
that acknowledgement is lost, they use a shorter response timeout than reads.

Do not blind-retry non-idempotent commands, such as media toggles, volume steps,
or schedule add/remove operations, on timeout alone. The signed-command retry
inside the library can also re-send an identical command after a WAIT status or
epoch/token fault, so verify by absolute state rather than by counting command
attempts.

### The confirmation ladder

A mutating BLE command tries to confirm itself in up to four steps: write the
GATT characteristic, wait for the addressed ack (racing a matching state
broadcast for lock/unlock), fall back to a state read, then decide the final
outcome. `confirmation` (constructor/factory arg, default `"ack"`) picks how
many of those steps run; `raise_unconfirmed` (default `False`) picks what the
last step does when nothing above it settled the question.

| Rung | Runs under | On success | On failure/ambiguity |
| --- | --- | --- | --- |
| GATT write | every level, incl. `"optimistic"` | proceeds to the next rung (or returns, under `"optimistic"`) | pre-submission (e.g. characteristic not found): `BluetoothTransportError`, always raises. Submitted-then-failed/timed-out: ambiguous, races any armed broadcast watcher, then falls to the "genuinely unresolved" outcome below |
| Addressed ack + broadcast race (lock/unlock only) | `"ack"`, `"verify"` | returns a confirmed result | a proven mismatch at window end raises `BluetoothCommandFailed`; a lost ack with nothing else confirming falls to the next rung |
| State-read verification | `"verify"` only | returns a confirmed result | a proven mismatch raises `BluetoothCommandFailed`; an unreadable prover (e.g. asleep car) falls to the next rung |
| Genuinely unresolved outcome | every level | - | `raise_unconfirmed=False` (default): best-effort success. `raise_unconfirmed=True`: raises `BluetoothUnconfirmedCommand` |

The GATT write rung's ambiguous case is not hypothetical: field measurements
of write-level transport errors found some had already executed on the
vehicle despite the local write call failing, so a submitted-then-ambiguous
write is deliberately routed into the same unresolved-outcome handling as a
lost ack rather than treated as a safe-to-retry transport failure.

**Broadcast confirmation (lock/unlock, `"ack"` and `"verify"`).** The vehicle
keeps emitting unsolicited VCSEC status broadcasts on the same notification
subscription even when it emits no addressed ack for a lock/unlock actuation.
`VehicleBluetooth` races the ack wait against a matching broadcast and returns
success as soon as either confirms - so most ack losses for lock/unlock now
resolve to a real confirmed success well before the ack-wait ceiling, with no
extra read. A broadcast showing a different state does not fail fast (a later
broadcast in the same window could still confirm success), but if the whole
window elapses with such a mismatch as the last word and nothing else
confirming, that is proof the command did not apply and raises
`BluetoothCommandFailed` rather than the ambiguous timeout.

**State-read verification (`confirmation="verify"`).** When a mutating command
still hasn't resolved after the ack/broadcast wait and its expected post-state
can be derived from its own arguments, the same held connection reads the
mapped prover state and either returns a normal success result
(`{"response": {"result": True, "reason": ""}}`) when the state matches or
raises `BluetoothCommandFailed` when a completed read does not match. The read
rides the existing connection and never wakes the vehicle; if an infotainment
prover cannot be read because the car is asleep, the outcome stays unresolved
and falls through to `raise_unconfirmed`. This runs only under
`confirmation="verify"` and only on a still-unresolved wait, so the normal
path - which returns as soon as something confirms - keeps its speed.

Verified commands and their provers:

| Command | Prover | Confirmed when |
| --- | --- | --- |
| `door_lock()` / `door_unlock()` | `vehicle_state()` | lock state matches |
| `set_charge_limit(percent)` | `charge_state()` | `charge_limit_soc` matches |
| `set_charging_amps(amps)` | `charge_state()` | `charging_amps` matches |
| `adjust_volume(volume)` | `media_state()` | `audio_volume` matches |
| `set_temps(driver, passenger)` | `climate_state()` | both temp settings match |
| `auto_conditioning_start()` / `auto_conditioning_stop()` | `climate_state()` | `is_climate_on` matches |

The VCSEC lock prover is readable while the vehicle is asleep; the infotainment
provers require the vehicle awake. Broadcast confirmation covers only
`door_lock()`/`door_unlock()` - the only commands with an observed status
broadcast; every other command in the table is reliably confirmed only under
`confirmation="verify"`. Commands not in the table - true toggles, relative
volume steps, and ack-only actions such as `flash_lights()` or
`trigger_homelink()` - are the documented best-effort set: they have no
broadcast and no prover to confirm against, so a still-unresolved wait always
falls through to `raise_unconfirmed` regardless of `confirmation`.

### Skipping the wait (`confirmation="optimistic"`) and defaulting to success (`raise_unconfirmed`)

- `confirmation="optimistic"` returns success as soon as the GATT write is
  confirmed, consulting nothing else for every mutating command. This is pure
  speed mode: the caller owns any state verification it wants afterward. A
  write provably rejected before submission (`BluetoothTransportError`) always
  raises; a submitted-then-ambiguous write instead follows `raise_unconfirmed`
  like every other rung, since even this mode must not let a fallback router
  blind-retry a command that may already have reached the car. `ping()` (the
  one non-mutating infotainment send) is exempt and always waits for its real
  reply.
- `raise_unconfirmed=True` changes what happens only when the whole ladder is
  exhausted without a definite answer - the ack/broadcast wait timed out and,
  under `confirmation="verify"`, the prover read itself could not complete
  (e.g. the car is asleep) - or the GATT write itself entered backend I/O and
  then failed/timed out with delivery unprovable either way. Instead of the
  default best-effort success (`{"response": {"result": True, "reason": ""}}`),
  that ambiguous case raises `BluetoothUnconfirmedCommand`. A car-side
  rejection carried in an ack, any proven non-application
  (`BluetoothCommandFailed`), and a write provably rejected before submission
  (`BluetoothTransportError`) are unaffected and always raise - this flag
  converts only the "could not determine what happened" outcome, and applies
  under every `confirmation` level including `"optimistic"`.

```python
vehicle = tesla_bluetooth.vehicles.create(
    "<vin>", confirmation="optimistic"
)
# or, to confirm as hard as possible but still never raise on a genuinely
# inconclusive outcome:
vehicle = tesla_bluetooth.vehicles.create(
    "<vin>", confirmation="verify", raise_unconfirmed=False  # raise_unconfirmed=False is also the default
)
```

`verify_commands`/`optimistic` booleans are still accepted as deprecated
constructor/factory aliases for `confirmation="verify"` /
`confirmation="optimistic"` - passing either emits a `DeprecationWarning` and
maps onto `confirmation`. A positional boolean in the `confirmation` slot is
also treated as the old positional `verify_commands` value. Prefer
`confirmation` directly in new code.

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
- `navigation_gps_request(lat, lon, order=0)`
- `navigation_sc_request(order)`
- `navigation_waypoints_request(waypoints)`
- `navigation_gps_destination_request(lat, lon, destination, order)`
- `dashcam_save_clip()`
- `flash_lights()`
- `set_keep_accessory_power_mode(on)`
- `set_low_power_mode(on)`

For the GPS navigation methods, `order` is the Tesla/protobuf remote-nav order
integer: `1` replaces the trip, `2` prepends a stop, and `3` appends a stop.
`navigation_gps_request`'s `order` defaults to `0`
(`REMOTE_NAV_TRIP_ORDER_UNKNOWN`) when omitted, matching the cloud path.
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

## Broadcast Listeners

The vehicle's VCSEC computer emits unsolicited `VehicleStatus` broadcasts on
the same BLE notification subscription used for command replies, independent
of any command you send. `VehicleBluetooth` fans these out to persistent
per-field listeners, so you can receive vehicle-state changes passively
instead of polling the state readers above.

Each modeled `VehicleStatus` leaf field has its own typed listener method,
similar in spirit to
[python-teslemetry-stream](https://github.com/Teslemetry/python-teslemetry-stream)'s
`listen_<Field>` surface:

- `listen_vehicle_lock_state(callback)` - `VehicleLockState_E`
- `listen_vehicle_sleep_status(callback)` - `VehicleSleepStatus_E`
- `listen_user_presence(callback)` - `UserPresence_E`
- `listen_gear(callback)` - `Gear_E`
- `listen_ui_desire(callback)` - `UIDesire_E`
- `listen_front_driver_door(callback)` - `ClosureState_E`
- `listen_front_passenger_door(callback)` - `ClosureState_E`
- `listen_rear_driver_door(callback)` - `ClosureState_E`
- `listen_rear_passenger_door(callback)` - `ClosureState_E`
- `listen_front_trunk(callback)` - `ClosureState_E`
- `listen_rear_trunk(callback)` - `ClosureState_E`
- `listen_charge_port(callback)` - `ClosureState_E`
- `listen_tonneau(callback)` - `ClosureState_E`
- `listen_tonneau_percent_open(callback)` - `int`

Each `listen_*` method takes a synchronous `callback(value)` and returns an
`unsubscribe()` closure:

```python
def on_lock_state(state):
    print(f"Lock state: {state}")

unsubscribe = vehicle.listen_vehicle_lock_state(on_lock_state)
...
unsubscribe()
```

The door/trunk/charge-port/tonneau listeners and `listen_tonneau_percent_open`
only fire on broadcasts that actually carry the corresponding submessage
(`closureStatuses`/`detailedClosureStatus`) - not every status broadcast
includes them. `listen_vehicle_lock_state`, `listen_vehicle_sleep_status`,
`listen_user_presence`, `listen_gear`, and `listen_ui_desire` fire on every
`VehicleStatus` broadcast, since proto3 gives no presence tracking for a
scalar enum field.

Anything not decoded into `VehicleStatus` - other VCSEC broadcast payloads
(`CommandStatus`, whitelist events, faults) and any future
infotainment-domain broadcast - has no typed listener surface. Use the untyped
`listen_broadcast`, which delivers every raw unsolicited `RoutableMessage` for
a given `Domain`, including decoded `VehicleStatus` broadcasts:

```python
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import Domain

unsubscribe = vehicle.listen_broadcast(Domain.DOMAIN_VEHICLE_SECURITY, print)
```

Listeners are plain Python callables registered on the `VehicleBluetooth`
instance - they persist across reconnects and are torn down only by calling
the `unsubscribe()` closure returned at registration.
Callback exceptions are logged and do not stop later listeners or normal
message routing; `KeyboardInterrupt` and `SystemExit` still propagate.

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

If a BLE command is still ambiguous after the write, re-read the relevant state
before assuming whether the command applied. A `BluetoothUnconfirmedCommand`
(when `raise_unconfirmed=True`) is not enough to prove either failure or
success.

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
REST responses that are valid JSON but not objects, such as `null`, lists, or
scalars, are returned unchanged and log as `result=success`.
For BLE commands run with `confirmation="verify"`, a resolved state-read logs a
second line with `verify_commands=resolved` and the confirmed result; an
unresolved read logs `verify_commands=unresolved` before the exception
propagates (`BluetoothCommandFailed` on a proven mismatch,
`BluetoothUnconfirmedCommand` if the read itself couldn't complete). With
`raise_unconfirmed=False` (the default), an exhausted ladder logs
`raise_unconfirmed=False result=success (best-effort)` instead of raising
`BluetoothUnconfirmedCommand`. `Router` additionally logs
`command=... backend=<ClassName> result=...` for each backend it tries, or
`result=unconfirmed` when it stops instead of failing over, so a
BLE-primary/cloud-fallback setup shows exactly which backend served each call
and why a failover happened.
