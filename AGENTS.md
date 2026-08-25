## Project Overview

Python library (`tesla_fleet_api`) providing async interfaces for Tesla Fleet API, Teslemetry, and Tessie services, plus BLE communication. Published to PyPI as `tesla-fleet-api`.

## Development Commands

```bash
uv sync --extra ble                     # install (add --extra ble for Bluetooth work/tests)
uv run pyright tesla_fleet_api          # type check (strict)
uv run ruff check tesla_fleet_api       # lint
uv run ruff format tesla_fleet_api
uv run pytest tests
```

Tests use `unittest.IsolatedAsyncioTestCase`, collected natively by pytest (no
`pytest-asyncio`). BLE command tests build on `MockedBleTransportTestCase`
(`tests/ble_mocked_transport.py`), which patches `VehicleBluetooth._send` and
pre-marks both signed-command sessions ready, so a test can drive any `Commands`
method with no real BLE/GATT connection; see `tests/test_ble_mocked_commands.py`.

## API References

- Tesla Fleet: https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints
- Tessie: https://developer.tessie.com/llms.txt
- Teslemetry: http://api.teslemetry.com/openapi.yaml
- Library docs: `docs/` (`bluetooth_vehicles.md`, `energy_local_control.md`, `teslemetry.md`, `tessie.md`, `fleet_api_*.md`)

## Architecture

### Class Hierarchy

```
Tesla (tesla/tesla.py) - EC key management for signed commands
  └── TeslaFleetApi (tesla/fleet.py) - core HTTP client, _request(), access_token
        ├── TeslaFleetOAuth (tesla/oauth.py)
        ├── Teslemetry (teslemetry/teslemetry.py)
        └── Tessie (tessie/tessie.py)
```

### Vehicle Command Layers

Three implementations share the same method signatures, selected by how you
create the vehicle:

```
Vehicle (vehicle/vehicle.py) - VIN and model detection
  └── VehicleFleet (vehicle/fleet.py) - REST commands (unsigned)
        └── VehicleSigned (vehicle/signed.py) - Commands + VehicleFleet
Commands (vehicle/commands.py) - protobuf signed-command implementation (ABC)
  └── VehicleSigned          (signed commands over Fleet API)
  └── VehicleBluetooth (vehicle/bluetooth.py) - BLE transport
```

### Vehicle Collections

`Vehicles` (`vehicle/vehicles.py`) is a `dict[str, Vehicle]` with
`createFleet`/`createSigned`/`createBluetooth` factories; see the
`createBluetooth` docstring for its confirmation/keepalive/key arguments.
Teslemetry/Tessie override `Vehicles` with `TeslemetryVehicle`/`TessieVehicle`,
adding service-specific commands.

**`bleak`/`bleak-retry-connector` are the optional `ble` extra** (`pip install tesla-fleet-api[ble]`); `cryptography`, `protobuf`, and `tesla-protocol` stay base dependencies because the cloud signed-command path (`vehicle/commands.py`, `vehicle/signed.py`) needs them too, not just Bluetooth. `Vehicles.Bluetooth`/`VehiclesBluetooth.Bluetooth` and the top-level `TeslaBluetooth`/`VehicleBluetooth` re-exports resolve `tesla.vehicle.bluetooth` lazily (a property or module `__getattr__`, not a top-level import) so importing the cloud surface never requires `bleak` to be installed; `DEFAULT_KEEPALIVE_INTERVAL` lives in `const.py` (not `vehicle/bluetooth.py`) so it can be a real default value on `Vehicles`' bleak-free code paths. `tests/test_ble_optional_extra.py` locks this in by poisoning `bleak`/`bleak_retry_connector` in `sys.modules` in a subprocess and asserting the cloud surface still imports and works.

### Submodule Pattern

`Tesla` lazily attaches `charging`, `energySites`, `user`, `partner`, `vehicles`
in `__init__`; scope flags on `TeslaFleetApi.__init__` control which are built.

