# Setting up Tesla Charge on Solar manually (vehicle + Powerwall pairing)

Charge on Solar lets a Tesla vehicle charge from excess solar measured by a Powerwall gateway. The Tesla app normally sets it up. If the app's setup fails, or the pairing breaks and the app will not redo it, you can perform the same steps yourself through the Teslemetry API (see [Teslemetry](teslemetry.md) and [Fleet API for Energy Sites](fleet_api_energy_sites.md)).

This guide is generic: substitute your own VIN, energy site id and gateway DIN. Everything here acts only on a vehicle and energy site on your own account, using keys you already hold.

## What Charge on Solar needs

All four must be in place. Setting the preference alone (step 4) stores a setting and does nothing else.

1. **The gateway's key on the vehicle's key list**, with the role `ROLE_CHARGING_MANAGER`.
2. **The vehicle's key registered on the gateway** as an authorized client of type VEHICLE, identified by the VIN, in state VERIFIED.
3. **A managed charging site on the vehicle** naming the gateway: its public key, its DIN, and the site's coordinates (the car uses them to decide it is at the site).
4. **The Charge on Solar preference** on the vehicle, enabled, with lower and upper charge limits.

## Which key signs which step

| Step | Must be signed by | Will not work with | Sent through |
|---|---|---|---|
| 1. Add the gateway key to the vehicle | A vehicle key with the owner role, which is what a key card tap gives it; a driver key cannot add keys (for example a Bluetooth key you paired yourself, see [Bluetooth for Vehicles](bluetooth_vehicles.md#pair-vehicle)). The vehicle checks the signer's role, not the transport, so this key can be sent through the cloud. | A Fleet API virtual key: the vehicle answers `WhitelistOperationNoPermissionToAdd`. | `POST /api/1/vehicles/{vin}/signed_command` |
| 2. Register the vehicle on the gateway | An RSA key that is already a VERIFIED client on your gateway (for example the key a local Powerwall client enrolled). | An unverified key: the gateway requires a trusted signature. | `POST /api/1/energy_sites/{site_id}/device_command` |
| 3. Add the managed charging site | Teslemetry (server-signed). | | `POST /api/1/vehicles/{vin}/custom_command/add_managed_charging_site` |
| 4. Enable the preference | Teslemetry (server-signed). | | `POST /api/1/vehicles/{vin}/custom_command/charge_on_solar` |

So steps 3 and 4 need only your Teslemetry token. Steps 1 and 2 need keys only you hold: a key-card-tapped vehicle key, and an RSA key verified on your gateway.

## Before you start: gather the inputs

- `VIN`, and `SITE_ID` from `GET /api/1/products`.
- The **gateway DIN**, from the energy site's info.
- The **gateway's ECC public key**: `GET /api/1/energy_sites/{site_id}/command/signed_commands_public_key`. It returns `pubKeyEcc` as base64 DER (SubjectPublicKeyInfo). Steps 1 and 3 need it as the raw 65-byte uncompressed point (`04 || X || Y`), so convert it.
- The **vehicle's ECC public key**: the `publicKey` in the `SessionInfo` the vehicle returns when you open a signed-command session with any key paired to it.
- The **site coordinates** (latitude, longitude). Neither the products list nor site info carries them, so use where the car is parked at home.

## Step 1: add the gateway key to the vehicle

A VCSEC whitelist operation, signed by your key-card-tapped key and sent through `signed_command` (see [Fleet API with Signed Vehicle Commands](fleet_api_signed_commands.md)):

```
UnsignedMessage {
  WhitelistOperation {
    addKeyToWhitelistAndAddPermissions {
      key { PublicKeyRaw: <gateway ECC key, raw 65-byte point> }
      keyRole: ROLE_CHARGING_MANAGER
    }
  }
}
```

Read the result from `commandStatus.whitelistOperationStatus` in the reply.

## Step 2: register the vehicle on the gateway

An energy-device message carrying an `add_authorized_client_by_trusted_signature_request`, signed with your verified RSA key:

```
RoutableMessage {
  to_destination { domain: DOMAIN_ENERGY_DEVICE }
  protobuf_message_as_bytes: MessageEnvelope {
    authorization {
      add_authorized_client_by_trusted_signature_request {
        type: AUTHORIZED_CLIENT_TYPE_VEHICLE
        description: "Vehicle"
        key_type: ECC
        public_key: <vehicle ECC key, raw point>
        roles: [AUTHORIZATION_ROLE_VEHICLE]
        identifier: <VIN>
      }
    }
  }
  signature_data {
    signer_identity { public_key: <your RSA public key, PKCS#1 DER> }
    RSA_data { expires_at, signature }
  }
}
```

Signature: build a TLV of signature type (RSA), domain, personalization (the gateway DIN) and `expires_at`, then a `TAG_END` byte (`0xFF`), then the envelope bytes, and sign it with RSA PKCS#1 v1.5 + SHA-512. `tesla_fleet_api.tesla.energy_signing` implements this scheme.

Request body to Teslemetry:

```json
{ "identifier_type": 1, "target_id": "<gateway DIN>", "routable_message": "<base64 RoutableMessage>" }
```

Note: `identifier_type` must be the integer `1`. The string form is rejected upstream with `400 Invalid request`.

Check it worked: `GET /api/1/energy_sites/{site_id}/command/authorized_clients` should list a client with type VEHICLE, your VIN as identifier, and state VERIFIED. Tesla also notifies the account that a key was paired with the Powerwall.

## Step 3: add the managed charging site

```http
POST /api/1/vehicles/{vin}/custom_command/add_managed_charging_site
```

```json
{ "public_key": "<pubKeyEcc from step 'gather the inputs'>", "din": "<gateway DIN>", "latitude": <lat>, "longitude": <lon> }
```

Teslemetry converts the base64 DER key to the raw point. Confirm with `GET /api/1/vehicles/{vin}/custom_command/managed_charging_sites`. `python-tesla-fleet-api` has no helper for this route, so call it directly.

## Step 4: enable the preference

```http
POST /api/1/vehicles/{vin}/custom_command/charge_on_solar
```

```json
{ "enabled": true, "lowerChargeLimit": 0, "upperChargeLimit": 80 }
```

## Notes

- Do steps 1 and 2 first. Steps 3 and 4 can be repeated safely.
- The app's "charge on solar capable" flag is only checked by the app. A site that reports no such flag can still use the feature once the four steps are in place.
- To start over, turn the preference off, remove the managed charging site(s) from the vehicle, and remove the VEHICLE client from the gateway. Leave your phone's own gateway client and vehicle key alone. The gateway key stays on the vehicle, so skip step 1 if it is still there with the `ROLE_CHARGING_MANAGER` role. Then repeat steps 2 to 4.
- These commands write to your vehicle and gateway. Only run them against your own account, and keep your private keys off shared machines.
