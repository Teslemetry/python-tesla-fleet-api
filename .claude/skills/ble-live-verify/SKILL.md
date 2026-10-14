---
name: ble-live-verify
description: Use when proving a BLE command or reader against the live test car (direct adapter or ESPHome BLE proxy) - snapshot, act, verify, restore, then record results in OBSERVATIONS.md.
---

# Live-verify a BLE command

Mocked tests (`tests/ble_mocked_transport.py`) prove the bytes we send. Only
the car proves what a command does. Use this procedure to check a command
against the real vehicle and leave the car as you found it.

## Setup

- Put the harness in a repo-root `test_*.py` file (for example
  `test_bluetooth.py`). `.gitignore` ignores `test*.py` at the root, so it
  stays out of commits. Never commit a VIN, key or proxy address.
- Build the vehicle with `TeslaBluetooth().vehicles.createBluetooth(...)` with a
  whitelisted key (see `docs/bluetooth_vehicles.md`). Log with millisecond
  timestamps.
- Set `keepalive_interval=None` for any sleep or wake experiment: keepalive
  reads keep the car awake.
- **ESPHome proxy:** a proxy has few connection slots. If connect fails while
  scans still see the car, free a slot first (for example turn off the owner's
  phone Bluetooth, disconnect other BLE clients) before you suspect the library.
  A proxy also does not enforce a `service_uuids` scan filter the way a direct
  BlueZ adapter does, so a discovery bug can hide behind it.
- **Direct adapter:** connect fails at range. Move closer and disconnect other
  BLE devices.
- Wake first and wait for infotainment: `wake_up(wait=True)`. VCSEC status or
  a broadcast does not mean infotainment is ready (4-16s later).

## Snapshot, act, verify, restore

1. **Snapshot.** Read the absolute state the command changes with the narrowest
   reader (`charge_state()`, `climate_state()`, `closures_state()`,
   `media_state()`, `vehicle_state()`, ...). Read one `vehicle_data()` endpoint
   at a time: two or more together raise
   `TeslaFleetMessageFaultResponseSizeExceedsMTU`.
2. **Act.** Send the command once. Record the result or the exception class.
3. **Verify** with a new read of the same absolute state. Compare values,
   never the number of calls: `Commands._command` re-sends on `WAIT` and epoch
   faults, so a toggle or step can apply twice.
4. **Restore** the snapshot value with an absolute command, then read again to
   confirm. For shared settings, restore all of them: `set_scheduled_charging`
   and `set_scheduled_departure` share `scheduled_charging_mode`.

If the command times out or raises `BluetoothUnconfirmedCommand`, the car may
have executed it. Do not send it again. Read the state and decide from that.

## Commands you must not cycle automatically

- **Individual doors** (`open_*_door()`, Model 3): no reliable powered close.
  An ACK from a close command does not mean the door re-latched; a person must
  push it shut. Never put an individual door-open inside an automated
  snapshot, act, verify, restore loop. Do it only with a person at the car.
- **Media track and favourite** (`media_next_track`, `media_prev_track`,
  `media_next_fav`, `media_prev_fav`): `now_playing_*` and
  `media_detail_state()` stay empty for some sources (Spotify). Verify by ACK,
  then send the inverse command. Use `MediaState.audio_volume` and
  `MediaState.media_playback_status` as the state provers for media.

## Record the result

Add the finding to `OBSERVATIONS.md` under a dated heading. Keep the setup
(model, adapter or proxy, RSSI, key, keepalive), the date and the sample size
with it, so another run can re-check it. Record results that overturn an
earlier entry too, and update that entry.
