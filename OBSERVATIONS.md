# Live vehicle observations

Measured behaviour of real vehicles that the library's design depends on. Add
to this when a live experiment settles (or overturns) a question; keep the
setup, date and sample size with each finding so it can be re-checked.

## BLE wake and infotainment readiness (2026-09-29)

**Setup:** Model 3, macOS CoreBluetooth direct to the car
(RSSI about -73), whitelisted key, `keepalive_interval=None`. Harness:
`test_wake.py` (gitignored, alongside `test_bluetooth.py`), which logs every
BLE broadcast, VCSEC read and INFO attempt with millisecond timestamps, with
the Teslemetry SSE stream as an out-of-band cross-check only. Times below are
relative to the RKE wake write.

### Wake to infotainment ready

| Run | Wake acked | VCSEC reports AWAKE | First INFO handshake answered |
|---|---|---|---|
| probe 1 | +0.36s | +0.45s (broadcast) | <= +6.3s (5s probe timeout, coarse) |
| probe 2 | +0.27s | - | +8.76s |
| probe 3 | +0.36s | - | +8.67s |
| probe 4 | +0.39s | - | +6.69s |
| `wait=True`, short sleep | - | - | +4.1s |
| `wait=True`, ~10 min sleep | - | - | +16.4s (see resend below) |
| boot (plain wake, then command) | +0.21s | +0.45s (broadcast) | ~+5.5s |

- **VCSEC being awake does not mean infotainment is ready.** VCSEC acks the
  wake in ~0.3s and reports AWAKE (read or broadcast) by ~0.5s; infotainment
  answers a handshake 4-16s later. Neither VCSEC status nor any broadcast can
  signal readiness, so `wake_up(wait=True)` polls the INFO handshake itself.
- **A ready infotainment answers a handshake in 0.26-0.39s**, and a signed
  command sent straight after one succeeds (268-325ms, first attempt, every
  run). That is why the per-probe timeout is 1.0s.
- **Wake re-send after a long sleep:** in the 16.4s run, six handshakes failed
  over 10s after the first wake; infotainment answered 5.5s after the wake was
  re-sent, matching the normal wake-to-ready delay. Suggests a first wake can
  fail to bring infotainment up after a long sleep (one sample, not
  isolated). The re-send interval is now 3s: BLE traffic is local and free.
- **No infotainment-domain broadcasts** were observed in any run (0 across all
  sessions). VCSEC broadcasts are sparse (about 5 in the second after a wake)
  and not relied on.

### Sleep

