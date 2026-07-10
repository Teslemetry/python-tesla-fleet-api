## Project Overview

Python library (`tesla_fleet_api`) providing async interfaces for Tesla Fleet API, Teslemetry, and Tessie services, plus BLE communication. Published to PyPI as `tesla-fleet-api`.

## Development Commands

```bash
# Install dependencies
uv sync

# Type checking (strict mode)
uv run pyright tesla_fleet_api

# Linting
uv run ruff check tesla_fleet_api
uv run ruff format tesla_fleet_api

# Tests
uv run pytest tests
```

Tests live in `tests/` and use `unittest.IsolatedAsyncioTestCase` (collected and
run natively by pytest — `pytest-asyncio` is not required).

BLE command tests over a mocked transport build on `tests/ble_mocked_transport.py`
(`MockedBleTransportTestCase`): it patches `VehicleBluetooth._send` and
pre-marks both signed-command sessions ready, so a test drives any inherited
`Commands` method with no real BLE/GATT connection and asserts on the signed
`RoutableMessage` built (`decrypt_sent_command`) and on canned replies
(`vcsec_ok_reply`/`infotainment_action_ok_reply`/`infotainment_vehicle_data_reply`).
See `tests/test_ble_mocked_commands.py` for worked examples.

## API References

- Tesla Fleet: https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints
- Tessie: https://developer.tessie.com/llms.txt
- Teslemetry: http://api.teslemetry.com/openapi.yaml

## Architecture

### Class Hierarchy

Three API client classes all inherit from `TeslaFleetApi`:

```
Tesla (base - tesla/tesla.py)
  └── TeslaFleetApi (tesla/fleet.py) - core HTTP client with _request(), access_token handling
        ├── TeslaFleetOAuth (tesla/oauth.py) - adds OAuth flow (login URL, token refresh)
        ├── Teslemetry (teslemetry/teslemetry.py) - fixed server, Teslemetry-specific endpoints
        └── Tessie (tessie/tessie.py) - fixed server, Tessie-specific endpoints
```

`Tesla` base holds EC key management for signed commands. `TeslaFleetApi` provides the `_request()` method used by all submodules.

### Vehicle Command Layers

Vehicle commands have three implementations sharing the same method signatures, selected by how you create the vehicle:

```
Vehicle (vehicle/vehicle.py) - base with VIN and model detection
  └── VehicleFleet (vehicle/fleet.py) - REST API commands (unsigned)
        └── VehicleSigned (vehicle/signed.py) - signed command protocol via Fleet API
Commands (vehicle/commands.py) - protobuf-based signed command implementation (ABC)
  └── VehicleSigned - multiple inheritance: Commands + VehicleFleet
  └── VehicleBluetooth (vehicle/bluetooth.py) - BLE transport for signed commands
```

`VehicleSigned` uses multiple inheritance: `Commands` for signed command logic, `VehicleFleet` for data endpoints and fallback.

`Router` (router.py) is an entity-agnostic composition wrapper (not part of the inheritance chain) that chains an ordered list of two-or-more backends sharing a common method surface and dispatches each method call down the chain with automatic per-command failover: it tries the first backend that has the method and, on any exception, retries the same call on the next backend that has it, returning the first success (raising the last error only if every applicable backend fails, `AttributeError` only if none has the method). Non-callable attributes resolve to the first backend that has them. The constructor is `Router(primary, secondary, *more_backends, health=None)` — the two-argument form is fully backward compatible. The health check (`bool` | sync callable | async callable returning `bool`; omitted = attempt primary, fail over on exception with no probe) gates **only the primary** (the first backend); the rest of the chain is reached purely through per-command failover — there is deliberately no per-backend health matrix. Note the double-execution caveat: a non-idempotent command that fails mid-flight can be re-run on the next backend.