### Router (command side)

`Router` (`router/base.py`) is an entity-agnostic composition wrapper, not part
of the inheritance chain: `Router(primary, secondary, *more, health=None)` chains
backends sharing a method surface and dispatches each call down the chain with
per-command failover — first backend that has the method, retried on the next on
any exception, returning the first success (last error if all fail,
`AttributeError` if none has the method). Non-callable attributes resolve to the
first backend that has them.

- The health check gates **only the primary**; the rest of the chain is reached
  purely through per-command failover. There is deliberately no per-backend
  health matrix.
- Failover can double-execute a non-idempotent command that failed mid-flight.
  `BluetoothUnconfirmedCommand` is the one exception: it propagates without replay.

`VehicleRouter` and `EnergySiteRouter` (`router/vehicle.py`, `router/energysite.py`)
are thin subclasses pairing a local/BLE primary with a Teslemetry cloud fallback.
`EnergySiteRouter`'s local backend is duck-typed (e.g. aiopowerwall's
`PowerwallEnergySite`) so no dependency is added. Both re-export from
`router/__init__.py` and `tesla/__init__.py`. They have no factory on the
`Vehicles`/`EnergySites` collections.

This repo owns the RSA keypair lifecycle and cloud registration
(`Tesla.get_rsa_private_key`, `EnergySite.add_authorized_client`) that
aiopowerwall's local signed transport depends on but does not implement;
`docs/energy_local_control.md` has the end-to-end pairing flow and the
security/protocol constraints of gateway pairing (RSA for LAN TEDapi v1r,
`PENDING_VERIFICATION_TIMEOUT` is terminal, presence-free key removal).

**`set_island_mode`/`go_off_grid`/`reconnect_grid` (`tesla/energysite.py`)
unconditionally raise `SignedCommandRequired`.** They can only send an unsigned
`grpc_command`, which gateways acknowledge without actuating the contactor —
shipping that as a silent no-op would be worse. Only the signed local path
(`add_authorized_client` + `EnergySiteRouter`) actuates, and even its success
response doesn't prove the contactor moved: verify state after the call.

### ObservationFunnel (read side)

`ObservationFunnel` (`funnel.py`) is separate from the command `Router`. It is a
**funnel, not a selector**: every attached publisher feeds the same per-field
listeners, so a field bound to one source survives that source dropping.

- There is deliberately no source health, availability, grace window, failback
  delay, priority, stickiness, per-field selection, or Bluetooth-vs-stream
  ranking. **Unavailability is a value a source reports** (a null/SNA reading),
  never something the funnel infers from a link dropping.
- The only arbitration: `publish()` ignores an observation older than the last
  one for that field, and does not re-dispatch an unchanged value. Both are
  hard-coded, not configurable.
- The module is **entirely synchronous and can never originate a request** — no
  `async def`/`await`, no polling loop, no request callable, no scheduling task.
  `tests/test_funnel.py::TestFunnelCannotOriginateWork` asserts this against the
  module's own AST; keep the module synchronous rather than adding a fetch path.
  Polling belongs to an external consumer, which may gate its schedule on
  `listen_demand(paths, cb)` and feed results back via
  `VehicleDataResultPublisher.publish_result(dict)`.
- Publishers push via `publish(Observation)`; `observed_at` values must come from
  one monotonic clock shared by every publisher on a funnel. `value(path)`
  returns the last observed value; its `None` means never observed *or* reported
  unavailable.
- Fields are deliberately three (`Locked`, `ChargePortDoorOpen`,
  `DoorState.TrunkFront`). Translations are positive allowlists: an unmapped
  VCSEC enum or absent JSON leaf emits no observation rather than a guess, while
  an explicit JSON null emits an unavailable value. Any unlocked VCSEC lock state
  (including `SELECTIVE_UNLOCKED`) maps to unlocked; closure `UNKNOWN`/
  `FAILED_UNLATCH` stay unmapped pending live-frame validation.
