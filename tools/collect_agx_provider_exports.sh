#!/usr/bin/env bash
# Read-only host-side collection of provider export logs referenced by the
# AGXMetalA10/A11 LC_LOAD_DYLIB records. This script never talks to the phone.

set -u

IPSW="${IPSW:-$HOME/ipsw-standalone/ipsw}"
TARGET_CACHE="${TARGET_CACHE:-$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64}"
DONOR_CACHE="${DONOR_CACHE:-$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64}"
OUT="${OUT:-$HOME/agx-metal-static-audit/provider-symbols}"
ARCHIVE="${ARCHIVE:-$HOME/agx-metal-static-audit/agx-provider-export-logs.tar.gz}"

test -x "$IPSW" || { echo "Standalone ipsw executable not found: $IPSW" >&2; exit 1; }
test -r "$TARGET_CACHE" || { echo "Target shared cache is not readable: $TARGET_CACHE" >&2; exit 1; }
test -r "$DONOR_CACHE" || { echo "Donor shared cache is not readable: $DONOR_CACHE" >&2; exit 1; }

mkdir -p "$OUT" "$(dirname "$ARCHIVE")"
: > "$OUT/query-status.tsv"
FAILED=0

run_one() {
  local label="$1"
  local cache="$2"
  local key="$3"
  local image="$4"
  local log="$OUT/$label-$key.txt"
  local err="$OUT/$label-$key.err"
  local status

  if "$IPSW" dyld macho "$cache" "$image" --symbols -V > "$log" 2> "$err"; then
    status=0
  else
    status=$?
    FAILED=1
  fi
  printf '%s\t%s\t%s\t%s\n' "$label" "$key" "$image" "$status" >> "$OUT/query-status.tsv"
  printf '%s %s: exit %s\n' "$label" "$key" "$status"
}

while IFS='|' read -r key image; do
  [ -n "$key" ] || continue
  run_one 19H422 "$TARGET_CACHE" "$key" "$image"
  run_one 20H392 "$DONOR_CACHE" "$key" "$image"
done <<'PROVIDERS'
AggregateDictionary|/System/Library/PrivateFrameworks/AggregateDictionary.framework/AggregateDictionary
CoreAnalytics|/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics
Foundation|/System/Library/Frameworks/Foundation.framework/Foundation
GPURawCounter|/System/Library/PrivateFrameworks/GPURawCounter.framework/GPURawCounter
libMobileGestalt|/usr/lib/libMobileGestalt.dylib
libSystem|/usr/lib/libSystem.B.dylib
libcxx|/usr/lib/libc++.1.dylib
CoreFoundation|/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation
libobjc|/usr/lib/libobjc.A.dylib
PROVIDERS

if ! tar -czf "$ARCHIVE" -C "$OUT" .; then
  echo "Failed to create provider export archive: $ARCHIVE" >&2
  exit 1
fi

echo "=== parser query status ==="
cat "$OUT/query-status.tsv"
echo "Archive: $ARCHIVE"
ls -lh "$ARCHIVE"

if [ "$FAILED" -ne 0 ]; then
  echo "One or more provider queries failed; inspect the status table and .err files." >&2
  exit 2
fi
