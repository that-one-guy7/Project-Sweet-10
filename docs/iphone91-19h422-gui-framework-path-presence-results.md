# iPhone9,1 19H422 GUI framework path-presence results

## Result

The user-run read-only scan checked **18 selected exact GUI-framework install paths** under one supplied target filesystem root, at wrapper depths 0, 1, and 2. **All 18 candidates returned `not-found-under-scanned-roots`.** No candidate produced a regular-file, symlink, or inspection-error result.

This includes both ExtensionFoundation candidates:
- Donor install path: `/System/Library/Frameworks/ExtensionFoundation.framework/ExtensionFoundation`
- Known target cache-inventory alternate: `/System/Library/PrivateFrameworks/ExtensionFoundation.framework/ExtensionFoundation`

The second path was previously represented in the target 19H422 dyld cache image list at image index 1093. Its absence as a standalone file at the checked filesystem paths does not cancel or contradict that separate cache-image-list record.

## Scan identity

| Field | Value |
|---|---|
| Target | iPhone9,1 / D10AP / iOS 15.8.8 / 19H422 |
| Donor reference | iPhone10,3 / D22AP / iOS 16.7.16 / 20H392 |
| Filesystem roots | 1 (`target_root_0`, supplied target mount) |
| Wrapper depths | 0, 1, 2 |
| Candidate count | 18 |
| Result count | 18 `not-found-under-scanned-roots` |
| Candidate-list SHA-256 | `e25a54af687e32e3e6959cf2959a7c637e4a195beae08cfa0eb4c0ecc2d46358` |

The complete structured output is preserved in [`research/iphone91-19h422-gui-framework-path-presence-results.json`](../research/iphone91-19h422-gui-framework-path-presence-results.json).

## Candidate groups

| Group | Candidates | Found at exact checked paths |
|---|---:|---:|
| RunningBoard dependencies | 3 | 0 |
| SpringBoard dependencies | 15 | 0 |
| **Total** | **18** | **0** |

## Interpretation

`not-found-under-scanned-roots` is deliberately narrow. The scanner tested only the 18 supplied absolute paths beneath the one supplied root, plus repeated `root/` wrapper prefixes at depths 0–2. It did not recursively search for framework basenames, inspect other volumes, or search Cryptex/runtime locations. It used component-wise `lstat`, stopped at symlinks, and did not open, hash, parse, or execute framework files.

Therefore this result **does not establish global filesystem absence** for any framework. In particular:
- A dyld cache image-list entry and a standalone filesystem path are separate evidence categories.
- A missing exact path does not establish that an image is absent from a shared cache or another filesystem volume.
- The scan says nothing about dyld resolution, ABI compatibility, framework loading, service startup, IOKit attachment, hardware operation, kernel boot, or SpringBoard readiness.

## Next static-analysis step

The next useful host-side check is a bounded, name-based location inventory for these same 18 binary basenames across explicitly selected target mount roots and any separately mounted system volumes supplied by the user. It should remain read-only, avoid following symlinks, report the searched roots, and preserve the distinction between a found filename and a valid/loadable Mach-O image. Do not infer that a missing item is globally absent when a volume was not included.

M6 remains in progress. M7/SpringBoard has not started. The physical iPhone 7 remains on iOS 12.1.4; no device, firmware, partition, or boot state was accessed or changed.