- `BleBroadcastPublisher` reuses `VehicleBluetooth`'s `listen_*` seams and never
  connects, reads, or commands. `VEHICLELOCKSTATE_UNLOCKED` is 0 with no proto3
  presence, so every VCSEC status broadcast reports a lock state and the funnel
  deduplicates the repeats.
- `TeslemetryStreamPublisher` is the intended primary source (Bluetooth is
  opportunistic) and takes a caller-supplied payload rather than depending on
  `teslemetry-stream`: `publish_update(data)` takes one push's `data` mapping
  keyed by signal name — the same strings that package's `Signal` `StrEnum`
  equals — and coerces the `"true"`/`"false"` wire strings some vehicles stream.

### Shared Utilities

`util.py` holds dependency-free helpers re-exported from the top-level package.
`firmware_compare`/`firmware_at_least` compare dotted week-based Tesla firmware
strings (`2025.14.3`), which plain string comparison misorders
(`"2025.10" < "2025.9"`); unparseable strings sort behind any parseable one.
Deliberately native tuple comparison, not a version-parsing dependency.

### Release Process

No release automation. To ship: bump `version` in `pyproject.toml` and
`__version__` in `tesla_fleet_api/__init__.py`, run `uv lock`, commit on `main`,
push a matching `vX.Y.Z` tag. CI and the release gate run `uv sync --locked`, so
a bump that skips `uv lock` fails before merge. `.github/workflows/release.yml`
triggers on the tag: reruns the full gate, then publishes via PyPA OIDC trusted
publishing (PEP 740 attestations) in the `pypi` environment and cuts the Release.
That environment has **no required reviewers** — merging the version-bump PR is
the effective publish approval. Keep `release.yml` a plain top-level workflow,
never a reusable `workflow_call` one: the PyPI trusted publisher is configured as
workflow `release.yml` + environment `pypi`, and a caller's signing identity
would not match. Sibling repos each carry their own copy rather than calling it.

### Error Handling

`exceptions.py` maps HTTP status codes and error keys to exception classes;
`raise_for_status()` raises the right one. Signed-command faults have separate
hierarchies (`TeslaFleetInformationFault`, `TeslaFleetMessageFault`,
`SignedMessageInformationFault`, `WhitelistOperationStatus`).

**All exceptions inherit from `TeslaFleetError(BaseException)`, deliberately not
`Exception`.** A bare `except Exception` (e.g. a retry loop around BLE reads)
silently fails to catch `BluetoothTimeout` and every other library error — catch
`TeslaFleetError` or `BaseException` explicitly. `VehicleBluetooth` wraps
transport failures (`connect`/`connect_if_needed`, notification setup) in
`BluetoothTransportError`, chaining the original cause. Those catch sites must
catch **both** `bleak.exc.BleakError` and builtin `TimeoutError`: bleak-esphome
converts an aioesphomeapi GATT/connect/notify timeout into a bare `TimeoutError`.
The GATT write in `_send` is *not* unconditionally wrapped — see
"Write-delivery certainty" below.

### Protobuf

Bindings come from the published `tesla-protocol` PyPI package
(`Teslemetry/tesla-protocol`); import from `tesla_protocol.command.<module>_pb2`.
`tesla_fleet_api/tesla/vehicle/proto/` holds only backwards-compatible re-export
shims, not generated code. To pick up new message definitions, bump the floor in
`pyproject.toml` — there is no local regeneration step.

**Runtime-version pin (Home Assistant compatibility).** protobuf refuses to load
gencode stamped *newer* than the installed runtime. Home Assistant core pins
`protobuf==6.32.0`, so any `tesla-protocol` version depended on must stamp
gencode **≤ 6.32.0** and declare a `protobuf` requirement compatible with
`==6.32.0` — check both before bumping. Keep `pyproject.toml`'s `protobuf` floor
in sync with what `tesla-protocol` requires, and keep the `tesla-protocol` floor
at `>=1.4.0` (earlier `.pyi` imports fail strict pyright; 1.4.0 is also the first
release allowing protobuf 7).

