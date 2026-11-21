#!/usr/bin/env bash
# Read-only host-side collection of provider export logs referenced by the
# AGXMetalA10/A11 LC_LOAD_DYLIB records. This script never talks to the phone.

set -u

IPSW="\${IPSW:-$HOME/ipsw-standalone/ipsw}"
TARGET_CACHE="\${TARGET_CACHE:-$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64}"
DONOR_CACHE="\${DONOR_CACHE:-$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64}"
OUT="\${OUT:-$HOME/agx-metal-static-audit/provider-symbols}"
ARCHIVE="\${ARCHIVE:-$HOME/agx-metal-static-audit/agx-provider-export-logs.tar.gz}"

test -x "$IPSW" || { echo "Standalone ipsw executable not found: $IPSW" >&2; exit 1; }
test -r "$TARGET_CACHE" || { echo "Target shared cache is not readable: $TARGET_CACHE" >&2; exit 1; }
test -r "$DONOR_CACHE" || { echo "Donor shared cache is not readable: $DONOR_CACHE" >&2; exit 1; }

mkdir -p "$OUT" "$(dirname "$ARCHIVE")"
: > "$OUT/query-status.tsv"

run_one() {
  LABEL="$1"
  CACHE="$2"
  KEY="$3"
  IMAGE="$4"
  LOG="$OUT/$LABEL-$KEY.txt"
  ERR="$OUT/$LABEL-$KEY.err"

  if "$IPSW" dyld macho "$CACHE" "$IMAGE" --symbols -V > "$LOG" 2> "$ERR"; then
    STATUS=0
  else
    STATUS=$?
  fi
  printf '%s\t%s\t%s\t%s\n' "$LABEL" "$KEY" "$IMAGE" "$STATUS" >> "$OUT/query-status.tsv"
  printf '%s %s: exit %s\n' "$LABEL" "$KEY" "$STATUS"
}

while IFS='|' read -r KEY IMAGE; do
  [ -n "$KEY" ] || continue
  run_one 19H422 "$TARGET_CACHE" "$KEY" "$IMAGE"
  run_one 20H392 "$DONOR_CACHE" "$KEY" "$IMAGE"
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

tar -czf "$ARCHIVE" -C "$OUT" .
echo "=== parser query status ==="
cat "$OUT/query-status.tsv"
echo "Archive: $ARCHIVE"
ls -lh "$ARCHIVE"
