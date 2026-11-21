# iPhone9,1 19H422 recursive GUI framework location inventory

## Purpose

The earlier 18-path scan checked only exact install paths and root-wrapper
prefixes. All 18 exact checks returned `not-found-under-scanned-roots`.
This follow-up checks whether the same framework binary names or enclosing
`.framework` bundle directory names occur anywhere beneath one explicitly
selected mounted target filesystem tree.

The search is read-only and does not open, hash, parse, or execute binaries.
It does not interact with the physical iPhone.

## Research basis

Apple's dyld shared-cache documentation describes cache mappings as being
built from dylib segments copied into shared-cache mappings. Consequently,
a framework's source file in a filesystem tree and an image represented in a
dyld shared cache remain distinct forms of evidence. A recursive filename
match is useful for locating candidates, but it is not dyld resolution or
loadability evidence.

The target 19H422 BuildManifest identifies the OS component as
`098-68844-067.dmg` for the iPhone9,1 `d10ap` identities (1 and 3).
This task scans only the already-mounted extracted OS hierarchy. It does not
assume that the iPhone X donor's separate SystemOS Cryptex layout also
exists for the target.

References:
- [Apple dyld shared-cache layout](https://github.com/apple-oss-distributions/dyld/blob/main/doc/CacheLayout.md).
- [Target iPhone9,1 19H422 BuildManifest audit](iphone91-19h422-buildmanifest-audit.md).
- [Earlier exact-path inspection results](iphone91-19h422-gui-framework-path-presence-results.md).

## Search semantics

`tools/inventory_framework_locations.py` loads the existing candidate JSON
and searches these names for every candidate:

1. The final executable basename (for example, `ActivityKit`).
2. The enclosing bundle directory basename (for example,
   `ActivityKit.framework`).

The scanner searches recursively beneath one supplied root. It uses
`os.walk(followlinks=False)`, explicitly removes directory symlinks from
the traversal list, and uses `lstat` to classify matching entries. It
records regular files, directories, symlinks and other file types. It also
records directory-walk and matching-entry stat errors.

A match is associated with every candidate sharing that basename. This is
intentional: for example, the two ExtensionFoundation candidate install paths
share the same binary and bundle basenames. A basename match does not prove
which install path is canonical.

### Result statuses

- `match-found`: at least one binary or bundle basename match was found
  somewhere under the supplied root.
- `no-match-in-complete-scan`: no match was found and the scan reported no
  walk or matching-entry stat errors.
- `no-match-scan-incomplete`: no match was found, but the scanner encountered
  errors, so the absence result is incomplete.

The report also includes `scan_status` (`complete` or `incomplete`),
directories and entries visited, all matching paths, and every captured
walk/stat error. Even a complete scan covers only the supplied root; it does
not cover other images, volumes, Cryptexes, APFS snapshots or the dyld cache.

## Run in Ubuntu

Run from the Project-Sweet-10 repository root after the PR is merged.
The existing mount layout places the extracted target filesystem below the
child directory named `root`, so use that directory as the recursive root:

```bash
set -euo pipefail

TARGET_OS_ROOT="$HOME/19H422-full-fs-mount/root"
OUT="$HOME/sweet10-gui-framework-location-inventory"
mkdir -p "$OUT"

python3 tools/inventory_framework_locations.py \
  --paths-json research/iphone91-19h422-gui-framework-path-candidates.json \
  --target-root "$TARGET_OS_ROOT" \
  > "$OUT/19H422-gui-framework-location-inventory.json"

echo "Report: $OUT/19H422-gui-framework-location-inventory.json"
```

No IPSW command or device connection is needed. Do not use `sudo`, chmod or
chown. If the scan reports permission/stat errors, preserve them in the output;
do not change permissions as a guess.

Upload the resulting JSON report for review. The report should be committed
only after its target-root provenance, candidate-name matches, and error list
have been checked.

## Evidence boundary

This scan searches names only. It does not establish that a match is a valid
Mach-O image, has a usable signature, matches the donor ABI, is in a dyld
cache, resolves from the recorded install name, or can be loaded by a process.
It does not establish service startup, IOKit attachment, hardware operation,
kernel boot, or SpringBoard readiness.

The scan does not follow symbolic links, and a scan error prevents unmatched
candidates from being classified as absent even within the supplied root.
The physical iPhone 7 remains on iOS 12.1.4. M6 remains in progress; M7 has
not started.
