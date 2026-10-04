## Project Overview

Python library (`tesla_fleet_api`) with async clients for Tesla Fleet API,
Teslemetry, Tessie and vehicle BLE. Published to PyPI as `tesla-fleet-api`.

## Development Commands

```bash
uv sync                                 # install
uv run pyright tesla_fleet_api          # type check (strict)
uv run ruff check tesla_fleet_api       # lint
uv run ruff format tesla_fleet_api
uv run pytest tests
```

Tests use `unittest.IsolatedAsyncioTestCase` collected by pytest (no
`pytest-asyncio`). BLE command tests build on `MockedBleTransportTestCase`
(`tests/ble_mocked_transport.py`), which needs no real BLE/GATT connection.

## API References

- Tesla Fleet: https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-endpoints
- Tessie: https://developer.tessie.com/llms.txt
- Teslemetry: http://api.teslemetry.com/openapi.yaml
- Library docs: `docs/`. Measured live-vehicle BLE timings: `OBSERVATIONS.md`
  (record new experiment results there).

## Release

No release automation. Bump `version` in `pyproject.toml` and `__version__` in
`tesla_fleet_api/__init__.py`, run `uv lock` (CI uses `uv sync --locked`), commit
on `main`, push a `vX.Y.Z` tag. `release.yml` publishes to PyPI via OIDC trusted
publishing in the `pypi` environment, which has **no required reviewers**:
merging the version-bump PR is the publish approval. Keep `release.yml` a plain
top-level workflow, never `workflow_call` — the trusted publisher is bound to
`release.yml` + `pypi`.

## Dependencies

- Protobuf bindings come from the `tesla-protocol` PyPI package
  (`tesla_protocol.command.<module>_pb2`); `tesla/vehicle/proto/` holds only
  re-export shims. There is no local regeneration step: bump the floor instead.
- **Home Assistant pin**: protobuf refuses gencode newer than the runtime. Before
  bumping `tesla-protocol`, check HA core's `protobuf` pin
  (`homeassistant/package_constraints.txt`) and keep our `protobuf` floor in sync.
- Do not add dependencies on aiopowerwall or `teslemetry-stream`.
  `EnergySiteRouter` and `BleBroadcastStreamGlue` use local structural
  `Protocol`s instead.
- `firmware_compare`/`firmware_at_least` (`util.py`) must be used for firmware
  strings (`"2025.10" < "2025.9"` as strings). No version-parsing dependency.

## Code Rules

- pyright strict; `TYPE_CHECKING` guards for circular imports.
- Enums are the custom `StrEnum`/`IntEnum` in `const.py`, not stdlib. `Region`
  is a `Literal`. camelCase for attributes that mirror API structure
  (`energySites`, `createFleet`); snake_case for endpoint methods.
- **All exceptions inherit `TeslaFleetError(BaseException)`, not `Exception`**,
  on purpose. `except Exception` does not catch them.
- BLE transport catch sites must catch both `bleak.exc.BleakError` and builtin
  `TimeoutError` (bleak-esphome raises a bare `TimeoutError`).
- `exceptions.is_key_rejected` is a positive allowlist verified against each
  fault's proto enum meaning, not its name.
- Captain directive: full proto coverage. `tests/test_proto_coverage_lock.py`
  fails on any unwrapped `VehicleAction`/`GetVehicleData` field; keep it in sync
  on a `tesla-protocol` bump instead of special-casing new fields.
- **Seat indexing**: `Seat` is 0-indexed and only for
  `remote_seat_heater_request`. `AutoSeat` is 1-indexed and is the type for
  `remote_auto_seat_climate_request` on both backends. A `Seat` there is off by one.
- `remote_seat_heater_request`/`remote_seat_cooler_request` build protobuf
  messages from string kwargs, so pyright does not check them. Cross-check field
  names against `tesla_protocol.command.car_server_pb2`.
- `navigation_gps_request`: pass the protobuf enum `order` as a bare int; the
  `EnumTypeWrapper` is not callable like an `IntEnum`.
- `legacy_vehicle_state()` (`getLegacyVehicleState`), `current_vehicle_state()`
  (`getVehicleState`) and `vehicle_state()` (VCSEC `VehicleStatus`) are three
  different messages.
- Typed accessors over undocumented raw-dict responses: check `key in payload`,
  never `payload.get(key) or default`. A `None` body or unknown shape raises
  `InvalidResponse`; only a well-formed empty response parses to empty. Widen
  `const.py` enums only against a live sample. Keep the untyped escape hatch.
- `register_client()` is Teslemetry-only. Do not add Fleet API or Tessie
  equivalents speculatively.
- SS256 JWS signing (`tesla/jws.py`) is locked by Go SDK vectors in
  `tests/fixtures/ss256_vectors.json`: regenerate with `ss256_vectors_gen.go`,
  never hand-edit, and do not add low-`s` normalisation.

## Router and Energy Sites

- `Router` health check gates **only the primary**. There is deliberately no
  per-backend health matrix.
