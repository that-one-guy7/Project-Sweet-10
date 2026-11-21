# iPhone9,1 19H422 SpringBoard / RunningBoard framework loader capture plan

## Purpose

The target iPhone 7 19H422 cache image-list cross-reference confirms that the
three GUI-chain executables' 44 unique regular direct dependency paths all
appear in the target `dylibs` image array. The next bounded static step is to
inspect the target PrebuiltLoaderSet records for three higher-level frameworks:

- `/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard`
- `/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard`
- `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices`

Their exact target cache image-list records are:

| Framework | Image-list index | Version | UUID |
|---|---:|---|---|
| SpringBoard | 454 | `4251.53.0.0.0` | `245B5F25-7DE1-329C-9107-87B37883CFB9` |
| RunningBoard | 553 | `618.100.42.0.0` | `68246786-1E83-3892-907F-123EE1F09C68` |
| RunningBoardServices | 62 | `618.100.42.0.0` | `616B8ECB-90ED-38C5-9988-24AD07AE0CE9` |

The image-list index is not a PrebuiltLoader reference index. Keep these
identities separate when recording query output.

## Host-side query

**Use this exact standalone executable only:**

`/home/hey/ipsw-standalone/ipsw`

Do not call `ipsw` by its short name and do not use the Snap package.
The script below invokes the absolute path directly, so `PATH` cannot
select a different executable. The physical phone is not involved.

The target cache is:

`$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`

Run this from Ubuntu. It checks that the standalone executable and target
cache are accessible, verifies that the output directory is writable, records
the exact executable version, saves each query's stdout and stderr, and
prints each exit status to the terminal.

```bash
set -uo pipefail

IPSW="/home/hey/ipsw-standalone/ipsw"
TARGET_CACHE="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
OUT="$HOME/19H422-gui-framework-loader-results"

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
echo "===== Target cache ====="
if [ ! -r "$TARGET_CACHE" ]; then
  echo "ERROR: target cache is not readable by the current Ubuntu user:"
  echo "$TARGET_CACHE"
  echo "No permission changes were attempted."
  exit 1
fi
echo "Target cache is readable."

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

for IMAGE in \
  /System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard \
  /System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard \
  /System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices
do
  NAME="$(basename "$IMAGE")"
  echo
  echo "===== $NAME ====="

  if "$IPSW" dyld image "$TARGET_CACHE" "$IMAGE" \
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

Do not execute or extract these images. This queries cache metadata only and
writes text reports under your home directory. The standalone executable is
called directly for every IPSW command; no Snap executable is used.

## What to retain

For each query preserve the exact requested image path, ipsw version,
exit status, stderr, PrebuiltLoader reference index, flags, VM size,
region count, every `Dependents` row in source order and raw kind, and
every `BindTargets` row separately. Do not infer an empty BindTargets list
when no section is printed.

## Comparison rules

Compare the three new records with the previously captured donor 20H392
loader records when available. Keep the following evidence categories
separate:

1. Executable direct Mach-O load commands.
2. Framework PrebuiltLoaderSet dependency rows.
3. The target cache `dylibs` image-list entries.
4. Standalone mounted filesystem paths.
5. Runtime behavior (not part of this audit).

Preserve regular, weak-link, re-export, upward, and unknown dependency kinds
as distinct edge types. A framework appearing in the image list does not
prove dyld resolves it for a process or that its own dependencies are
satisfied.

## Evidence boundary

This is host-side static metadata only. It does not establish ABI
compatibility, code-signing validity, runtime dependency resolution,
launchd registration, process launch, IOKit provider attachment, hardware
operation, kernel compatibility, or SpringBoard readiness. The target cache
belongs to stock iOS 15.8.8 build 19H422 on iPhone9,1; it is not an iOS 16
target build.

The physical iPhone 7 remains on iOS 12.1.4. No device or boot operation is
part of this plan.
