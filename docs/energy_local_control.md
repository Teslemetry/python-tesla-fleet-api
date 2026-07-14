# Energy: Local Control (aiopowerwall + EnergySiteRouter)

This library and the sibling [`aiopowerwall`](https://pypi.org/project/aiopowerwall/)
library are designed to be used together to give an energy gateway (Powerwall
2/3) both a local, signed LAN control path and a cloud fallback:

- **This repo holds the keypair lifecycle.** `Tesla.get_rsa_private_key`
  generates or loads and persists the RSA key, `rsa_public_der_pkcs1` derives
  the public key bytes for registration, and
  `EnergySite.add_authorized_client` registers its public half with the
  gateway over the cloud. `aiopowerwall` deliberately does **not** implement
  registration - it only consumes an already-paired key.
- **aiopowerwall holds the local, RSA-signed transport.** Its
  `PowerwallEnergySite` adapter implements the local subset of this repo's
  `EnergySite` surface with matching names, signatures, and `dict[str, Any]`
  return shapes, without importing this package - it is duck-typed by design
  so it drops straight into `EnergySiteRouter`.

`aiopowerwall` is not a dependency of this project; nothing here imports it.
You add it to your own application alongside `tesla-fleet-api`.

## 1. Generate or load the RSA private key

`get_rsa_private_key(path)` (available on `Tesla` and everything that
inherits it - `TeslaFleetApi`, `Teslemetry`, `Tessie`) loads an existing RSA
private key or creates a new 4096-bit unencrypted PEM key file. This is the
key you will register with the gateway and later hand to `aiopowerwall`.

## 2. Register the key with the gateway, over the cloud

`EnergySite.add_authorized_client` registers the public half of that key with
the gateway. After registration the key sits in `PENDING`/
`PENDING_VERIFICATION` state (`AuthorizedClientState`) until the gateway
confirms it - either auto-verified via cloud, or by a physical breaker toggle
at the gateway.

```python
import aiohttp
from tesla_fleet_api import Teslemetry

async def register_key(session: aiohttp.ClientSession, energy_site_id: int):
    api = Teslemetry(access_token="<access_token>", session=session)

    # Creates tedapi_rsa_private.pem (mode 0600) on first run, or loads
    # the existing key on subsequent runs.
    await api.get_rsa_private_key("tedapi_rsa_private.pem")

    energy_site = api.energySites.create(energy_site_id)
    await energy_site.add_authorized_client(
        api.rsa_public_der_pkcs1_b64,
        description="My local control client",
    )
    return api, energy_site
```

## 3. Hand the paired key to aiopowerwall

`aiopowerwall`'s `PowerwallClient` consumes the *same* PEM file directly - it
does not need anything else from this library at this point. `local_energysite`
then exposes the locally implemented `EnergySite`-compatible calls
(`live_status()`, `operation()`, `backup()`, `set_island_mode()`,
`get_backup_events()`, and backup-event scheduling) through signed requests
directly to the gateway over the LAN:

```python
import aiohttp
from aiopowerwall import PowerwallClient
from aiopowerwall.energysite import PowerwallEnergySite

async def make_local_energysite(session: aiohttp.ClientSession) -> PowerwallEnergySite:
    with open("tedapi_rsa_private.pem", "rb") as f:
        rsa_private_key_pem = f.read()

    powerwall_client = PowerwallClient(
        host="192.168.91.1",       # the gateway's local IP
        gateway_password="<gateway-password>",  # local gateway password, not your Tesla account password
        rsa_private_key_pem=rsa_private_key_pem,
        session=session,
    )
    return PowerwallEnergySite(powerwall_client)
```

The example uses `192.168.91.1`, the gateway's own WiFi access point. When
your client connects over your own LAN instead, you can discover the
gateway's LAN IP over the cloud with
`TeslemetryEnergySite.find_gateway_address()`, which reads the gateway's
`networking_status` and returns the decoded IPv4 of its active `eth`/`wifi`
interface (or `None` when no usable interface is reported) - see
[Teslemetry](teslemetry.md#energy-site-gateway-address).

## 4. Verify the key is paired by using it

The gateway takes registration (step 2) and confirmation (auto-verify, or a
physical breaker toggle) as two separate events, and there is a window
between them where the key exists but is not yet usable. **The reliable way
to tell that window has closed is to attempt a signed local read through
`aiopowerwall` and retry until it succeeds** - a successful signed response
*is* proof the key is `VERIFIED`, because the gateway would otherwise reject
it.

`get_system_info()`/`get_status()`-style reads are the natural choice for
this, but `PowerwallEnergySite` does not implement them locally yet (they
raise `NotImplementedError` and would tell you nothing about the key - see
the `EnergySiteRouter` note in step 5). Use `live_status()` instead: it is
already implemented locally and, under the hood, issues a signed v1r
request, so it fails exactly the way an unverified key would fail.

Before verification, every signed request rejects with
`aiopowerwall.PowerwallAuthenticationError` (the gateway's "unknown key id"
or "authorization not verified" fault) - **that failure is expected and not
a bug**; treat it as "not yet, keep retrying" and back off between attempts:

```python
import asyncio
from aiopowerwall import PowerwallAuthenticationError
from aiopowerwall.energysite import PowerwallEnergySite

async def wait_until_verified(
    local_energysite: PowerwallEnergySite,
    attempts: int = 10,
    initial_delay: float = 5.0,
    max_delay: float = 60.0,
) -> None:
    delay = initial_delay
    for attempt in range(attempts):
        try:
            await local_energysite.live_status()
            return  # a successful signed read proves the key is VERIFIED
        except PowerwallAuthenticationError:
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(delay)
            delay = min(delay * 2, max_delay)
```

Only fall back to polling the cloud `list_authorized_clients()` (or, on
`Teslemetry`, `find_authorized_clients()`) as a **secondary, best-effort**
check - for example while you have no local network path to the gateway yet.
Tesla's cloud endpoint for this is undocumented, and Teslemetry's
`list_authorized_clients` in particular has been observed returning a bare
JSON `null` with a `200` status rather than an envelope; that behavior may
recur, so do not treat this endpoint as authoritative, and never let it
override a signed local read that already succeeded or failed.
`TeslemetryEnergySite.find_authorized_clients()` parses the recognized
shapes (list vs. dict envelope, `state` typing) into a typed
`AuthorizedClients`, but raises
`tesla_fleet_api.exceptions.InvalidResponse` on a null body or any other
unrecognized response shape so that malformed data is distinguishable from
a genuinely empty client list. Catch `InvalidResponse` (or
`TeslaFleetError`) around this call and treat it as "no signal" - note that
`TeslaFleetError` subclasses `BaseException`, so a bare `except Exception`
will not catch it. Either way, a `null` response here tells you nothing
about whether the key actually works.

## 5. Compose local + cloud with EnergySiteRouter

```python
import asyncio
import aiohttp
from tesla_fleet_api.router import EnergySiteRouter

async def main():
    async with aiohttp.ClientSession() as session:
        api, teslemetry_energysite = await register_key(session, energy_site_id=12345)
        local_energysite = await make_local_energysite(session)
        await wait_until_verified(local_energysite)

        router = EnergySiteRouter(local_energysite, teslemetry_energysite)

        status = await router.live_status()  # tries local first, cloud on failure
        print(status)

asyncio.run(main())
```

Locally implemented commands go over the LAN when the gateway is reachable,
and fail over to the Teslemetry cloud otherwise - the same
local-primary/cloud-fallback pattern `VehicleRouter` uses for vehicles. Calls
that aiopowerwall does not implement locally yet, including `get_system_info()`
and most energy-device gRPC commands, raise `NotImplementedError` from the
local adapter and then fall through to the cloud backend. See [the README's
Routing and Failover section](../README.md#routing-and-failover) for the
general `Router` semantics (per-command failover, the double-execution caveat,
and the `health` check).

> **Warning: island mode / off-grid actuation is not guaranteed on either
> transport - always verify by state.**
>
> This repo's cloud `EnergySite.set_island_mode()` / `go_off_grid()` /
> `reconnect_grid()` send an **unsigned** `grpc_command`. Per their own
> docstrings and the commits that added them, the gateway accepts this
> command but does **not** physically operate the grid contactor over that
> transport - a plain cloud-only `EnergySite` (no router, no local backend)
> gets a silent no-op with an OK-looking response.
>
> Routing through `EnergySiteRouter` with an `aiopowerwall` local primary is
> the intended way to actually operate the contactor, since it sends a
> signed request over the LAN. But `aiopowerwall`'s own docs carry an
> unresolved, firmware-dependent caveat for its local `set_island_mode`
> too - some gateways acknowledge it without acting on it, and
> `trigger_islanding()` (the explicit black-start command) may be needed as
> a fallback.
>
> In both cases a success-shaped response does not prove the contactor
> moved, and `Router` has no way to detect that on its own - a call that
> returns without raising looks identical whether it actuated or not, so
> failover to the cloud secondary will not trigger. Always confirm the
> actual outcome with a signed local status read (for example
> `live_status()`'s grid/island fields) before trusting either path's
> response for anything actuation-critical.

## See also

- [Fleet API for Energy Sites](fleet_api_energy_sites.md) - the cloud
  `EnergySite` command surface (`get_rsa_private_key`, the gRPC "Device
  Commands" section) on its own, without a local backend.
- [Routing and Failover](../README.md#routing-and-failover) - the general
  `Router`/`EnergySiteRouter` dispatch and failover semantics.
- `aiopowerwall`'s own README for local-only concerns: gateway pairing
  (breaker toggle / auto-verify), backup-reserve and SoC scaling, and
  multi-Powerwall leader/follower behavior.
