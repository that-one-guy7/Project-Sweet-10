# iPhone9,1 19H422 GUI framework path-presence inspection plan

## Purpose

The 20H392 / 19H422 PrebuiltLoader comparison identifies several donor-side
GUI framework paths that have no same-basename record in the target cache
image-list inventory. Cache-list absence is not filesystem absence. This
bounded check asks whether the exact selected install paths (or one known
ExtensionFoundation alternate path) exist in the already-mounted 19H422
filesystem.

It checks 18 explicit candidate paths. It does not recursively search by
basename, open framework files, inspect Mach-O contents, or interact with the
physical iPhone.

## Inputs

- Target filesystem: iPhone9,1 / D10AP / iOS 15.8.8 build 19H422.
- Mount root: `$HOME/19H422-full-fs-mount`.
- Known mount layout: the extracted iOS hierarchy is below a child
  `root/` directory, so the earlier cache path is
  `$HOME/19H422-full-fs-mount/root/System/Library/Caches/...`.
- Candidate list:
  [`research/iphone91-19h422-gui-framework-path-candidates.json`](../research/iphone91-19h422-gui-framework-path-candidates.json).

The candidate list contains the exact donor ExtensionFoundation
`/System/Library/Frameworks` path and the target cache's known
`/System/Library/PrivateFrameworks` alternate path as separate records.
It also includes PrivacyDisclosureCore and selected modern SpringBoard UI
framework paths.

## Method

`tools/inspect_framework_paths.py` checks each exact candidate path under
the supplied target root at wrapper depths 0, 1, and 2 by default. Every
component is queried with `lstat`; the scanner stops if any component is a
symlink. It records regular files, directories, symlinks, non-directory
components, permission/stat errors, and missing exact paths distinctly.

The tool reads the candidate JSON and filesystem metadata only. It does not
open, hash, parse, or execute any framework binary. It does not recursively
walk the filesystem, follow symlinks, change permissions, or modify the
mounted source tree. Output is JSON written by shell redirection to a
separate directory under the user's home folder.

Interpretation:
- `regular-file-found`: a regular filesystem object exists at one checked
  exact path. This does not establish that it is a Mach-O image or loadable.
- `symlink-present-unresolved`: a path component is a symlink; its target
  was deliberately not followed.
- `inspection-incomplete`: a permission, stat, or non-directory error
  prevented a complete check.
- `not-found-under-scanned-roots`: no exact candidate path was found at
  wrapper depths 0–2 beneath the supplied root. It is not a global absence
  claim and does not cover other paths or volumes.

The two ExtensionFoundation records are intentionally separate. A regular
file at the PrivateFrameworks alternate path does not prove that the donor's
Frameworks install name will resolve to it.

## Run in Ubuntu

From the Project-Sweet-10 repository root:

```bash
set -euo pipefail

OUT="$HOME/sweet10-gui-framework-path-presence"
mkdir -p "$OUT"

python3 tools/inspect_framework_paths.py \
  --paths-json research/iphone91-19h422-gui-framework-path-candidates.json \
  --target-root "$HOME/19H422-full-fs-mount" \
  --wrapper-depth 2 \
  > "$OUT/19H422-gui-framework-path-presence.json"

echo "Report: $OUT/19H422-gui-framework-path-presence.json"
```

No IPSW executable is needed for this filesystem metadata check. Do not use
`sudo`, chmod, or chown. If access is denied, retain the error status and
inspect the exact reported path separately; do not change permissions as a
guess.

Upload the resulting JSON file for review. The result should be committed
only after its candidate statuses and input hash have been reviewed.

## Validation

The synthetic test module covers exact file presence, wrapper depth, the
ExtensionFoundation exact-path versus alternate-path distinction, symlink
handling, missing paths, non-directory components, candidate-schema and
duplicate-ID validation, safe absolute paths, wrapper-depth bounds, root
validation, and output preservation. The source-check workflow runs the full
host-side unittest suite.

## Evidence boundary

This is static filesystem metadata from the supplied 19H422 mount only. It
does not establish whether a cache image can be resolved by dyld, whether a
framework's ABI or signature is compatible, whether a process can launch,
whether an IOKit provider attaches, or whether display/input hardware works.
The target cache is stock iOS 15.8.8, not the intended 20H392 userland.
M6 remains in progress; M7/SpringBoard has not started. The physical iPhone 7
remains on iOS 12.1.4; no device, firmware, partition, or boot state is
accessed or changed.
