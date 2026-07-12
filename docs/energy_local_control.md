# Energy: Local Control (aiopowerwall + EnergySiteRouter)

This library and the sibling [`aiopowerwall`](https://pypi.org/project/aiopowerwall/)
library are designed to be used together to give an energy gateway (Powerwall
2/3) both a local, signed LAN control path and a cloud fallback:

- **This repo holds the keypair lifecycle.** `Tesla.get_rsa_private_key` /
  `rsa_public_der_pkcs1` generate and persist the RSA key, and
  `EnergySite.add_authorized_client` registers its public half with the
  gateway over the cloud. `aiopowerwall` deliberately does **not** implement
  registration - it only consumes an already-paired key.
- **aiopowerwall holds the local, RSA-signed transport.** Its
  `PowerwallEnergySite` adapter mirrors this repo's `EnergySite` method-for-
  method (same names, signatures, and `dict[str, Any]` return shapes) without
  importing this package - it is duck-typed by design so it drops straight
  into `EnergySiteRouter`.

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

Poll `list_authorized_clients()` (or, on `Teslemetry`,
`find_authorized_clients()`) until the key shows `VERIFIED`. Keep the wording
of that check resilient: Tesla's cloud endpoint for this is undocumented, and
Teslemetry's `list_authorized_clients` in particular has been observed
returning a bare JSON `null` with a `200` status rather than an envelope -
treat that as "not verified yet, keep polling," not as an error.
`TeslemetryEnergySite.find_authorized_clients()` already does this parsing
for you (null body, list vs. dict envelope, `state` typing) and always
returns a typed `AuthorizedClients` with `clients == []` rather than raising.
(`find_authorized_clients` is only on `TeslemetryEnergySite`. Plain
`TeslaFleetApi`/`Tessie` callers use the untyped `list_authorized_clients()`
and should apply the same "null/unrecognized shape means not-yet" tolerance
themselves.)

Steps 1 and 2 together:

```python
import asyncio
import aiohttp
from tesla_fleet_api import Teslemetry
from tesla_fleet_api.const import AuthorizedClientState

async def pair_key(session: aiohttp.ClientSession, energy_site_id: int) -> None:
    api = Teslemetry(access_token="<access_token>", session=session)

    # Creates tedapi_rsa_private.pem (mode 0600) on first run, or loads
    # the existing key on subsequent runs.
    await api.get_rsa_private_key("tedapi_rsa_private.pem")

    energy_site = api.energySites.create(energy_site_id)
    await energy_site.add_authorized_client(
        api.rsa_public_der_pkcs1,
        description="My local control client",
    )

    for _ in range(30):
        result = await energy_site.find_authorized_clients()
        verified = [
            c for c in result.clients
            if c.state == AuthorizedClientState.VERIFIED
        ]
        if verified:
            return
        await asyncio.sleep(10)
    raise TimeoutError("Key was not verified in time")

async def main():
    async with aiohttp.ClientSession() as session:
        await pair_key(session, energy_site_id=12345)  # id from api.products()

asyncio.run(main())
```

## 3. Hand the paired key to aiopowerwall

Once the key is verified, `aiopowerwall`'s `PowerwallClient` consumes the
*same* PEM file directly - it does not need anything else from this library
at this point. `local_energysite` then exposes the same method surface as
this repo's `EnergySite` (`get_system_info()`, `live_status()`,
`set_island_mode()`, etc.), but issues signed requests directly to the
gateway over the LAN:

```python
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

## 4. Compose local + cloud with EnergySiteRouter

```python
from tesla_fleet_api import Teslemetry
from tesla_fleet_api.router import EnergySiteRouter

async def main():
    async with aiohttp.ClientSession() as session:
        local_energysite = await make_local_energysite(session)

        api = Teslemetry(access_token="<access_token>", session=session)
        teslemetry_energysite = api.energySites.create(12345)

        router = EnergySiteRouter(local_energysite, teslemetry_energysite)

        status = await router.live_status()  # tries local first, cloud on failure
        print(status)

asyncio.run(main())
```

Commands go over the LAN when the gateway is reachable, and fail over to the
Teslemetry cloud otherwise - the same local-primary/cloud-fallback pattern
`VehicleRouter` uses for vehicles. See [the README's Routing and Failover
section](../README.md#routing-and-failover) for the general `Router`
semantics (per-command failover, the double-execution caveat, and the
`health` check).

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
> actual outcome with a status read (e.g. `live_status()`'s grid/island
> fields, or aiopowerwall's `get_status()` `islanding.contactorClosed`)
> before trusting either path's response for anything actuation-critical.

## See also

- [Fleet API for Energy Sites](fleet_api_energy_sites.md) - the cloud
  `EnergySite` command surface (`get_rsa_private_key`, the gRPC "Device
  Commands" section) on its own, without a local backend.
- [Routing and Failover](../README.md#routing-and-failover) - the general
  `Router`/`EnergySiteRouter` dispatch and failover semantics.
- `aiopowerwall`'s own README for local-only concerns: gateway pairing
  (breaker toggle / auto-verify), backup-reserve and SoC scaling, and
  multi-Powerwall leader/follower behavior.