- Failover can double-execute a non-idempotent command that failed mid-flight.
  `BluetoothUnconfirmedCommand` must propagate without replay.
- `set_island_mode`/`go_off_grid`/`reconnect_grid` **must keep raising
  `SignedCommandRequired`**: the unsigned `grpc_command` is acknowledged but does
  not move the contactor. Only the signed local path actuates; verify state after.

## ObservationFunnel (`funnel.py`)

- A funnel, not a selector. Do not add source health, availability, grace
  windows, priority, stickiness or per-field selection. Unavailability is a value
  a source reports, never inferred from a dropped link.
- The only arbitration (drop older observations, skip unchanged values) is
  hard-coded, not configurable.
- The module must stay fully synchronous and never originate a request;
  `TestFunnelCannotOriginateWork` enforces this. Polling belongs to the consumer.
- Translations are positive allowlists: an unmapped value emits nothing, not a
  guess. Fields are deliberately limited to three.

## Cross-Transport Rules

- Add a `_transport_name` `ClassVar` to every new `Commands`/`TeslaFleetApi`
  subclass; command log line shapes are locked by `tests/test_command_logging.py`.
- `_log_request_result` (`fleet.py`) must never raise on any JSON-legal body.
- The same-named command on REST `VehicleFleet` and BLE `Commands` must build an
  equivalent instruction from identical args. Check
  `tests/test_cross_transport_parity.py` for known form gaps before "fixing" one.

Vehicle behaviours that look like library bugs but are not:

- `remote_heater_control_enabled=false` (read-only, no command) makes every remote
  comfort action return `"cabin comfort remote settings not enabled"`.
- `scheduled_charging_mode` is shared by `set_scheduled_charging` and
  `set_scheduled_departure`. Read `charge_state()` first and restore the prior mode.
- `set_scheduled_departure`: a present preconditioning/off-peak block turns the
  feature on, so the signed path omits it when disabled (as Tesla's proxy does).
- `charge_standard()` returns `already_standard` as a failure, not a no-op.

## BLE

User-facing behaviour lives in `docs/bluetooth_vehicles.md`. Do not break these:

- **Never pass `service_uuids=[SERVICE_UUID]` to `BleakScanner`**: a Tesla
  advertises only its VIN-derived name, in the scan response. Scan unfiltered
  with active scanning and match by name.
- Reference `bleak.BleakClient`/`bleak.BleakScanner` at call time, never
  `from bleak import ...`: Home Assistant replaces them at runtime. Tests patch
  the `bleak.*` names.
- `_on_message` must look up `_queues` with `.get()`; a `KeyError` aborts the
  whole notification's reassembly.
- **Mutating-command timeouts are inconclusive**: the car may have executed.
  Never blind-retry a non-idempotent command (toggle, step, schedule add/remove)
  on a timeout; verify by absolute state, not invocation count
  (`Commands._command` already re-sends on `WAIT`/epoch faults).
- `BluetoothUnconfirmedCommand` means unresolved; `BluetoothCommandFailed` means a
  state check proved it did not apply and does not subclass `BluetoothTimeout`.
  Plain reads raise plain `BluetoothTimeout`.
- In `_send`, only `BleakCharacteristicNotFoundError` is provably pre-submission
  and may become `BluetoothTransportError` (retryable). Every other write error
  is delivery-unknown.
- `"verify"` plans cover only clearly derivable absolute commands. Do not add
  plans for toggles, relative steps or ack-only actions.
- VCSEC actuations reply with a single bare ACK; callers declare
  `expects_data=False` for them.
- **`pair()` must never re-send the whitelist op** — it re-prompts the user.
- A `session_info` reply that fails authentication is re-requested, never trusted.
- Keepalive reads must never raise into user code, trigger reconnect or wake the
  car. They delay sleep; disable keepalive or disconnect when the car should sleep.
- **`False`, not `None`, disables signing** for `private_key`/`key`. `None` falls
  back to the parent key and must keep raising `ValueError("No private key.")`.
  Test identity (`is False`/`is not None`), never truthiness. `pair()`'s fast path
  skips `_handshake`, so any new signed-session entry point needs its own guard.

Vehicle-side BLE behaviours (not library bugs):

- Infotainment answers a handshake 4-16s after VCSEC wake. Readiness is a fresh
  INFO handshake, never VCSEC status or a broadcast.
- Two or more `vehicle_data()` endpoints together raise
  `TeslaFleetMessageFaultResponseSizeExceedsMTU`; that is why BLE `vehicle_data()`
  has no all-endpoints default.
- **Individual doors have no reliable powered close** (Model 3). Never automate a
  snapshot→act→verify→restore cycle across an individual door-open command.
- Media track/favourite commands are not reliably state-observable (Spotify).
  Verify them by ACK; use `audio_volume`/`media_playback_status` as provers.

## Maintaining this file

Keep only context an agent cannot get by reading the code. Point to the
authoritative file or command instead of restating it. Prefer pruning to
appending; deep task-specific knowledge belongs in a repo skill.
