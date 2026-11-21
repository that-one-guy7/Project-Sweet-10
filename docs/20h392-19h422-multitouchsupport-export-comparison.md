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

The exact-set parser was run against the saved target and donor logs.
The supplied result shows the parser's set-difference and metadata summary.
The output pasted into the conversation begins at the `Target-only names`
section, so its earlier row-count, unique-name, and duplicate-name summary
lines are not available here.

The parser printed an empty `Target-only names` section. It printed the
following seven `Donor-only names`, confirming the preliminary list from
the earlier pasted exports:

| Donor-only export name | Printed kind |
|---|---|
| `_MTDeviceGetMaxHoverHeightValue` | `regular` |
| `_MTDeviceGetMultipleFirmwaresConfig` | `regular` |
| `_MTDeviceSetBinaryFiltersProperty` | `regular` |
| `_MTDeviceShouldSkipFaceDetectionMode` | `regular` |
| `_MTDeviceUpdateUILockState` | `regular` |
| `_OBJC_CLASS_$_MTAHTSupport` | `regular` |
| `_OBJC_METACLASS_$_MTAHTSupport` | `regular` |

All seven donor-only rows are printed as `regular`. The parser printed
no entries under `Names with differing printed kinds`, so it reported no
kind-set differences for the common names. It also printed
`Common names with different first printed addresses: 277`. These are
cache-specific address differences, not a symbol compatibility result.

**Count qualification:** the pasted parser output does not include its
earlier row-count, unique-name, and duplicate-name summary lines, so those
totals are not recorded here. The set-difference result itself is explicit:
no target-only names and seven donor-only names.

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
and Zephyr-related symbol names that overlaps the donor 20H392 list. The
exact-set parser confirms that the target has no target-only export names
relative to this donor comparison, while the donor has the seven listed
additional names: five `_MTDevice...` names and an Objective-C
class/metaclass pair for `MTAHTSupport`. The parser reported no differing
printed kinds among common names.

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

## Remaining record detail

The output excerpt supplied for this update starts after the script's
row-count, unique-name, and duplicate-name summary. Those numeric totals
remain unrecorded. The complete command output can be retained with the
project notes if those totals are needed for a later quantitative report.
The set differences and common-name kind comparison are already recorded
above.

No cache file, binary, filesystem image, firmware file, or device state
is modified or committed by this report.
