# iPhone9,1 / 19H422 BackBoard framework loader comparison plan

## Purpose and status

The repository has complete donor-side PrebuiltLoaderSet dependency records for
four frameworks directly named by the iPhone X 20H392 `backboardd` loader:

- `BackBoardHIDEventFoundation`
- `BackBoardHIDEventProcessors`
- `BackBoardServices`
- `IOMobileFramebuffer`

The next bounded M6 step is to collect the same four records from the
already-inventoried iPhone 7 / D10AP / iOS 15.8.8 (19H422) target-reference
shared cache. The donor baseline and its dependency rows are documented in
[the 20H392 BackBoard results](20h392-backboard-framework-dependency-results.md).

This target reference is iOS 15.8.8, not the intended iOS 16 userland.
Differences may reflect the different iOS releases as well as device/board
differences. Do not attribute any difference to T8010 hardware without
separate evidence.

The physical iPhone 7 remains on iOS 12.1.4. This is a host-side,
read-only cache query. It does not connect to, boot, modify, or install
anything on the phone.

## Why these four images

The donor `backboardd` loader lists these four install names as direct
dependents. The four donor loader records have already been collected:
BackBoardHIDEventFoundation has 10 regular dependency rows;
BackBoardHIDEventProcessors has 9;
BackBoardServices has 12 regular rows plus one re-export;
IOMobileFramebuffer has 4 regular rows. No weak-link rows appeared in those
four donor blocks.

The target 19H422 cache image inventory already lists BackBoardServices,
BackBoardHIDEventFoundation, and BackBoardHIDEventProcessors. The target
image-list record for IOMobileFramebuffer has not yet been recorded in this
specific crosswalk. The loader query must report a missing/unresolved path
as-is; do not silently substitute a different image or a donor record.

## Input cache

Use the target shared cache already identified in the project:

```text
$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64
```

The split-cache companion files are in the same directory. Do not rename,
concatenate, or copy the cache pieces. The previously recorded target cache
image inventory was generated with ipsw 3.1.749.

Before running the queries, verify the file is readable and record the
installed ipsw version:

```sh
TARGET_CACHE="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
test -r "$TARGET_CACHE" && echo "target cache readable"
ipsw version
```

If the main cache is not readable, stop and report the exact error. Do not
remount or modify an IPSW as part of this plan.

## Read-only collection command

Run this from Ubuntu. It writes only text reports under your home directory.
Each requested image gets a separate stdout and stderr file; the combined
report includes the exact requested path, exit status, stdout, and stderr.

```sh
TARGET_CACHE="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
OUT="$HOME/19H422-backboard-loader-results"
mkdir -p "$OUT"
: > "$OUT/combined-loader-report.txt"

for IMAGE in \
  /System/Library/PrivateFrameworks/BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation \
  /System/Library/PrivateFrameworks/BackBoardHIDEventProcessors.framework/BackBoardHIDEventProcessors \
  /System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices \
  /System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer
do
  NAME="$(basename "$IMAGE")"

  if ipsw dyld image "$TARGET_CACHE" "$IMAGE" \
      > "$OUT/$NAME.txt" 2> "$OUT/$NAME.err"; then
    STATUS=0
  else
    STATUS=$?
  fi

  {
    printf '\n===== REQUESTED IMAGE: %s =====\n' "$IMAGE"
    printf 'EXIT STATUS: %s\n' "$STATUS"
    printf '%s\n' '--- STDOUT ---'
    cat "$OUT/$NAME.txt"
    printf '\n%s\n' '--- STDERR ---'
    cat "$OUT/$NAME.err"
    printf '\n'
  } >> "$OUT/combined-loader-report.txt"
done

ls -lh "$OUT"
```

The command form `ipsw dyld image <DSC> <IMAGE>` is documented by the
[ipsw dyld guide](https://blacktop.github.io/ipsw/docs/guides/dyld/).
Keep the installed version with the report. The project previously used
ipsw 3.1.749; do not mix results from different versions without recording
the difference.

## What to preserve

For every image that returns a loader record, record:

1. Exact requested path and exact path printed by ipsw.
2. Command exit status and stderr.
3. PrebuiltLoaderSet version, loader flags, info flags, and VM size if shown.
4. Every `Dependents` row in printed order, retaining its raw kind exactly
   (`regular`, `weak-link`, re-export, upward, or any unknown display).
5. Every `BindTargets` row separately from dependency edges.
6. Whether the query returns a PrebuiltLoaderSet record, a legacy image-array
   record, no record, or an error.

Do not equate PrebuiltLoader reference indexes with cache image-list indexes.
The indexes belong to different tables. Obtain source version and Mach-O UUID
from the cache image-list inventory as a separate evidence category, not by
guessing from a loader reference index.

## Comparison method

Compare each target record with the corresponding donor record in
[20H392 BackBoard dependency results](20h392-backboard-framework-dependency-results.md):

- Compare exact dependency install names and raw dependency kinds.
- Keep weak-link, re-export, and any unknown kind separate from regular
  dependency rows.
- Preserve row order in the raw report; create a separate deduplicated graph
  only after the raw record is documented.
- Compare `BindTargets` independently; a bind target does not establish
  which clients use an API or prove a hardware provider.
- If a target dependency path is not found, distinguish a failed lookup from
  absence in the complete target system. The shared cache image list and
  filesystem volumes are separate evidence sources.
- If IOMobileFramebuffer is absent from the target cache, record that finding
  with the exact command output and image-list cross-check. Do not assume it
  exists because the donor has it.

The previous donor and target reports contain suspicious decoded
Swift/Objective-C `Sections` offsets and sizes. Exclude those fields from
this audit. Do not use them for file-range calculations, memory layout, or
binary compatibility claims. Preserve the raw output locally if later parser
validation is needed.

## Reporting and privacy

Keep full raw output files on the host. Do not commit complete proprietary
loader records, shared-cache files, IPSW/DMG files, personal identifiers, or
device-specific values. Once supplied, summarize only exact image paths,
parser version/status, counts and kinds of dependency rows, relevant
provider-independent differences, and image-list identity values needed for
the comparison.

## Acceptance criteria

This bounded collection is complete when:

1. All four exact target paths have a recorded query result, including
   explicit failures or missing records.
2. The ipsw version, exit status, and stderr state are recorded per query.
3. Every returned dependency row and bind-target row is preserved with its
   printed kind.
4. The target result is compared against the existing four donor records.
5. Cache image-list identity is kept separate from loader-reference indexes.
6. The report explicitly states that static cache metadata does not prove
   runtime loading, IOKit attachment, HID event delivery, display operation,
   or iPhone9,1 compatibility.

This plan advances M6 target-side userland evidence only. It does not close
readiness gate G9, establish an iOS 16 launchd configuration, or show that
SpringBoard can start. M6 remains in progress; M7 has not started.