Command coverage is locked by `tests/test_proto_coverage_lock.py`, which fails if
any `VehicleAction`/`GetVehicleData` field has no wrapper (`commands.py`) or
reader (`bluetooth.py`) and is not allowlisted with a reason — keep that test in
sync with a `tesla-protocol` bump rather than special-casing new fields. Naming:
`legacy_vehicle_state()` (`bluetooth.py`) reads CarServer's `GetVehicleState`
sub-state; `vehicle_state()` is the VCSEC `VehicleStatus`, a different
message/domain. `set_rate_tariff`/`add_managed_charging_site` take
`tesla_protocol` message types directly rather than a parallel flattened API.

## Code Style

- **Type checking**: pyright strict. Use `TYPE_CHECKING` guards for circular imports.
- **Linting**: ruff.
- **Async**: all API methods are `async`; `aiohttp`, `aiofiles`, `bleak`.
- **Enums**: custom `StrEnum`/`IntEnum` in `const.py` (not stdlib). `Region` is a
  `Literal["na", "eu", "cn"]`, not an enum.
- **Naming**: camelCase for instance attributes mirroring API structure
  (`energySites`, `createFleet`); snake_case for endpoint method names.
- **Seat indexing gotcha**: `Seat` is **0-indexed** (`FRONT_LEFT=0`) and is for
  the manual seat heater/cooler paths (`remote_seat_heater_request`,
  `remote_seat_cooler_request`). `AutoSeat` is **1-indexed** and is the correct
  type for `remote_auto_seat_climate_request` on **both** backends — its values
  equal Tesla's REST wire values and the proto `AutoSeatPosition_*` enum. Passing
  a `Seat` to the auto-climate command is off-by-one.
- **Protobuf oneof-by-string-kwargs bypasses pyright**:
  `remote_seat_heater_request`/`remote_seat_cooler_request` (`commands.py`) build
  their action message from a `dict` of literal field-name strings expanded as
  `**kwargs`; a typo raises at call time, not at type-check time. Cross-check new
  field-name strings against `tesla_protocol.command.car_server_pb2`.
- **`navigation_gps_request`'s `order` is a raw int, not a callable enum**: the
  protobuf `EnumTypeWrapper` is not an `IntEnum` class; pass `order=order`, which
  protobuf accepts as a bare int for an enum field.
- **Typed accessors over undocumented raw-dict responses** (e.g.
  `TeslemetryEnergySite.find_authorized_clients`/`find_gateway_address`) keep
  API-parsing logic in the library. Two rules for any new one: (1) field lookup
  must check key presence (`key in payload`), never `payload.get(key) or default`
  — a legal falsy value is not "missing"; (2) a `None` body or an unrecognized
  shape is malformed data — raise `InvalidResponse`, never collapse it to an
  empty result. Only a well-formed-but-empty response parses to empty. Tesla
  publishes no schema for these endpoints, so `const.py`'s enums are the schema of
  record: widen modeled fields only against a further live sample. Untyped
  escape hatches (`list_authorized_clients()`) stay available alongside.
- **`register_client()` (`teslemetry/teslemetry.py`) is Teslemetry-only** OAuth
  Dynamic Client Registration (RFC 7591) — a module-level function, not a
  `Teslemetry` method, since registration precedes having a `client_id` or token.
  It always registers a new client (no dedup) and raises
  `TeslemetryRegistrationError` on transport failure, non-2xx, non-JSON, non-dict,
  or a body with no usable `client_id`. Fleet API and Tessie have no equivalent —
  don't add one speculatively.

## Cross-Transport Behaviour

