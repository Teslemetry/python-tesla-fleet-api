---
name: tesla-protocol-bump
description: Use when raising the tesla-protocol (protobuf bindings) floor - check the Home Assistant protobuf pin, bump floors, resync test_proto_coverage_lock.py, run the gate.
---

# Bump tesla-protocol

Protobuf bindings come from the `tesla-protocol` PyPI package
(`Teslemetry/tesla-protocol`). There is no local regeneration step: new
message definitions arrive only by raising the floor in `pyproject.toml`.
(`upgradeProtoc.sh` is not part of this procedure.)

## 1. Check the Home Assistant protobuf pin first

protobuf refuses to load gencode stamped newer than the installed runtime, and
Home Assistant core installs this library under its own `protobuf` pin.

1. Read the current `protobuf==` line in Home Assistant core's
   `homeassistant/package_constraints.txt` (on `dev`).
2. Check the target `tesla-protocol` release: its gencode stamp must be at or
   below that pin, and its `protobuf` requirement must accept that pin.
3. If it is not, stop. The bump has to wait for Home Assistant, or needs a
   `tesla-protocol` release built against an older protoc.

## 2. Bump the floors

1. In `pyproject.toml`, raise `tesla-protocol>=` to the target version.
2. Set the `protobuf>=` floor in `pyproject.toml` to match what that
   `tesla-protocol` version requires (and not above the Home Assistant pin).
3. Run `uv lock`. CI uses `uv sync --locked`.

## 3. Resync the coverage lock

`tests/test_proto_coverage_lock.py` fails on any `VehicleAction` field with no
wrapper in `commands.py`, or `GetVehicleData` field with no reader in
`bluetooth.py`, unless it is allowlisted with a reason.

1. Run `uv run pytest tests/test_proto_coverage_lock.py`.
2. For each new field, wrap it (the captain's directive is full proto
   coverage). Add a field to an allowlist only with a written reason, in a
   reasoned set like the existing `TESLA_PROTOCOL_3_UNWRAPPED_VEHICLE_ACTION_FIELDS`.
   Do not special-case new fields in the test logic.
3. `test_allowlisted_fields_still_exist_in_the_proto` catches renamed or
   removed fields: delete stale allowlist entries, and find the new name.

## 4. Check renumbered or renamed messages

A major `tesla-protocol` release can renumber request fields and change enums
(3.0.0 did). Diff the `.proto` changes and check:

- `BluetoothVehicleData` in `tesla_fleet_api/const.py`: each value must still
  name the intended `GetVehicleData` field.
- Proto enum values the library passes or translates. 3.0.0 dropped the
  invented `*_UNKNOWN = 0` from the outlet, power feed and powershare enums,
  which changed the number behind each name.
- The re-export shims in `tesla_fleet_api/tesla/vehicle/proto/`
  (`tests/test_proto_compatibility.py` lists the modules).
- `tests/test_cross_transport_parity.py` if a REST/BLE-shared command changed.

## 5. Run the gate

```bash
uv sync --locked
uv run ruff check tesla_fleet_api tests
uv run pyright tesla_fleet_api
uv run pytest tests -q
```

In the PR, state the Home Assistant `protobuf` pin you checked and the gencode
version of the new `tesla-protocol`.
