# Threat model

## What this project does

`tesla_fleet_api` is an async Python client library. It talks to Tesla
vehicles and energy sites through four transports:

- the Tesla Fleet API over HTTPS (`tesla_fleet_api/tesla/`);
- the Teslemetry and Tessie cloud APIs over HTTPS (`teslemetry/`, `tessie/`);
- Tesla's signed vehicle-command protocol, sent through the Fleet API
  (`tesla/vehicle/signed.py`) or directly to the car over Bluetooth LE
  (`tesla/vehicle/bluetooth.py`).

Home Assistant's Tesla Fleet, Teslemetry and Tessie integrations use it. It
runs inside the user's own process and stores nothing except key files the
caller asks it to create.

## Where untrusted input enters

- **Bluetooth LE.** Any device in radio range can advertise as a Tesla (the
  advertised name is derived from the VIN) and send GATT notifications.
  `ReassemblingBuffer` in `tesla/vehicle/bluetooth.py` reassembles
  length-prefixed frames and parses them as `RoutableMessage` protobufs.
  Every byte of a notification is attacker-controlled.
- **HTTP replies** from the Fleet API, Teslemetry and Tessie: JSON bodies, and
  base64 protobuf in the `signed_command` reply (`tesla/vehicle/signed.py`).
  Treat the body as untrusted where the library parses it; a malicious server
  itself is out of scope (see below).
- **Caller-supplied secrets**: the EC P-256 command key and RSA energy-gateway
  key (PEM files loaded in `tesla/tesla.py`), OAuth access and refresh tokens
  (`tesla/oauth.py`, `tesla/fleet.py`), and Teslemetry/Tessie API tokens.

## Components that matter most

- `tesla/vehicle/commands.py`: the signed-command session. `Session` holds the
  ECDH shared key, command HMAC key, epoch, anti-replay counter and clock
  offset. `_authenticate_session_info` must verify a `SessionInfo` HMAC tag
  (bound to the request UUID) before trusting any field. `_commandHmac` and
  `_commandAes` sign or encrypt commands. Response handling checks AES-GCM
  response tags and rejects a replayed response counter.
- `tesla/vehicle/bluetooth.py`: frame reassembly, routing of replies to
  per-domain queues (`_on_message`), pairing (`pair()`), and the logic that
  decides whether a command executed.
- `tesla/vehicle/signed.py`: the Fleet API transport for signed commands.
- `tesla/jws.py`: Tesla.SS256 Schnorr/P-256 signing for Fleet Telemetry
  configuration. It is a clean-room implementation, locked to Go SDK vectors
  in `tests/fixtures/ss256_vectors.json`.
- `tesla/tesla.py`: private key generation, loading and file permissions.
- `tesla/vehicle/broadcast.py`: listeners for unsolicited VCSEC status
  broadcasts.

## Out of scope

- Behaviour of Tesla, Teslemetry or Tessie servers, and the Fleet API's own
  authentication and authorisation. The library trusts TLS (aiohttp defaults)
  to identify these servers.
- Vehicle firmware behaviour.
- VCSEC status broadcasts are unsigned in Tesla's protocol, so the library
  cannot authenticate them. A nearby device that spoofs one can change what a
  broadcast listener reports. This is a known protocol limit, not a library
  bug. A report is in scope only if a spoofed broadcast does more than that.
- `keytool.py` at the repository root is a local developer script.

## How to exercise it

`pytest` runs the full suite offline (about 900 tests). The BLE command tests
use `tests/ble_mocked_transport.py`, which drives `VehicleBluetooth` with no
real Bluetooth adapter: feed crafted notification bytes through it to test
the parser and session code. `tests/test_session_info_authentication.py`,
`tests/test_command_counter_lock.py` and `tests/test_jws.py` cover the
cryptographic paths.

## How we rate severity

- **Critical**: forging, replaying or misdirecting a vehicle command (for
  example, making the library sign a command the caller did not ask for, or
  accept a forged or replayed `SessionInfo` or response); leaking a private
  key, session key or command HMAC key.
- **High**: leaking an OAuth or API token; a Bluetooth peer making the library
  report a command as confirmed when the car did not execute it, or making the
  library repeat a command the caller sent once.
- **Medium**: denial of service from a malformed Bluetooth frame or HTTP reply
  (crash, hang, unbounded memory or CPU).
- **Low**: other robustness issues with no security effect.

A finding needs a reproducer that runs against this library, for example a
test built on `tests/ble_mocked_transport.py`.