- **A held BLE connection keeps the car awake** (also the owner's experience).
  Connected (VCSEC read every 30s), it stayed awake 35+ min after a
  `flash_lights`; once, ~9 min after the link was dropped it went quiet, but
  another time it stayed `online` for over an hour with no BLE link at all, so
  other factors matter too. Keepalive reads (`keepalive_interval`) keep it
  awake by design.
- **Woken and left idle, it re-slept after ~76-78s** (3 runs, only
  `ping`/handshakes sent, link held but otherwise idle). After a real action
  (`flash_lights`) it stayed awake far longer; not characterised.
- **The cloud can report `offline` rather than `asleep`** for a sleeping car
  that has dropped Wi-Fi; don't gate on `state == "asleep"` alone.

### Other

- **A VCSEC read issued ~0.3s after the wake did not return within 20s** in all
  three probe runs (the harness watchdog cancelled it); the next read succeeded
  in ~0.3s. The same read issued 5s after a wake returned in 157ms. Likely
  `Commands._command`'s `OPERATIONSTATUS_WAIT` retries while VCSEC is
  mid-wake, but not confirmed. The library never reads VCSEC that soon after
  its own wake.
- **Connecting is unreliable at range.** With the Mac further away, GATT connect
  failed for 20+ consecutive ~40s attempts while scans still saw the car;
  moving closer and disconnecting other BLE devices fixed it.

## Fleet API wake

Not measured here. `VehicleFleet.wake_up(wait=True)` polls `vehicle()` every
3s for `state == "online"` rather than re-POSTing the rate-limited wake.

## Charge-port release and sleeping closures (2026-10-09)

**Setup:** Model 3, vehicle firmware 2026.26.6.3, Home Assistant 2026.10.0,
Teslemetry using `tesla-fleet-api` 1.17.3 / `tesla-protocol` 3.0.2 through an
ESPHome Bluetooth proxy and a whitelisted signing key. The direct probing
harness used `keepalive_interval=None` and `wake_if_asleep=False`; RSSI was not
recorded. The frunk/boot commands used the existing HA integration; its keepalive
setting was not captured for these trials. These observations used the existing
library, not the proposed physical-confirmation change.

- **Reported symptom, not a captured failing trace:** an opening request with
  the cable plugged into a sleeping car woke it without releasing the latch;
  another request 1-2 seconds later released it promptly. The first request's
  exact response and charging state were not captured, so charging interlocks
  and wake timing remain hypotheses rather than an established root cause.
- **Latch observation:** 90 direct BLE charge-state reads, zero read errors,
  during one awake session. Explicit `charge_port_latch` changed from `Engaged`
  to `Disengaged` when the owner confirmed physical release. The separate
  `charge_cable_unlatched` flag stayed false. This demonstrates the latch field
  on this vehicle in that session; it does not establish its reliability while
  asleep, the reverse transition, or behavior on other vehicles/firmware.
- **Frunk:** one trial with direct VCSEC ASLEEP observed at 01:15:11 UTC, then
  one HA open request logged as Bluetooth success at 01:16:21.939 UTC. The owner
  confirmed it physically opened and later closed it.
- **Boot:** one trial with Fleet API asleep at 02:15:32 UTC, then one HA open
  request logged as Bluetooth success at 02:15:50.507 UTC. The owner confirmed
  it physically opened and later closed it. Neither closure trial had a
  recorded cloud fallback. One successful trial each does not establish
  universal reliability, but these trials do not reproduce the charge-port
  symptom for frunk or boot.

Sharing the VCSEC transport does not imply identical actuator or interlock
behavior. Keep the charge-port change scoped to that operation. The proposed
wake/readiness sequencing and post-command latch verification are tested
separately below; mocked regressions alone are not live acceptance.

### Isolated patched charge-port trials

**Setup:** Same vehicle, firmware and proxy as above, using an isolated copy of
the modified library in a separate process inside the HA container; the installed
library was not replaced. `confirmation="verify"`, `wake_if_asleep=True`,
`raise_unconfirmed=False` and `keepalive_interval=None`. The proxy's HA entry was
temporarily disabled to release its existing BLE connection. Charging was
stopped, the cable remained inserted, and pre-command BLE charge state had to
report a known connected cable and `charge_port_latch=Engaged`. The harness
counted actual GATT writes and disconnected BLE and the proxy API after the
command. The HA proxy entry was restored to enabled and loaded afterwards;
charging controls were unchanged. RSSI was not captured.

- **Asleep trial 1 (03:41 UTC):** the patched command's VCSEC preflight reported
  `ASLEEP`. The existing wake helper wrote two wake requests before INFO
  readiness. A fresh charge-state read reported `IEC`, `Stopped` and `Engaged`.
  Exactly one opening request was written at 03:41:15.731 UTC. After its ACK,
  the first charge-state read still reported `Engaged`; the second reported
  `Disengaged` at 03:41:17.109 UTC. The command returned success after 7.369s,
  with release state observed 1.378s after the opening write. No second opening
  request or cloud command was issued. The owner did not observe physical
  release, so that result is unknown.
- **Awake baseline (03:49 UTC):** the owner first confirmed the cable was locked
  in place. VCSEC preflight reported `AWAKE`, and BLE charge state reported
  `IEC`, `Stopped` and `Engaged`. Exactly one opening request was written at
  03:49:23.176 UTC, with no wake requests. A first post-command read still
  reported `Engaged`; the second reported `Disengaged` at 03:49:24.610 UTC
  (1.434s after the opening write). The command returned success in 2.762s.
  The owner confirmed the cable latch physically released without pressing
  the plug button.
- **Asleep trial 2 (03:55 UTC):** VCSEC preflight reported `ASLEEP` at
  03:55:34.266 UTC. After two wake writes and INFO readiness, fresh charge state
  reported `IEC`, `Stopped` and `Engaged`. Exactly one opening request was
  written at 03:55:39.801 UTC and ACKed. The first post-command read still
  reported `Engaged` at 03:55:40.554 UTC. The BLE link dropped at
  03:55:42.561 UTC before the next read completed, and the command raised
  `BluetoothUnconfirmedCommand` after 11.520s, despite
  `raise_unconfirmed=False`. The owner confirmed the cable latch physically
  released without pressing the plug button; physical release timing was not
  measured. No second opening request was sent. A later read-only connection
  also dropped before a state read completed, with no wake or opening writes.
- **Connection failures, excluded from command trials:** two connection
  attempts timed out before any wake or opening request. Read-only connections
  and command trials also succeeded. Advertisement subscription and diagnostic
  logging changed after the first failure, but the later timeout still
  occurred, so a cause was not isolated. The link drops above likewise do not
  establish a range, proxy, phone or vehicle cause.

**Sample and limits:** two asleep trials and one awake trial, each with exactly
one opening write. The awake trial confirmed both physical release and a
successful verified return. Of the asleep trials, one returned verified success
without owner observation; the other physically released the latch but returned
unconfirmed after a link drop. Neither asleep trial therefore establishes both
results together. These isolated processes exercised `VehicleBluetooth`, not
the HA service or router; cloud fallback was not configured. This supports the
wake/readiness sequencing on this vehicle and the refusal to report verified
success after lost state evidence. The HA trial below supplies the combined
asleep-state and physical acceptance check missing from these isolated trials.
The original failure's cause and behavior on other vehicles remain unproven.

### Node-RED / Home Assistant acceptance trial

**Setup:** Same vehicle, firmware, HA and ESPHome proxy. The charge-port-only
diff was temporarily applied to the installed 1.17.3 library, preserving its
existing frame parser rather than adding unrelated changes from repository
HEAD. Both original files were backed up and hash-checked. The temporary
backport passed 146 targeted tests / 49 subtests with `tesla-protocol` 3.0.2,
and all 32 new charge-port tests inside HA's actual Python 3.14 environment.
HA was restarted to load the change; its existing `confirmation="verify"`,
`raise_unconfirmed=False` and `keepalive_interval=None` settings were unchanged.
The proxy remained enabled and the Node-RED flow was unchanged. Command/state
logs and HA service events were captured; no GATT-write counter was installed
for this trial. RSSI was not captured.

- **One trial, 04:17-04:18 UTC:** after advance warning, the owner double-pressed
  the existing garage switch once. Its Node-RED flow invoked the charge-cable
  lock's HA `lock.unlock` service once at 04:17:50.986 UTC. The command's VCSEC
  preflight reported `ASLEEP` at 04:17:59.721 UTC. Two successful RKE wake
  operations were logged before fresh charge state reported `IEC`, `Stopped`
  and `Engaged` at 04:18:06.102 UTC. A VCSEC closure request was acknowledged
  at 04:18:06.497 UTC. The first post-command read still reported `Engaged`;
  the next reported `Disengaged` at 04:18:07.699 UTC. The library logged
  `physical_confirmation=confirmed`, and the router logged
  `charge_port_door_open` success on `VehicleBluetooth`, with no recorded cloud
  fallback for that operation. Verification completed about 16.7s after the
  HA service invocation, including connection and wake time. The owner confirmed
  physical latch release without pressing the plug button or repeating the
  trigger. Physical release time was not separately measured.
- **Restore:** the latch subsequently reported locked again. Both original
  library hashes were restored and checked again after a second HA restart.
  Teslemetry and the proxy were enabled and loaded. No Node-RED flow or charging
  control was modified by the test. Charging was stopped throughout the unlock
  and confirmation; it resumed later in the existing installation.

This trial establishes one complete asleep-to-release-and-verified-success
result through the user's actual Node-RED / HA / Bluetooth path. Together with
the awake baseline, it meets the live acceptance checks for this vehicle. One
successful asleep acceptance trial does not establish universal reliability,
the cause of the earlier isolated connection drops, or the root cause of the
original uncaptured failure. The installed library was restored after testing;
this was not a permanent deployment.
