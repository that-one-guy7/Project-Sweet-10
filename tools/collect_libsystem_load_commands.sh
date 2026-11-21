#!/usr/bin/env bash
# Read-only host-side inspection of libSystem's Mach-O load commands.
# This script does not extract a binary or communicate with the iPhone.

set -u

IPSW="${IPSW:-$HOME/ipsw-standalone/ipsw}"
TARGET_CACHE="${TARGET_CACHE:-$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64}"
DONOR_CACHE="${DONOR_CACHE:-$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64}"
OUT="${OUT:-$HOME/agx-metal-static-audit/libsystem-load-commands}"
ARCHIVE="${ARCHIVE:-$HOME/agx-metal-static-audit/libsystem-load-command-logs.tar.gz}"
IMAGE="/usr/lib/libSystem.B.dylib"

test -x "$IPSW" || { echo "Standalone ipsw executable not found: $IPSW" >&2; exit 1; }
test -r "$TARGET_CACHE" || { echo "Target shared cache is not readable: $TARGET_CACHE" >&2; exit 1; }
test -r "$DONOR_CACHE" || { echo "Donor shared cache is not readable: $DONOR_CACHE" >&2; exit 1; }

mkdir -p "$OUT" "$(dirname "$ARCHIVE")"
: > "$OUT/query-status.tsv"
FAILED=0

run_one() {
  local label="$1"
  local cache="$2"
  local log="$OUT/$label-libSystem-loads.json"
  local err="$OUT/$label-libSystem-loads.err"
  local status

  if "$IPSW" dyld macho "$cache" "$IMAGE" --loads --json > "$log" 2> "$err"; then
    status=0
  else
    status=$?
    FAILED=1
  fi
  printf '%s\t%s\t%s\n' "$label" "$IMAGE" "$status" >> "$OUT/query-status.tsv"
  printf '%s libSystem load commands: exit %s\n' "$label" "$status"
}

run_one 19H422 "$TARGET_CACHE"
run_one 20H392 "$DONOR_CACHE"

if ! tar -czf "$ARCHIVE" -C "$OUT" .; then
  echo "Failed to create libSystem load-command archive: $ARCHIVE" >&2
  exit 1
fi

echo "=== query status ==="
cat "$OUT/query-status.tsv"
echo "Archive: $ARCHIVE"
ls -lh "$ARCHIVE"

if [ "$FAILED" -ne 0 ]; then
  echo "One or more queries failed; inspect the status table and .err files." >&2
  exit 2
fi
