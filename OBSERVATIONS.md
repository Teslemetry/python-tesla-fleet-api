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
