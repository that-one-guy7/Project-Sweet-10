# iOS 20H392 GUI framework PrebuiltLoader capture plan

## Purpose

The iPhone 7 target-reference cache (19H422) now has successful `ipsw dyld image` captures for these three framework images:

- `/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard`
- `/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard`
- `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices`

The target records are documented in
[the 19H422 results report](iphone91-19h422-gui-framework-loader-results.md).
The matching framework records have not yet been captured from the selected
iPhone X iOS 16.7.16 (20H392) donor SystemOS cache. This plan collects only
those three donor-side records so a later comparison uses the same requested
install paths on both caches.

The donor is an iPhone X / D22AP reference. Its records are not iPhone 7
hardware evidence and cannot establish iOS 16 compatibility on A10/T8010.

## Exact inputs

Use the already-mounted 20H392 **SystemOS Cryptex** cache, not the OS root
filesystem cache and not the DriverKit cache.

The previously verified APFS-FUSE layout places the selected main cache at:

```text
$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64
```

The outer `root` is the host mountpoint directory; the inner `root` is the
iOS filesystem hierarchy exposed by the APFS-FUSE mount. The 20H392 cache is
split across its main file and companion subcaches. Do not concatenate,
rename, or treat the companion files as separate caches.

Use only this standalone IPSW executable:

```text
/home/hey/ipsw-standalone/ipsw
```

The previously recorded executable version is IPSW 3.1.749,
build commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`. Do not invoke
a bare `ipsw` command; that could resolve to a different installation.

## Read-only host capture

Run this in the Ubuntu environment where the donor SystemOS Cryptex is already
mounted. It reads the cache metadata and writes report files only.

```bash
set -uo pipefail

IPSW="/home/hey/ipsw-standalone/ipsw"
DONOR_CACHE="$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
OUT="$HOME/20H392-gui-framework-loader-results"

echo "===== Standalone IPSW ====="
if [ ! -x "$IPSW" ]; then
  echo "ERROR: standalone IPSW is missing or not executable: $IPSW"
  exit 1
fi

printf 'Executable: %s\n' "$IPSW"
"$IPSW" version
VERSION_STATUS=$?
printf 'Version command exit status: %s\n' "$VERSION_STATUS"
if [ "$VERSION_STATUS" -ne 0 ]; then
  echo "ERROR: could not query standalone IPSW version."
  exit 1
fi

echo
echo "===== Donor SystemOS cache ====="
if [ ! -r "$DONOR_CACHE" ]; then
  echo "ERROR: donor cache main file is not readable:"
  echo "$DONOR_CACHE"
  echo "No permission changes were attempted."
  exit 1
fi
echo "Donor SystemOS cache main file is readable."

echo
echo "===== Output directory ====="
if ! mkdir -p "$OUT"; then
  echo "ERROR: could not create output directory: $OUT"
  exit 1
fi
if [ ! -w "$OUT" ]; then
  echo "ERROR: output directory is not writable: $OUT"
  exit 1
fi
echo "Output directory is writable: $OUT"

: > "$OUT/status.tsv" || {
  echo "ERROR: could not create status.tsv in $OUT"
  exit 1
}

"$IPSW" version > "$OUT/ipsw-version.txt" 2>&1
printf 'Standalone executable: %s\n' "$IPSW" >> "$OUT/ipsw-version.txt"

IMAGES=(
  "/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard"
  "/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard"
  "/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices"
)

for IMAGE in "${IMAGES[@]}"; do
  NAME="$(basename "$IMAGE")"
  echo
  echo "===== $NAME ====="

  if "$IPSW" dyld image "$DONOR_CACHE" "$IMAGE" \
      > "$OUT/$NAME.txt" 2> "$OUT/$NAME.err"; then
    STATUS=0
  else
    STATUS=$?
  fi

  printf '%s\t%s\n' "$IMAGE" "$STATUS" >> "$OUT/status.tsv"
  printf 'Exit status: %s\n' "$STATUS"
  printf 'stdout: %s/%s.txt (%s bytes)\n' "$OUT" "$NAME" "$(wc -c < "$OUT/$NAME.txt")"
  printf 'stderr: %s/%s.err (%s bytes)\n' "$OUT" "$NAME" "$(wc -c < "$OUT/$NAME.err")"

  if [ -s "$OUT/$NAME.err" ]; then
    echo "--- stderr ---"
    cat "$OUT/$NAME.err"
  fi
done

echo
echo "===== Saved results ====="
cat "$OUT/status.tsv"
echo "Reports are in: $OUT"
```

The command queries the selected mounted cache only. It does not extract,
execute, patch, or modify any framework image or cache file. It does not
communicate with the physical iPhone.

## What to preserve

Send the complete `20H392-gui-framework-loader-results` directory, or upload
these files individually:

- `ipsw-version.txt`
- `status.tsv`
- `SpringBoard.txt` and `SpringBoard.err`
- `RunningBoard.txt` and `RunningBoard.err`
- `RunningBoardServices.txt` and `RunningBoardServices.err`

Keep the full stdout files unchanged. A nonzero exit status, missing loader,
or empty `Dependents` block is a finding to record, not a reason to silently
substitute a different image path. Preserve any stderr output.

## Comparison rules

For each requested image, compare the target 19H422 and donor 20H392 records
using the same exact install name. Record separately:

1. IPSW version, query exit status, and stderr state.
2. Printed image path and PrebuiltLoader reference index.
3. Loader flags, VM size, region count, and presence or absence of reported
   `Dependents` and `BindTargets` blocks.
4. Each dependent install name and its printed kind, preserving regular and
   weak-link rows separately.
5. Whether each dependent path appears in that build's cache image list and,
   separately, the corresponding mounted filesystem inventory when evidence
   exists.

Do not compare a PrebuiltLoader reference index with a cache image-list index;
they are distinct identifiers. Do not infer that a missing printed block is
an empty set.

The 19H422 output contains implausible `Sections` offsets and sizes that look
like parsed text bytes rather than valid section metadata. The cause has not
been isolated. Keep those fields excluded from comparisons and do not use
them for file-range or memory-layout conclusions. Apply the same caution to
any similar 20H392 output until independently validated.

## Evidence boundary

These are static PrebuiltLoader/cache metadata observations. They do not prove
that dyld resolves the dependencies at runtime, that symbols or ABIs match,
that signatures or entitlements are acceptable, that a framework launches,
or that any hardware provider attaches. A comparison between an iPhone 7
19H422 cache and an iPhone X 20H392 donor cache is not a controlled hardware-
only comparison: both the device and OS build differ.

The physical iPhone 7 remains on iOS 12.1.4. No restore, update, boot,
partition, security-state, or firmware operation is part of this research.
