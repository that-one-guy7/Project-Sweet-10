# iPhone9,1 / 19H422 BackBoard framework loader comparison plan

## Purpose and status

The repository has complete donor-side PrebuiltLoaderSet dependency records for
four frameworks directly named by the iPhone X 20H392 `backboardd` loader:

- `BackBoardHIDEventFoundation`
- `BackBoardHIDEventProcessors`
- `BackBoardServices`
- `IOMobileFramebuffer`

The planned collection of the same four records from the iPhone 7 / D10AP /
iOS 15.8.8 (19H422) target-reference shared cache has now been completed.
The target records and exact donor comparison are documented in
[the target BackBoard loader results](iphone91-19h422-backboard-loader-results.md)
and the donor baseline in
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

All four requested target install names returned loader records in the
19H422 cache. The records and their dependency rows have been compared to
the corresponding 20H392 donor records. The resulting differences are
limited to a donor-only StudyLog dependency edge in each of the two HID
frameworks; see the result document for exact rows and status caveats.

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


## Troubleshooting: first query attempt returned only stderr

The first user-reported run produced the following file sizes:

- Each of the four framework `.txt` stdout files: **0 bytes**.
- Each of the four framework `.err` stderr files: **128 bytes**.
- `combined-loader-report.txt`: approximately **1.2 KiB**.

This is **not a successful loader inventory**. Empty stdout means no loader
record was captured; the stderr files indicate that ipsw reported an error.
The file sizes alone do not identify the cause, so do not change the cache
path, substitute another image, or assume the target lacks these frameworks.

The next step is to display the exact combined report already created by the
collection command. Run this one command in Ubuntu:

```sh
cat "$HOME/19H422-backboard-loader-results/combined-loader-report.txt"
```

Paste the complete output into the Project Sweet-10 issue/chat or attach the
`combined-loader-report.txt` file. It should contain each requested image
path, exit status, stdout section, and exact stderr text. Use that evidence
to diagnose the failure before rerunning any image query.

If the file is not found, report the exact output of:

```sh
ls -lh "$HOME/19H422-backboard-loader-results"
```

Do not treat zero-byte stdout files as evidence that the frameworks are
missing from the target cache. The command may have failed before image
lookup, and the exact stderr text is required to distinguish the cases.

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


## Troubleshooting: confirmed host permission failure (2026-11-20)

The supplied combined report resolves the earlier unknown error. All four
queries exited with status 1 and printed the same error:

`open /home/hey/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64: permission denied`

This is a host filesystem access failure while opening the shared-cache file.
It is not a loader result and does not show that any requested framework is
missing. No target dependency rows were collected. The repeated identical
error across all four requests points to the shared input path, before
framework-specific lookup.

### Next read-only diagnosis

Do not rerun the four queries yet. In Ubuntu, run:

```sh
TARGET_CACHE="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
printf '%s\\n' '--- path permissions ---'
namei -l "$TARGET_CACHE"
printf '%s\\n' '--- cache file metadata ---'
stat "$TARGET_CACHE"
printf '%s\\n' '--- current-user readability ---'
if test -r "$TARGET_CACHE"; then
  echo "readable by current user"
else
  echo "NOT readable by current user"
fi
```

Share the complete output. These commands only inspect path and file
metadata; they do not change permissions, remount the image, or access the
phone. Use the output to identify which directory or file denies access
before choosing any correction. Do not apply recursive permission changes
or change ownership as a guess.

The target loader audit remains blocked. M6 remains in progress; M7 has not
started. The physical iPhone 7 remains on iOS 12.1.4.


## First successful target query (2026-11-20)

The user has now run the first target query successfully using the standalone
Linux IPSW 3.1.749 executable extracted from the official x86_64 Debian
package. Package SHA-256:
`333cab58451330f0080c3c2b7bec3d9e6f4be588b27f6213a5233dd08821d071`.
The target `BackBoardServices` query exited 0 with empty stderr and returned
a prebuilt in-cache dylib record, reference index 18, VM size
`0x865a8000`, five regions, 12 regular dependencies, and one re-export.
The exact dependency names and kinds match the recorded 20H392 donor
BackBoardServices record in printed order. See
[the target loader result](iphone91-19h422-backboard-loader-results.md).

This resolves the earlier Snap-specific access problem for this workflow:
the non-Snap executable successfully parsed the same target cache. The old
permission-denied report remains historical evidence of the Snap attempt,
not the current audit status. Do not repeat the Snap diagnosis.

At the time this initial success note was added, three target records
remained to be collected. That interim status was superseded by the
"Completed target collection and donor comparison" section below.


## Completed target collection and donor comparison (2026-11-20)

The four requested 19H422 loader records have now been collected with the
standalone Linux IPSW 3.1.749 executable and compared against the existing
20H392 donor records. Three supplied command results explicitly show exit
status 0 and empty stderr; the BackBoardHIDEventFoundation output includes
a valid loader record and an empty stderr section, but its explicit status
line was not present in the excerpt supplied for documentation. No status
is invented for that one record.

Target totals: 33 regular dependency rows, one re-export, and zero
weak-link rows. Donor totals: 35 regular rows, one re-export, and zero
weak-link rows. Both sides have the same 12 regular plus one re-export
BackBoardServices record and the same four IOMobileFramebuffer regular
dependencies. The target HID framework records each omit the donor's
StudyLog dependency. There are no target-only dependency rows in this
four-image comparison. The difference is not attributed to hardware,
because the target and donor use different iOS releases and device models.

The Snap package's permission-denied error is now historical troubleshooting
context only: the standalone executable successfully opened and parsed the
same target cache. There is no need to repeat Snap access diagnostics.

This bounded four-image collection and comparison is complete. The broader
M6 audit remains in progress; M7/SpringBoard has not started. Static loader
metadata does not demonstrate runtime framework loading, API ABI
compatibility, IOKit attachment, HID event delivery, display operation, or
iPhone9,1 compatibility. The phone remains on iOS 12.1.4.
