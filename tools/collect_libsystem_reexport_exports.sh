#!/usr/bin/env bash
# Collect export logs for the exact LC_REEXPORT_DYLIB paths found in the
# uploaded 19H422 / 20H392 libSystem.B.dylib load-command JSON.
# Read-only host-side shared-cache queries; never connects to the phone.

set -u

IPSW="${IPSW:-$HOME/ipsw-standalone/ipsw}"
TARGET_CACHE="${TARGET_CACHE:-$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64}"
DONOR_CACHE="${DONOR_CACHE:-$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64}"
OUT="${OUT:-$HOME/agx-metal-static-audit/libsystem-reexport-exports}"
ARCHIVE="${ARCHIVE:-$HOME/agx-metal-static-audit/libsystem-reexport-export-logs.tar.gz}"

test -x "$IPSW" || { echo "Standalone ipsw executable not found: $IPSW" >&2; exit 1; }
test -r "$TARGET_CACHE" || { echo "Target shared cache is not readable: $TARGET_CACHE" >&2; exit 1; }
test -r "$DONOR_CACHE" || { echo "Donor shared cache is not readable: $DONOR_CACHE" >&2; exit 1; }

mkdir -p "$OUT" "$(dirname "$ARCHIVE")"
: > "$OUT/query-status.tsv"
FAILED=0

run_one() {
  local label="$1"
  local cache="$2"
  local image="$3"
  local key
  local log
  local err
  local status
  key="$(basename "$image" .dylib)"
  log="$OUT/$label-$key.txt"
  err="$OUT/$label-$key.err"

  if "$IPSW" dyld macho "$cache" "$image" --symbols -V > "$log" 2> "$err"; then
    status=0
  else
    status=$?
    FAILED=1
  fi
  printf '%s\t%s\t%s\t%s\n' "$label" "$key" "$image" "$status" >> "$OUT/query-status.tsv"
  printf '%s %s: exit %s\n' "$label" "$key" "$status"
}

TARGET_IMAGES=(
  "/usr/lib/system/libcache.dylib"
  "/usr/lib/system/libcommonCrypto.dylib"
  "/usr/lib/system/libcompiler_rt.dylib"
  "/usr/lib/system/libcopyfile.dylib"
  "/usr/lib/system/libcorecrypto.dylib"
  "/usr/lib/system/libdispatch.dylib"
  "/usr/lib/system/libdyld.dylib"
  "/usr/lib/system/libmacho.dylib"
  "/usr/lib/system/libremovefile.dylib"
  "/usr/lib/system/libsystem_asl.dylib"
  "/usr/lib/system/libsystem_blocks.dylib"
  "/usr/lib/system/libsystem_c.dylib"
  "/usr/lib/system/libsystem_collections.dylib"
  "/usr/lib/system/libsystem_configuration.dylib"
  "/usr/lib/system/libsystem_containermanager.dylib"
  "/usr/lib/system/libsystem_coreservices.dylib"
  "/usr/lib/system/libsystem_darwin.dylib"
  "/usr/lib/system/libsystem_dnssd.dylib"
  "/usr/lib/system/libsystem_featureflags.dylib"
  "/usr/lib/system/libsystem_info.dylib"
  "/usr/lib/system/libsystem_m.dylib"
  "/usr/lib/system/libsystem_malloc.dylib"
  "/usr/lib/system/libsystem_networkextension.dylib"
  "/usr/lib/system/libsystem_notify.dylib"
  "/usr/lib/system/libsystem_product_info_filter.dylib"
  "/usr/lib/system/libsystem_sandbox.dylib"
  "/usr/lib/system/libsystem_kernel.dylib"
  "/usr/lib/system/libsystem_platform.dylib"
  "/usr/lib/system/libsystem_pthread.dylib"
  "/usr/lib/system/libsystem_symptoms.dylib"
  "/usr/lib/system/libsystem_trace.dylib"
  "/usr/lib/system/libunwind.dylib"
  "/usr/lib/system/libxpc.dylib"
)

DONOR_IMAGES=(
  "/usr/lib/system/libcache.dylib"
  "/usr/lib/system/libcommonCrypto.dylib"
  "/usr/lib/system/libcompiler_rt.dylib"
  "/usr/lib/system/libcopyfile.dylib"
  "/usr/lib/system/libcorecrypto.dylib"
  "/usr/lib/system/libdispatch.dylib"
  "/usr/lib/system/libdyld.dylib"
  "/usr/lib/system/libmacho.dylib"
  "/usr/lib/system/libremovefile.dylib"
  "/usr/lib/system/libsystem_asl.dylib"
  "/usr/lib/system/libsystem_blocks.dylib"
  "/usr/lib/system/libsystem_c.dylib"
  "/usr/lib/system/libsystem_collections.dylib"
  "/usr/lib/system/libsystem_configuration.dylib"
  "/usr/lib/system/libsystem_containermanager.dylib"
  "/usr/lib/system/libsystem_coreservices.dylib"
  "/usr/lib/system/libsystem_darwin.dylib"
  "/usr/lib/system/libsystem_dnssd.dylib"
  "/usr/lib/system/libsystem_featureflags.dylib"
  "/usr/lib/system/libsystem_info.dylib"
  "/usr/lib/system/libsystem_m.dylib"
  "/usr/lib/system/libsystem_malloc.dylib"
  "/usr/lib/system/libsystem_networkextension.dylib"
  "/usr/lib/system/libsystem_notify.dylib"
  "/usr/lib/system/libsystem_sandbox.dylib"
  "/usr/lib/system/libsystem_kernel.dylib"
  "/usr/lib/system/libsystem_platform.dylib"
  "/usr/lib/system/libsystem_pthread.dylib"
  "/usr/lib/system/libsystem_symptoms.dylib"
  "/usr/lib/system/libsystem_trace.dylib"
  "/usr/lib/system/libunwind.dylib"
  "/usr/lib/system/libxpc.dylib"
)

for image in "${TARGET_IMAGES[@]}"; do
  run_one 19H422 "$TARGET_CACHE" "$image"
done
for image in "${DONOR_IMAGES[@]}"; do
  run_one 20H392 "$DONOR_CACHE" "$image"
done

if ! tar -czf "$ARCHIVE" -C "$OUT" .; then
  echo "Failed to create re-export provider archive: $ARCHIVE" >&2
  exit 1
fi

echo "=== parser query status ==="
cat "$OUT/query-status.tsv"
echo "Archive: $ARCHIVE"
ls -lh "$ARCHIVE"

if [ "$FAILED" -ne 0 ]; then
  echo "One or more re-export provider queries failed; inspect the status table and .err files." >&2
  exit 2
fi
