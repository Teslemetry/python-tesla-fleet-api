//go:build ignore

// Generates tests/fixtures/ss256_vectors.json, the Tesla.SS256 cross-check
// vectors for tesla_fleet_api/tesla/jws.py, from Tesla's own Go implementation.
//
// It imports vehicle-command internal packages, so it must run inside that
// module:
//
//	git clone https://github.com/teslamotors/vehicle-command
//	mkdir vehicle-command/cmd/ss256vector
//	cp tests/fixtures/ss256_vectors_gen.go vehicle-command/cmd/ss256vector/main.go
//	(cd vehicle-command && go run cmd/ss256vector/main.go) > vectors.json
//
// then merge the output into the fixture, keeping its "_provenance" and the
// "jws.config" claims (the same JSON this program signs).
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"

	"github.com/golang-jwt/jwt/v5"
	"github.com/teslamotors/vehicle-command/internal/authentication"
	"github.com/teslamotors/vehicle-command/pkg/sign"
)

type sigVector struct {
	Scalar    string `json:"scalar"`
	Public    string `json:"public"`
	Message   string `json:"message_hex"`
	Signature string `json:"signature"`
}

func main() {
	testScalar := make([]byte, 32)
	testScalar[0] = 3
	h := sha256.Sum256([]byte("python-tesla-fleet-api SS256 vector key"))
	altScalar := h[:]

	var sigs []sigVector
	for _, scalar := range [][]byte{testScalar, altScalar} {
		key := authentication.UnmarshalECDHPrivateKey(scalar)
		for _, msg := range []string{"hello world", "", "eyJhbGciOiJUZXNsYS5TUzI1NiIsInR5cCI6IkpXVCJ9.e30"} {
			sig, err := key.SchnorrSignature([]byte(msg))
			if err != nil {
				panic(err)
			}
			sigs = append(sigs, sigVector{
				Scalar:    hex.EncodeToString(scalar),
				Public:    hex.EncodeToString(key.PublicBytes()),
				Message:   hex.EncodeToString([]byte(msg)),
				Signature: hex.EncodeToString(sig),
			})
		}
	}

	key := authentication.UnmarshalECDHPrivateKey(altScalar)
	var config jwt.MapClaims
	if err := json.Unmarshal([]byte(`{"hostname":"telemetry.example.com","port":443,"ca":"-----BEGIN CERTIFICATE-----\nMIIB\n-----END CERTIFICATE-----\n","exp":1790000000,"fields":{"Locked":{"interval_seconds":60},"BatteryLevel":{"interval_seconds":300}},"alert_types":["service"]}`), &config); err != nil {
		panic(err)
	}
	token, err := sign.SignMessageForFleet(key, "TelemetryClient", config)
	if err != nil {
		panic(err)
	}
	out := map[string]interface{}{
		"signatures": sigs,
		"jws": map[string]interface{}{
			"scalar": hex.EncodeToString(altScalar),
			"token":  token,
		},
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(out); err != nil {
		panic(err)
	}
	fmt.Fprintln(os.Stderr, "ok")
}
