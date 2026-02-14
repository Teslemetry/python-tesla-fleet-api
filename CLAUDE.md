# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python library (`tesla_fleet_api`) providing async interfaces for Tesla Fleet API, Teslemetry, and Tessie services, plus BLE communication. Published to PyPI as `tesla-fleet-api`.

## Development Commands

```bash
# Install dependencies
pip install -e .

# Type checking (strict mode)
pyright tesla_fleet_api

# Linting
ruff check tesla_fleet_api
ruff format tesla_fleet_api
```

No test suite exists in this repo.

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

Generated protobuf files live in `tesla/vehicle/proto/` and are excluded from ruff and pyright. Do not edit these directly.

## Code Style

- **Type checking**: pyright strict mode. Use `TYPE_CHECKING` guards for circular imports.
- **Linting**: ruff (proto files excluded).
- **Async**: All API methods are `async`. Uses `aiohttp` for HTTP, `aiofiles` for file I/O, `bleak` for BLE.
- **Enums**: Custom `StrEnum`/`IntEnum` in `const.py` (not stdlib). `Region` is a `Literal["na", "eu", "cn"]`, not an enum.
- **Naming**: camelCase for class instance attributes that mirror API structure (`energySites`, `createFleet`). Snake_case for method names that are API endpoints.