Command logging happens at exactly five chokepoints: `Commands`'
`_sendVehicleSecurity`/`_getVehicleSecurity`/`_sendInfotainment`/`_getInfotainment`
(BLE and Fleet-signed) and `TeslaFleetApi._request` (REST), all emitting
`command=<name> transport=<t> result=...`. `transport` comes from a
`_transport_name` `ClassVar` per concrete class — **add that ClassVar to any new
`Commands`/`TeslaFleetApi` subclass.** For signed transports `command` is *not*
the Python method name but the populated protobuf oneof field (`door_lock()` logs
as `RKE_ACTION_LOCK`). `Router._dispatch` logs its own per-backend line. Exact
line shapes are locked by `tests/test_command_logging.py`.

`_log_request_result` (`fleet.py`) runs after a successful request and must never
raise on any JSON-legal body — it guards with `isinstance(data, dict)` before
`.get()`.

**Cross-transport parity**: the same-named command on REST `VehicleFleet` and BLE
`Commands` must build a semantically equivalent instruction from identical args;
a divergence is a bug. Response *bodies* legitimately differ (REST JSON vs decoded
protobuf). `tests/test_cross_transport_parity.py` locks this in and documents the
known non-bug form differences — check it before "fixing" one.

Vehicle-side behaviours that look like library bugs but are not:

- **`remote_heater_control_enabled`** (`climate_state()`) is a read-only
  vehicle-side setting with no command to flip it, and gates every remote comfort
  action (seat heater/cooler, steering wheel heat, auto seat climate). With it
  `false` the vehicle ACKs `{"result": false, "reason": "cabin comfort remote
  settings not enabled"}` and changes nothing.
- **`scheduled_charging_mode` is tri-state and shared**: `set_scheduled_charging`
  and `set_scheduled_departure` both write it (Off/StartAt/DepartBy). Disabling
  one while the other is active turns the whole feature Off. A caller toggling one
  must read `charge_state()` first and restore the exact prior mode.
- **`set_scheduled_departure`'s `preconditioning_enabled`/
  `off_peak_charging_enabled` args are dead**: `ScheduledDepartureAction` has only
  `preconditioning_times`/`off_peak_charging_times` (weekday recurrence, no on/off).
- **`charge_standard()` rejects `already_standard`**: calling it when
  `charge_limit_soc` already equals `charge_limit_soc_std` returns
  `{"result": False, "reason": "already_standard"}`, not a no-op success.

## BLE

User-facing behaviour, examples and the confirmation-ladder table live in
`docs/bluetooth_vehicles.md`. The invariants below are what code changes must not
break.

- **Discovery**: a Tesla advertises no 128-bit service UUID pre-connect — only its
  VIN-derived local name (`^S[a-f0-9]{16}[CDRP]$`), and only in the scan response.
  **Never pass `service_uuids=[SERVICE_UUID]` as a `BleakScanner` filter** — it
  hides the vehicle on a direct BlueZ adapter (an ESPHome proxy doesn't enforce
  the filter the same way, which masks the bug in testing). Scan unfiltered with
  active scanning and match by name; `SERVICE_UUID` is for post-connect GATT only.
- **`bleak` client/scanner must be resolved dynamically**: both BLE modules
  (`tesla/vehicle/bluetooth.py`, `tesla/bluetooth.py`) `import bleak` and
  reference `bleak.BleakClient`/`bleak.BleakScanner` at call time, never
  `from bleak import BleakClient`. Home Assistant's habluetooth replaces those
  module attributes at runtime with a proxy-aware client; a name captured at
  import would permanently ignore that and use the local adapter. Keep type-only
  imports under `TYPE_CHECKING`; tests patch the canonical `bleak.*` names.
- **Domain routing**: `Domain` has more values than `_queues` has keys (only
  `DOMAIN_VEHICLE_SECURITY`/`DOMAIN_INFOTAINMENT`). `_on_message` must look up
  `_queues` with `.get()` and drop unrecognized domains — indexing raises
  `KeyError` inside the `ReassemblingBuffer` callback, aborting reassembly of
  every already-buffered message in that notification.