`VehicleRouter` and `EnergySiteRouter` are thin entity-specific subclasses of `Router`. `VehicleRouter(bluetooth_primary, teslemetry_secondary)` pairs a `VehicleBluetooth` primary with a cloud (`TeslemetryVehicle`) secondary; `EnergySiteRouter(local_energysite, teslemetry_energysite)` pairs a duck-typed local `EnergySite`-shaped object (e.g. aiopowerwall's `PowerwallEnergySite`, no dependency added) with a cloud `TeslemetryEnergySite` fallback. All three live in the top-level `router/` package — `Router` (and shared helpers) in `router/base.py`, `VehicleRouter` in `router/vehicle.py`, `EnergySiteRouter` in `router/energysite.py`, re-exported from `router/__init__.py` (importable as `tesla_fleet_api.router.Router` etc.) and, for backward compatibility, also re-exported from `tesla/__init__.py` (`tesla_fleet_api.tesla.Router`). They have no factory on the `Vehicles`/`EnergySites` collections.

### Vehicle Collections

`Vehicles` (vehicle/vehicles.py) is a `dict[str, Vehicle]` with factory methods:
- `createFleet(vin)` → `VehicleFleet`
- `createSigned(vin)` → `VehicleSigned`
- `createBluetooth(vin)` → `VehicleBluetooth`

Teslemetry/Tessie override `Vehicles` with their own vehicle classes (`TeslemetryVehicle`, `TessieVehicle`) extending `VehicleFleet` with service-specific commands (e.g., `closure()`, `seat_heater()` for Teslemetry; `wake()`, `lock()` for Tessie).

### Submodule Pattern

Each API client lazily attaches submodules in `__init__` via class attributes on `Tesla`:
- `charging`, `energySites`, `user`, `partner`, `vehicles`

Scope flags on `TeslaFleetApi.__init__` control which submodules are instantiated.

### Shared Utilities

`util.py` holds small, dependency-free helpers shared across the library, re-exported from the top-level package. `firmware_compare(a, b) -> int` compares dotted, numeric, week-based Tesla firmware version strings (e.g. `2025.14.3`) correctly — plain string comparison misorders them (`"2025.10" < "2025.9"`). It returns 1/-1/0, right-pads shorter versions with zeros before comparing, and treats unparseable strings (e.g. `"Unknown"`) as sorting behind any parseable version. `firmware_at_least(firmware, minimum) -> bool` is a thin wrapper (`firmware_compare(firmware, minimum) >= 0`) for the common "does this vehicle's firmware support feature X" gate — ported from Home Assistant core PR #175745, which fixed the same lexicographic bug in the `teslemetry` integration. Deliberately implemented as native tuple comparison rather than taking on an `AwesomeVersion` dependency, matching this library's narrow, purpose-built dependency list (no general-purpose version-parsing lib elsewhere).

### Release Process

No release-please or version-bump automation. To ship: bump `version` in `pyproject.toml` and `__version__` in `tesla_fleet_api/__init__.py` in a `Bump version to X.Y.Z` commit on `main`, then push a matching `vX.Y.Z` tag. `.github/workflows/python-publish.yml` runs on every push but only builds+publishes to PyPI (and creates a GitHub Release) when `github.ref` starts with `refs/tags/` — pushing the tag is what actually ships the release; merging to `main` alone does not.

### Error Handling

`exceptions.py` maps HTTP status codes and error keys to specific exception classes. `raise_for_status()` parses responses and raises the appropriate exception. Signed command faults have separate hierarchies: `TeslaFleetInformationFault`, `TeslaFleetMessageFault`, `SignedMessageInformationFault`, `WhitelistOperationStatus`.

All exceptions inherit from `TeslaFleetError(BaseException)`, deliberately **not** `Exception` — a bare `except Exception` (e.g. in retry/backoff loops around BLE reads) silently fails to catch `BluetoothTimeout` and every other library error. Catch `TeslaFleetError` (or `BaseException`) explicitly. `VehicleBluetooth` wraps transport-layer failures (`connect`/`connect_if_needed`, notification setup, the GATT write in `_send`) in `BluetoothTransportError`, a `TeslaFleetError` subclass chaining the original transport exception as its cause — so `except TeslaFleetError` alone now catches BLE transport failures too, not just the response-wait `BluetoothTimeout`. These catch sites deliberately catch **both** `bleak.exc.BleakError` and builtin `TimeoutError`: bleak-esphome converts an aioesphomeapi GATT/connect/notify timeout into a bare `TimeoutError` (not a `BleakError`), which would otherwise escape the wrap as a non-`TeslaFleetError`.

### Protobuf

Source protobuf definitions live in `proto/`; generated Python files live in `tesla_fleet_api/tesla/vehicle/proto/` and are excluded from ruff and pyright. Do not edit generated `*_pb2.py`/`*_pb2.pyi` files directly — update the source `.proto`, add new files to the `PROTOS` list and import-rewrite set in `tools/regenerate_protos.sh`, then regenerate (needs `protoc` on `PATH`). If a new generated module is added, also update the hand-maintained `tesla_fleet_api/tesla/vehicle/proto/__init__.pyi` export stub.

**Runtime-version pin (Home Assistant compatibility).** The gencode stamps a `ValidateProtobufRuntimeVersion(major, minor, patch, …)` call, and protobuf refuses to load gencode that is *newer* than the installed runtime (`gencode X > runtime` → `VersionError`). Home Assistant core pins `protobuf==6.32.0`, so the gencode must be stamped **≤ 6.32.0** or it breaks in HA. The generator version is the `protoc` version: under unified protobuf versioning, `protoc vX.Y` (`libprotoc X.Y`) stamps Python gencode `6.X.Y`. So to target runtime 6.32.0, regenerate with **protoc v32.0** (`protoc-32.0-linux-x86_64.zip` from the protobuf GitHub releases). The `protobuf>=6.32.0` floor in `pyproject.toml` must match the gencode version — never set it below the stamped version, or installs that resolve an older protobuf will hit `VersionError` at import.

## Code Style

- **Type checking**: pyright strict mode. Use `TYPE_CHECKING` guards for circular imports.
- **Linting**: ruff (proto files excluded).
- **Async**: All API methods are `async`. Uses `aiohttp` for HTTP, `aiofiles` for file I/O, `bleak` for BLE.
- **Enums**: Custom `StrEnum`/`IntEnum` in `const.py` (not stdlib). `Region` is a `Literal["na", "eu", "cn"]`, not an enum.
- **Seat indexing gotcha**: two distinct seat enums with different conventions. `Seat` is **0-indexed** (`FRONT_LEFT=0`) and is for the manual seat heater/cooler paths (`remote_seat_heater_request`, `remote_seat_cooler_request`). `AutoSeat` is **1-indexed** (`FRONT_LEFT=1`, `FRONT_RIGHT=2`) and is the correct type for `remote_auto_seat_climate_request` on **both** backends — its values equal Tesla's REST wire values and the proto `AutoSeatPosition_*` enum. Don't mix them; passing a `Seat` to the auto-climate command is off-by-one (issue #11).
- **Naming**: camelCase for class instance attributes that mirror API structure (`energySites`, `createFleet`). Snake_case for method names that are API endpoints.
- **BLE discovery gotcha**: a Tesla vehicle advertises no 128-bit service UUID pre-connect — only its VIN-derived local name (`^S[a-f0-9]{16}[CDRP]$`), and only in the scan response, not the `ADV_IND`. `SERVICE_UUID` (`tesla_fleet_api/tesla/vehicle/bluetooth.py`) exists only as a GATT service after connecting. Never pass `service_uuids=[SERVICE_UUID]` as a `BleakScanner` discovery-time filter — it hides the vehicle on a direct BlueZ adapter (an ESPHome proxy doesn't enforce that filter the same way, which can mask the bug in testing). Scan unfiltered with active scanning and match by name; keep `SERVICE_UUID` for post-connect GATT use only.
- **BLE domain-routing gotcha**: `Domain` (`proto/universal_message.proto`) has more values (`DOMAIN_BROADCAST`, `DOMAIN_AUTHD`, ...) than `VehicleBluetooth._queues` has keys (only `DOMAIN_VEHICLE_SECURITY`/`DOMAIN_INFOTAINMENT`). `_on_message` (`tesla_fleet_api/tesla/vehicle/bluetooth.py`) must look up `_queues` with `.get()` and drop unrecognized domains rather than indexing directly — indexing raises `KeyError` inside the `ReassemblingBuffer` callback, aborting reassembly of any further already-buffered messages in that notification.
- **BLE infotainment boot-delay gotcha**: `wake_up()` (VCSEC) returns as soon as the vehicle-security computer acks it, well before the infotainment computer is ready to complete a signed-command handshake. An INFO-domain read/command issued immediately after `wake_up()` can raise `BluetoothTimeout` on the handshake through no fault of the command itself. Live-verified: waiting ~10s after `wake_up()` before the first INFO read is sufficient on the test rig; callers doing INFO work right after waking should retry-with-backoff rather than treat one timeout as failure.
- **BLE `vehicle_data()` response-size cap**: the vehicle's signed-command implementation enforces its own response-size limit independent of the BLE transport's packet reassembly. Live-verified: a single-endpoint `vehicle_data()` call (or any of the dedicated per-substate readers like `charge_state()`) succeeds, but requesting as few as two `BluetoothVehicleData` endpoints together reliably raises `TeslaFleetMessageFaultResponseSizeExceedsMTU` (`exceptions.py`). This is why `vehicle_data()`'s `endpoints` arg has no all-endpoints default (unlike the cloud method) - prefer the per-substate readers, or a single-endpoint `vehicle_data()` call, over a multi-endpoint composite. Auto-chunking (split under the cap, merge replies) would fix this properly but is not implemented.
- **BLE individual-door powered-close gotcha**: `open_*_door()` unlatches a door over VCSEC; on a Model 3 there is no reliable powered close. Live-verified: `close_rear_passenger_door()` returned an OK ack (`{"result": True}`) but `closures_state().door_open_passenger_rear` stayed `True` - the ack only means the car accepted the command, not that the door physically re-latched (a human has to push it shut). Never chain an automated snapshot→act→verify→restore cycle across an individual door-open command; treat the 8 door commands as ack-verified only, or require a human to confirm the physical re-close before trusting `closures_state()` again.
- **`remote_heater_control_enabled` gate**: `climate_state().remote_heater_control_enabled` is a read-only vehicle-side setting (no command exists to flip it) that gates every "remote comfort" action - live-verified on `commands.py`: `remote_seat_heater_request`, `remote_auto_seat_climate_request`, `remote_steering_wheel_heater_request`, `remote_steering_wheel_heat_level_request`, `remote_auto_steering_wheel_heat_climate_request`. With it `false`, the vehicle ACKs `{"result": false, "reason": "cabin comfort remote settings not enabled"}` and leaves state untouched (not a library bug, not a partial mutation) - this is presumably the touchscreen/app "Remote Climate" or comfort-access toggle, outside this library's command surface. Check this field before treating a comfort-command rejection as a regression.
- **Protobuf oneof-by-string-kwargs bypasses pyright**: `remote_seat_heater_request`/`remote_seat_cooler_request` (`commands.py`) build their `HvacSeatHeaterAction`/`HvacSeatCoolerAction` via a `dict` of literal field-name strings expanded as `**kwargs` into the message constructor (with a `# pyright: ignore[reportUnknownArgumentType]` already on the call) - a typo in one of those strings (e.g. `SEAT_HEATER_MEDIUM` vs. the proto's actual `SEAT_HEATER_MED`, fixed live during PR-4) raises at call time, not at type-check time. Cross-check any new field-name string against the proto (`proto/car_server.proto`) rather than trusting pyright to catch it.
- **`scheduled_charging_mode` is tri-state and shared**: `set_scheduled_charging` and `set_scheduled_departure` (`commands.py`) both write the same `ChargeState.scheduled_charging_mode` (Off/StartAt/DepartBy) - live-verified. Disabling one when the other is active turns the whole feature Off rather than leaving the other's config intact; a caller toggling one must read `charge_state()` first and restore the exact prior mode (including the other command's fields) rather than assuming independence.
- **`set_scheduled_departure`'s `preconditioning_enabled`/`off_peak_charging_enabled` args are dead**: live-verified - `ScheduledDepartureAction` (`proto/car_server.proto`) has no fields for them, only `preconditioning_times`/`off_peak_charging_times` (weekday-recurrence only, no on/off). Passing `preconditioning_enabled=False` has no effect on the vehicle's observed state. Not a library bug to "fix" without a wider protocol capability; document, don't rely on these args to gate the feature.
- **`charge_standard()` rejects `already_standard`**: live-verified - calling it while `charge_state().charge_limit_soc` already equals `charge_limit_soc_std` gets `{"result": False, "reason": "already_standard"}` rather than a no-op success. Not a library bug; callers/tests exercising this command need the limit to actually differ from the std preset first (e.g. via `charge_max_range()` or `set_charge_limit()`).
- **BLE media state-observability gotcha**: `MediaState.now_playing_artist/title` and all of `MediaDetailState` (`now_playing_album/station/source_string/elapsed/duration`) were observed empty/zero on the test car while Spotify was actively `Playing` at nonzero volume - these legacy fields are apparently only populated for certain sources (e.g. USB/Bluetooth), not Spotify. Don't assume `media_next_track`/`media_prev_track`/`media_next_fav`/`media_prev_fav` are state-observable via these readers; verify by ACK (`{"result": True}`) and pair with the inverse command when the fingerprint doesn't change. `audio_volume`/`media_playback_status` (for `adjust_volume`/`media_volume_up`/`media_volume_down`/`media_toggle_playback`) were populated correctly and are reliable provers.
- **BLE mutating-command timeout is inconclusive - never assume "the write didn't land"**: this corrects an earlier version of this note, which observed `adjust_volume` write timeouts on one rig leaving the car unmutated and concluded a write timeout means the write never landed. Later live testing disproved that as a general rule: `door_unlock` and `door_lock` each raised `BluetoothTimeout` yet both physically executed - a VCSEC state read after each confirmed the lock state had flipped. Reads (state readers, `wake_up()`'s effect) came back reliably all night; only mutating VCSEC/RKE actions showed this false-negative pattern, most likely because the vehicle doesn't reliably return an ack `_send()` observes within the timeout, not because the write failed. Treat a `BluetoothTimeout` from any mutating BLE command as **inconclusive, not failure**: snapshot state before acting, then verify the outcome with a follow-up state read whenever a mutation times out. Never blind-retry a non-idempotent command (toggles like `media_toggle_playback`, volume steps, schedule add/remove) on timeout alone - see the retry-double-execution entry below for why the library's own retry has the same exposure. The `adjust_volume`/`TimeoutAPIError` root cause from the original observation is still unexplained; it just isn't evidence that timed-out writes never land. VCSEC actuations now use the shorter `_actuation_timeout` when their terminal ack is lost.
- **`wake_up()` is best-effort; confirm readiness with an INFO read**: `wake_up()` is a VCSEC actuation, so a terminal ack now returns promptly when observed, but a `BluetoothTimeout` is still only an inconclusive wake signal, not command failure. Call it best-effort (catch and ignore timeout) and confirm readiness by retrying a cheap INFO read instead (see the boot-delay gotcha above for why the first INFO read still needs its own retry/backoff). Hold one connection across a whole batch of related commands rather than reconnecting between each - reconnecting costs ~123% more per operation with no demonstrated wake-preservation benefit from the connection alone.
- **The signed-command retry in `Commands._command` can double-execute a mutating command**: on an `OPERATIONSTATUS_WAIT` reply or an `INCORRECT_EPOCH`/`INVALID_TOKEN` fault, `_command` (`commands.py`) re-signs and re-sends the identical command, bounded at 3 attempts then a clean `{"result": False, "reason": "Too many retries"}` - the cap itself is safe and doesn't loop. Live-verified deterministically: a WAIT-then-OK sequence produces 2 physical sends of the same command on the wire. Combined with the mutating-timeout-is-inconclusive gotcha above (a command can execute despite a WAIT/fault reply), this retry is a latent double-apply window. Harmless for a naturally idempotent command (lock/unlock), a real correctness risk for toggles and step commands (`media_toggle_playback`, `media_volume_up`/`down`, schedule add/remove) - verify those by absolute state after the call, never by counting invocations or trusting the retry to be safe.
- **`expects_data` splits BLE reply-waiting: VCSEC actuations return on the terminal ack**: a VCSEC read replies with a bare ACK **then** a data frame, but a VCSEC actuation (RKE/closure/wake via `_sendVehicleSecurity`) replies with a **single bare ACK only** - `_send` cannot tell the two apart at transport level, so the caller declares it. `_sendVehicleSecurity` passes `expects_data=False` down through `_command` into `_send` (`commands.py`/`bluetooth.py`); everything else (VCSEC reads via `_getVehicleSecurity`, all infotainment via `_send/_getInfotainment`, `_handshake`, `pair`) keeps the default `expects_data=True`. With `expects_data=False`, `_send` returns immediately on the matching ACK instead of waiting out `_ack_followup_timeout` (was a flat ~2s tax on every VCSEC actuation), and on a lost ack it raises `BluetoothTimeout` after the shorter `_actuation_timeout` (2s) rather than `_default_timeout` (5s) - the verify-by-state contract makes a longer wait pointless. Infotainment actuations never paid the tax (their `actionStatus` rides in `protobuf_message_as_bytes`, so `_send` returns on that data frame). The WAIT/fault retry threads `expects_data` through unchanged, so the double-execute exposure noted above is unaffected.
- **`navigation_gps_request`'s `order` param is a raw int, not a callable enum**: `commands.py` used to build it as `NavigationGpsRequest.RemoteNavTripOrder(order)`, treating the protobuf nested-enum wrapper (`EnumTypeWrapper`) as if it were a callable Python `enum.IntEnum` class - it isn't, so every call raised `TypeError` before any message was sent (found live during PR-8; this method had never been exercised over BLE before). Fixed to pass `order=order` directly (matching the working sibling `navigation_gps_destination_request`), which protobuf accepts as a bare int for an enum field at runtime.
- **`ReassemblingBuffer` resets on a >1s inter-chunk gap, not just on decode failure**: `bluetooth.py`'s `ReassemblingBuffer.receive_data` discards any in-progress partial frame if the next chunk arrives more than `STALE_CHUNK_TIMEOUT` (1s) after the previous one, mirroring Tesla's official Go SDK (`teslamotors/vehicle-command`, `pkg/connector/ble/ble.go`'s `rxTimeout`). Without this, a chunk dropped mid-message left a stale partial in the buffer that got prepended to the next message, corrupting it until a lucky decode failure resynced. This is a frame-integrity hardening, not a fix for the separate ack-loss behavior documented above (that's a stalled/silent link, which no buffer-side reset can recover).
- **Cross-transport parity (cloud REST `VehicleFleet` vs BLE `Commands`)**: the same-named command on both paths should build a semantically equivalent instruction from identical args - a divergence there is a bug, but response *bodies* legitimately differ (REST JSON dict vs decoded protobuf) and are not. `tests/test_cross_transport_parity.py` locks the equivalence in with mocked-both-transports tests. Known **non-bug FORM differences** (do not "fix"): `set_scheduled_departure`'s `preconditioning_enabled`/`off_peak_charging_enabled` (no proto fields), `window_control` lat/lon and `navigation_sc_request` `id` (no proto fields), `navigation_request`'s `type`/`locale`/`timestamp_ms` (REST share-intent framing), and `media_volume_up` (no Tesla REST endpoint - BLE-only; cloud raises volume via `adjust_volume`). Two **open divergences left unfixed** pending live verification: `clear_pin_to_drive_admin` builds `DrivingClearSpeedLimitPinAction` (speed-limit PIN, not PIN-to-Drive - suspected mismapping, security-sensitive), and `navigation_gps_request`'s `order` is required on BLE but optional on cloud (signature mismatch; null-order wire semantics undecided).

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
