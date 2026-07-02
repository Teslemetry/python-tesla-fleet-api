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

`Router` (router.py) is an entity-agnostic composition wrapper (not part of the inheritance chain) that chains an ordered list of two-or-more backends sharing a common method surface and dispatches each method call down the chain with automatic per-command failover: it tries the first backend that has the method and, on any exception, retries the same call on the next backend that has it, returning the first success (raising the last error only if every applicable backend fails, `AttributeError` only if none has the method). Non-callable attributes resolve to the first backend that has them. The constructor is `Router(primary, fallback, *more_backends, health=None)` — the two-argument form is fully backward compatible. The health check (`bool` | sync callable | async callable returning `bool`; omitted = attempt primary, fail over on exception with no probe) gates **only the primary** (the first backend); the rest of the chain is reached purely through per-command failover — there is deliberately no per-backend health matrix. Note the double-execution caveat: a non-idempotent command that fails mid-flight can be re-run on the next backend.

`VehicleRouter` and `EnergySiteRouter` are thin entity-specific subclasses of `Router`. `VehicleRouter(bluetooth_primary, teslemetry_fallback)` pairs a `VehicleBluetooth` primary with a cloud (`TeslemetryVehicle`) fallback; `EnergySiteRouter(local_energysite, teslemetry_energysite)` pairs a duck-typed local `EnergySite`-shaped object (e.g. aiopowerwall's `PowerwallEnergySite`, no dependency added) with a cloud `TeslemetryEnergySite` fallback. All three live in `tesla/router.py` and are re-exported from `tesla/__init__.py` (importable as `tesla_fleet_api.tesla.Router` etc.) but have no factory on the `Vehicles`/`EnergySites` collections.

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

### Error Handling

`exceptions.py` maps HTTP status codes and error keys to specific exception classes. `raise_for_status()` parses responses and raises the appropriate exception. Signed command faults have separate hierarchies: `TeslaFleetInformationFault`, `TeslaFleetMessageFault`, `SignedMessageInformationFault`, `WhitelistOperationStatus`.

All exceptions inherit from `TeslaFleetError(BaseException)`.

### Protobuf

Generated protobuf files live in `tesla/vehicle/proto/` and are excluded from ruff and pyright. Do not edit these directly — regenerate them with `tools/regenerate_protos.sh` (needs `protoc` on `PATH`).

**Runtime-version pin (Home Assistant compatibility).** The gencode stamps a `ValidateProtobufRuntimeVersion(major, minor, patch, …)` call, and protobuf refuses to load gencode that is *newer* than the installed runtime (`gencode X > runtime` → `VersionError`). Home Assistant core pins `protobuf==6.32.0`, so the gencode must be stamped **≤ 6.32.0** or it breaks in HA. The generator version is the `protoc` version: under unified protobuf versioning, `protoc vX.Y` (`libprotoc X.Y`) stamps Python gencode `6.X.Y`. So to target runtime 6.32.0, regenerate with **protoc v32.0** (`protoc-32.0-linux-x86_64.zip` from the protobuf GitHub releases). The `protobuf>=6.32.0` floor in `pyproject.toml` must match the gencode version — never set it below the stamped version, or installs that resolve an older protobuf will hit `VersionError` at import.

## Code Style

- **Type checking**: pyright strict mode. Use `TYPE_CHECKING` guards for circular imports.
- **Linting**: ruff (proto files excluded).
- **Async**: All API methods are `async`. Uses `aiohttp` for HTTP, `aiofiles` for file I/O, `bleak` for BLE.
- **Enums**: Custom `StrEnum`/`IntEnum` in `const.py` (not stdlib). `Region` is a `Literal["na", "eu", "cn"]`, not an enum.
- **Naming**: camelCase for class instance attributes that mirror API structure (`energySites`, `createFleet`). Snake_case for method names that are API endpoints.