- **`ReassemblingBuffer` resets on a >`STALE_CHUNK_TIMEOUT` (1s) inter-chunk gap**,
  not only on decode failure, mirroring Tesla's Go SDK `rxTimeout`. Without it a
  dropped chunk leaves a stale partial that corrupts the next message.
- **`_stream_sinks` peels subscription pushes off the command-reply queue**: a
  `vehicleDataSubscription`'s pushes arrive on the same domain queue a command
  reply uses, correlated by the subscribe request's `request_uuid`. `_on_message`
  checks `_stream_sinks` before touching `_queues`, so `_send`'s pre-send drain
  can't discard a push and `_await_response` can't return one as an unrelated
  reply. `_register_stream_sink`/`_unregister_stream_sink` are the only entry
  points; there is no public subscription API yet.
- **Mutating-command timeouts are inconclusive — never assume "the write didn't
  land"**: a mutating VCSEC/RKE action can raise `BluetoothTimeout` yet have
  physically executed. Snapshot state before acting and verify with a follow-up
  read. Never blind-retry a non-idempotent command (toggles, volume steps,
  schedule add/remove) on timeout alone.
- **`Commands._command` can double-execute**: on `OPERATIONSTATUS_WAIT` or an
  `INCORRECT_EPOCH`/`INVALID_TOKEN` fault it re-signs and re-sends the identical
  command (3 attempts, then `{"result": False, "reason": "Too many retries"}`).
  Harmless for idempotent commands, a real risk for toggles and step commands —
  verify those by absolute state, never by counting invocations.
- **`BluetoothUnconfirmedCommand` vs `BluetoothCommandFailed`**:
  `_sendVehicleSecurity`/`_sendInfotainment` wrap a caught `BluetoothTimeout` into
  `BluetoothUnconfirmedCommand` when the ladder is genuinely unresolved (the
  vehicle may have executed). `BluetoothCommandFailed` is the distinct outcome
  where a state check *proved* the command did not apply; it does **not** subclass
  `BluetoothTimeout`. `Router` special-cases only the former (no replay). A plain
  read (`_getVehicleSecurity`/`_getInfotainment`) raises unadorned
  `BluetoothTimeout` — a read has no side effect to be unconfirmed about.
- **Write-delivery certainty splits the two at the GATT write in `_send`**:
  `BleakCharacteristicNotFoundError` is the only provably pre-submission failure
  (bleak resolves `WRITE_UUID` before any backend I/O), so it alone stays
  `BluetoothTransportError` and is safe for `Router` to retry. Every other
  `BleakError`/`TimeoutError` from `write_gatt_char` happens inside backend I/O
  where delivery is unprovable, so `_send` races any armed broadcast watcher for
  the rest of the window and otherwise raises plain `BluetoothTimeout`.
  `_send_optimistic` gets the same treatment explicitly since it bypasses the
  ladder. Tests: `test_ble_send_transport.py`, `test_ble_write_timeout_router.py`.
- **The confirmation ladder is one `confirmation` enum plus one
  `raise_unconfirmed` bool**: `confirmation` (`"optimistic" | "ack" | "verify"`,
  default `"ack"`) picks how many of write → ack-or-broadcast wait → state-read
  run; `raise_unconfirmed` (default `False`) picks what happens when the ladder
  still can't tell. `"optimistic"` signs and writes but never waits — a provably
  pre-submission write failure still raises `BluetoothTransportError`, but a
  submitted-then-ambiguous write follows `raise_unconfirmed` like every other
  rung. `"verify"` adds a post-timeout state read (`_resolve_timeout` against
  `_vcsec_verify_plan`/`_INFOTAINMENT_VERIFY_PLANS`, covering only clearly
  derivable absolute commands) returning success on a match,
  `BluetoothCommandFailed` on a proven mismatch, or `None` (falls through to
  `raise_unconfirmed`) if the read itself failed. Commands with no plan (true
  toggles, relative steps, ack-only actions) always fall through. The legacy
  `optimistic`/`verify_commands` booleans are deprecated: both warn and map onto
  `confirmation`, and survive as read-only properties.
