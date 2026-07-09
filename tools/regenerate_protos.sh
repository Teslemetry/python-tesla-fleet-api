#!/usr/bin/env bash
# Regenerate the *_pb2.py / *_pb2.pyi files from .proto sources.
#
# To make the file-level descriptor key unique (and avoid clashes with other
# libraries that also ship a bare "common.proto", "vehicle.proto", etc. in the
# global descriptor pool), the .proto sources live under proto/tesla/ so the
# descriptor name becomes "tesla/common.proto" instead of "common.proto".
#
# Usage:
#   tools/regenerate_protos.sh
#
# Requirements: protoc on PATH. The protoc version determines the version
# stamped into the generated gencode: under unified protobuf versioning,
# protoc vX.Y emits Python gencode 6.X.Y. Because protobuf refuses to load
# gencode newer than the installed runtime, and Home Assistant core pins
# protobuf==6.32.0, regenerate with protoc v32.0 (-> gencode 6.32.0) and keep
# the protobuf floor in pyproject.toml in sync with the stamped version. See
# the "Protobuf" section of AGENTS.md for the full rationale.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$REPO_ROOT/proto"
OUT_DIR="$REPO_ROOT/tesla_fleet_api/tesla/vehicle/proto"

STAGE="$(mktemp -d)"
TMP="$(mktemp -d)"
trap 'rm -rf "$STAGE" "$TMP"' EXIT

NS_DIR="$STAGE/tesla"
mkdir -p "$NS_DIR"

PROTOS=(
  common.proto
  errors.proto
  keys.proto
  signatures.proto
  managed_charging.proto
  vcsec.proto
  vehicle.proto
  car_server.proto
  universal_message.proto
  session.proto
)

# Copy the top-level .proto files into proto/tesla/, rewriting imports of our
# own files to be tesla/-prefixed. google/* imports are left alone.
for f in "${PROTOS[@]}"; do
  python3 - "$SRC_DIR/$f" "$NS_DIR/$f" <<'PY'
import re, sys
src, dst = sys.argv[1], sys.argv[2]
own = {"common.proto","errors.proto","keys.proto","signatures.proto",
       "managed_charging.proto","vcsec.proto","vehicle.proto",
       "car_server.proto","universal_message.proto","session.proto"}
text = open(src).read()
def repl(m):
    name = m.group(1)
    if name in own:
        return f'import "tesla/{name}"'
    return m.group(0)
text = re.sub(r'import\s+"([^"]+)"', repl, text)
open(dst, "w").write(text)
PY
done

# Generate into a temp dir, then move into the package, rewriting absolute
# `from tesla import X_pb2` imports to package-relative `from . import X_pb2`.
protoc \
  --proto_path="$STAGE" \
  --python_out="$TMP" \
  --pyi_out="$TMP" \
  "${PROTOS[@]/#/tesla/}"

for f in "${PROTOS[@]}"; do
  base="${f%.proto}"
  for ext in _pb2.py _pb2.pyi; do
    gen="$TMP/tesla/${base}${ext}"
    dst="$OUT_DIR/${base}${ext}"
    python3 - "$gen" "$dst" <<'PY'
import re, sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()
# `from tesla import X_pb2 as ...` -> `from . import X_pb2 as ...`
text = re.sub(r'^from tesla import ', 'from . import ', text, flags=re.M)
open(dst, "w").write(text)
PY
  done
done

echo "Regenerated $(printf '%s ' "${PROTOS[@]}")into $OUT_DIR"
echo "Descriptor pool keys are now prefixed with tesla/ (e.g. tesla/common.proto)."
