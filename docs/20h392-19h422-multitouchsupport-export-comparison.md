# 20H392 donor / 19H422 target MultitouchSupport export comparison

## Scope and image identity

This report records a read-only comparison of the `Dyld Exports` output
for the same cached image path:

```text
/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport
```

| Field | Target 19H422 | Donor 20H392 |
|---|---|---|
| Device | iPhone 7, `iPhone9,1` / D10AP / A10-T8010 | iPhone X, `iPhone10,3` / D22AP / A11-T8015 |
| iOS build | 15.8.8 / `19H422` | 16.7.16 / `20H392` |
| Image-list index | 1249 | 1648 |
| Image version | `5100.27.0.0.0` | `6140.3.0.0.0` |
| Mach-O UUID | `0EAF98B3-8D31-3A90-A578-1787797B9467` | `1B6ABB86-B8A9-3941-A66A-EC9715F6B034` |

The physical iPhone 7 remains on iOS 12.1.4. These results come from
host-side inspection of existing IPSW shared caches. No device, firmware,
partition, boot, or restore state was accessed or changed.

## Observed export surface

The supplied output contains a target block followed by an explicitly
labelled `DONOR EXPORTS` block. The target block's own heading and the
two parser exit-code lines were not included in the pasted excerpt. The
target/donor interpretation below follows the order of the documented
command, which prints the target first and donor second.

A line-by-line comparison of the supplied symbol names shows substantial
overlap. The seven additional names visible in the donor 20H392 list, and
not present in the supplied target 19H422 list, are:

| Donor-only export name | Printed kind |
|---|---|
| `_MTDeviceGetMaxHoverHeightValue` | `regular` |
| `_MTDeviceGetMultipleFirmwaresConfig` | `regular` |
| `_MTDeviceSetBinaryFiltersProperty` | `regular` |
| `_MTDeviceShouldSkipFaceDetectionMode` | `regular` |
| `_MTDeviceUpdateUILockState` | `regular` |
| `_OBJC_CLASS_$_MTAHTSupport` | `regular` |
| `_OBJC_METACLASS_$_MTAHTSupport` | `regular` |

All rows shown in both pasted blocks are marked `(regular)`. No weak or
re-export rows were visible in the supplied sections. I did not identify
a target-only name in the pasted comparison.

**Count qualification:** exact total counts, unique-name set differences,
duplicate rows, and parser exit statuses have not yet been independently
verified from the two saved complete log files. The seven donor-only
names above are preliminary observations from the user-pasted output.
Run the automated comparison in the audit plan before treating the
counts or the absence of target-only names as final.

## Address interpretation

The target output uses addresses in a different range from the donor
output. The two shared caches have different image load addresses and
cache layouts; these printed addresses must be retained only as
cache-specific metadata. Address differences do not show that corresponding
functions have different implementations or that either image is
compatible with the other.

## Interpretation

The target 19H422 `MultitouchSupport` image exposes a broad set of
multitouch-device, contact, path, callback, recording/playback, actuator,
and Zephyr-related symbol names that substantially overlaps the donor
20H392 list. The donor additionally exports the five listed
`_MTDevice...` names and an Objective-C class/metaclass pair for
`MTAHTSupport`.

The extra donor exports identify a difference in the two images'
visible exported-name surfaces. Their names alone do not establish
which hardware features they implement, whether equivalent functionality
exists elsewhere in the target OS, or whether they are required for
touch input on the iPhone 7.

The different image versions and UUIDs were already recorded in the
cache inventory audits. This export comparison does not establish
matching implementations, calling conventions, structure layouts, ABI
compatibility, code-signature validity, runtime dependency resolution,
plugin loading, IOKit provider attachment, touch-event delivery, or
SpringBoard stability.

## Next verification

Use the saved logs `$HOME/19H422-MultitouchSupport-exports.txt` and
`$HOME/20H392-MultitouchSupport-exports.txt` with the exact-set parser
in the [export audit plan](20h392-19h422-multitouchsupport-export-audit-plan.md).
That will verify exact counts, common names, donor-only names, target-only
names, duplicate records, and per-name export-kind differences.

No cache file, binary, filesystem image, firmware file, or device state
is modified or committed by this report.