- **Broadcast-as-confirmation races the ack wait for lock/unlock**: the vehicle
  keeps emitting unsolicited VCSEC status broadcasts even when it emits no
  addressed ack. `_send`'s `confirm_broadcast` arms a per-domain watcher
  (`_broadcast_watchers`) that decodes broadcast frames and races them against the
  addressed reply; first to satisfy the plan's predicate wins, and only the
  addressed path can raise a car-side rejection. A mismatching broadcast does not
  fail fast (a later one could still confirm), but a mismatch standing at
  window-end raises `BluetoothCommandFailed` rather than an ambiguous timeout.
  Reuses the `"verify"` rung's predicate; currently only lock/unlock has an
  observed status broadcast. Tests: `test_ble_broadcast_confirmation.py`.
- **`expects_data` splits reply-waiting**: a VCSEC read replies with a bare ACK
  **then** a data frame; a VCSEC actuation replies with a **single bare ACK only**.
  `_send` cannot tell them apart, so the caller declares it — `_sendVehicleSecurity`
  passes `expects_data=False` (returns on the matching ACK, and on a lost ack
  reaches the unresolved outcome after the shorter `_actuation_timeout` rather than
  `_default_timeout`); everything else keeps the default `True`.
- **`pair()` confirms two ways and writes the whitelist op exactly once**: the
  success frame is single-shot and lost forever if the link cycles while the user
  walks to the car. `pair()` waits one `poll_interval` for the reply, then polls
  `_pair_probe()` (a VCSEC `_handshake` with our own key, which faults
  `NotOnWhitelistFault` until whitelisted; any `TeslaFleetError` means "not yet",
  so polling survives reconnects) until `timeout`. **Never re-send the whitelist
  op** — it re-prompts the user. Deadline with neither path confirming raises
  `BluetoothTimeout`.
- **Idle keepalive**: an idle held link to the vehicle drops at ~42s mean; a
  trivial passive GATT read on an idle cadence extends the session ~10x, so
  `keepalive_interval` (default `DEFAULT_KEEPALIVE_INTERVAL`, `None`/`0`
  disables) starts one task per connection reading `VERSION_UUID` after that many
  seconds of *genuine GATT idleness* — `_last_activity` is bumped by every `_send`
  write and every notify, so an active session gets no extra traffic. The read is
  bounded and best-effort: every attempt is timed out and swallows all failures
  except `CancelledError`; it must never raise into user code, trigger reconnect,
  or wake the car. Lifecycle is tied to the connection (started at the end of
  `connect()`, cancelled-and-awaited in `disconnect()`). **Tradeoff**: these reads
  keep an awake car awake and defer sleep — disable keepalive or disconnect when
  the car should sleep.
- **Broadcast listeners** (`tesla/vehicle/broadcast.py`): `VehicleBluetooth` fans
  VCSEC status broadcasts out to long-lived per-field listeners from the same
  `_on_message`. Each modeled `VehicleStatus` leaf has a typed `listen_<field>`;
  anything not decoded is covered by `listen_broadcast(domain, callback)`.
  Closure/tonneau-percent listeners gate on `HasField` (real proto3 presence); the
  five scalar enum fields have none, so they fire on **every** status broadcast,
  not only on change. Each returns an `unsubscribe()`; registries live for the
  instance's lifetime and survive reconnects, like `_queues`. Callback exceptions
  are logged and isolated from later listeners and message routing, except
  `KeyboardInterrupt`/`SystemExit`.
  `listen_connection_status()` reports session transitions including unexpected
  transport loss; the contract is `docs/bluetooth_vehicles.md#connection-status-events`.
- **`BleBroadcastStreamGlue` (`tesla/vehicle/stream_glue.py`) never imports
  `teslemetry_stream`**: it wires BLE broadcast listeners to `sink.ingest(data,
  metadata)` against a local structural `StreamSink` `Protocol`, the same
  duck-typed pattern `EnergySiteRouter` uses — `TeslemetryStream`'s `ingest()`
  satisfies it with no coupling or dependency either direction. It reuses
  `funnel.py`'s `LOCK_STATES`/`CLOSURE_STATES` (module-level, not underscore-private,
  precisely so this cross-module import is legal under strict pyright) and adds
  `GEAR_STATES`/`TONNEAU_POSITION_STATES` for the two fields teslemetry-stream
  carries as `<Prefix><Option>` wire strings (`"ShiftStateP"`), verified against
  that package's listeners rather than guessed. Unmapped by design: tonneau
  OPENING/CLOSING (no in-transit state to translate to), plus sleep status (the
  `ingest()` payload is always nested under the signal-topic key, with no way to
  produce a `state`-topic event), user presence and UI desire (no `Signal` entry
  upstream). Push-only — no demand gating, since VCSEC broadcasts regardless of
  listeners. `stop()` unsubscribes everything and is idempotent.
- **`False`, not `None`, is the "signing disabled" value** for `Commands.__init__`'s
  `private_key` (and the `key` argument of `VehicleBluetooth.__init__` and the
  `create*` factories). `None` keeps its long-standing meaning of falling back to
  the parent's key and raising `ValueError("No private key.")` if it has none; a
  caller passing `None` to mean "I haven't got one" must keep getting that error,
  not a silently unsignable vehicle. **Because `False` and `None` are both falsy,
  every branch on this argument must test identity (`is False`/`is not None`)** —
  a truthiness check collapses the two states. `self.private_key is None` means
  signing-disabled and makes `_handshake` raise `SigningDisabled` up front.
  `_handshake` is **not** a single choke point: `pair()`'s fast path builds and
  sends its own whitelist request, so it carries its own identical guard — any new
  signed-session entry point that skips `_handshake` needs one too.

### Vehicle-side BLE behaviours (not library bugs)

- **Infotainment boot delay**: `wake_up()` is VCSEC and returns as soon as the
  vehicle-security computer acks, well before infotainment can complete a signed
  handshake. An INFO read/command issued immediately after can raise
  `BluetoothTimeout` through no fault of its own — retry with backoff. `wake_up()`
  is best-effort: an unresolved wake is an inconclusive signal, not failure.
  Confirm readiness with a cheap INFO read, and hold one connection across a batch
  of related commands rather than reconnecting between each.
- **`vehicle_data()` response-size cap**: the vehicle's signed-command
  implementation enforces its own response-size limit independent of BLE
  reassembly. One endpoint succeeds; as few as **two** `BluetoothVehicleData`
  endpoints together reliably raise
  `TeslaFleetMessageFaultResponseSizeExceedsMTU`. That is why the BLE
  `vehicle_data()` has no all-endpoints default — prefer the per-substate readers.
- **Individual doors have no reliable powered close** (Model 3): `open_*_door()`
  unlatches over VCSEC, and an ack from a close command only means the car
  accepted it, not that the door re-latched — a human must push it shut. Never
  chain an automated snapshot→act→verify→restore cycle across an individual
  door-open command.
- **Media state observability**: `MediaState.now_playing_artist/title` and all of
  `MediaDetailState` are only populated for some sources (USB/Bluetooth, not
  Spotify), so `media_next_track`/`media_prev_track`/`media_next_fav`/
  `media_prev_fav` are not reliably state-observable — verify by ACK and pair with
  the inverse command. `audio_volume`/`media_playback_status` are reliable provers.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
