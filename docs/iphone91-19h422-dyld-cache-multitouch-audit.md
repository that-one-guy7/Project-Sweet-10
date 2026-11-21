# iPhone9,1 19H422 dyld shared-cache multitouch image audit

## Purpose and evidence boundary

This report records the user's host-side inspection of the split dyld shared
cache included with the iPhone 7 `iPhone9,1` / D10AP / A10-T8010
iOS 15.8.8 (19H422) filesystem DMG. It focuses on the multitouch plugin
image that was not found as a standalone file in the mounted filesystem.

The physical iPhone remains on iOS 12.1.4. The 19H422 IPSW was mounted
read-only on the host; no firmware, partition, activation, security, or boot
state on the phone was accessed or changed. This audit establishes cache
image-list metadata, not runtime loading or hardware operation.

## Cache files located

The user searched:

```text
/home/hey/19H422-full-fs-mount/root/System/Library/Caches
```

The command reported these seven files under
`com.apple.dyld`:

| File | Bytes |
|---|---:|
| `dyld_shared_cache_arm64` | 541,999,104 |
| `dyld_shared_cache_arm64.1` | 541,442,048 |
| `dyld_shared_cache_arm64.2` | 542,294,016 |
| `dyld_shared_cache_arm64.3` | 163,840,000 |
| `dyld_shared_cache_arm64.4` | 250,150,912 |
| `dyld_shared_cache_arm64.5` | 211,075,072 |
| `dyld_shared_cache_arm64.symbols` | 489,406,464 |

These are the paths returned by the user's filename search, not a claim
that no other dyld companion files exist.

The selected main cache path was:

```text
/home/hey/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64
```

The user ran `ipsw dyld info --dylibs --json` against this cache and saved
the output to `$HOME/19H422-dyld-images.json`. The terminal reported an
output size of 132,175,259 bytes. The user then supplied `log.txt`, which
contains the relevant indexed image records.

## Multitouch plugin image

The uploaded cache image inventory contains this exact record:

| Field | Observed value |
|---|---|
| Image index | `1948` |
| Image path | `/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID` |
| Version | `5100.27.0.0.0` |
| Mach-O UUID reported by the cache inventory | `304953E6-6B67-3CF1-B7CA-E011978210DE` |
| Cache load-address field | `7982772224` |

The cache image path and version are consistent with the separately
extracted 19H422 `MultitouchHID.plugin/Info.plist`, which declares
`CFBundleExecutable=MultitouchHID` and bundle version `5100.27`.

This resolves the apparent filesystem-search contradiction: no standalone
file or symlink named `MultitouchHID*` was returned from the complete
mounted 19H422 filesystem DMG, but the dyld shared-cache image inventory
does list the plugin image under its bundle path. Therefore the plugin
code is represented in the shared cache, even though it was not present
as a separate file in the mounted filesystem tree.

The cache record supplies an image path, version, UUID, and load-address
field. It does not by itself extract the Mach-O bytes, validate the code
signature, prove that the plugin is loaded at runtime, or prove that it
can be used with a different kernel or board.

## Related target cache image records

The same uploaded image inventory contains these relevant neighboring
userland image records:

| Image index | Image path suffix | Version | UUID |
|---:|---|---|---|
| 19 | `BackBoardServices.framework/BackBoardServices` | `478.19.0.0.0` | `35EE3FFB-EB35-38F4-ABFF-D695B8E3FB9F` |
| 454 | `SpringBoard.framework/SpringBoard` | `4251.53.0.0.0` | `245B5F25-7DE1-329C-9107-87B37883CFB9` |
| 588 | `BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation` | `478.19.0.0.0` | `A99AD801-5B39-347B-AAED-590362F01048` |
| 934 | `BackBoardHIDEventProcessors.framework/BackBoardHIDEventProcessors` | `478.19.0.0.0` | `8E09BC84-3783-33FF-9674-57ECB993FF76` |
| 1249 | `MultitouchSupport.framework/MultitouchSupport` | `5100.27.0.0.0` | `0EAF98B3-8D31-3A90-A578-1787797B9467` |
| 1948 | `AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID` | `5100.27.0.0.0` | `304953E6-6B67-3CF1-B7CA-E011978210DE` |
| 1950 | `IOHIDFamily.kext/PlugIns/IOHIDLib.plugin/IOHIDLib` | `1787.241.1.0.0` | `7E4B06D9-8D41-3F9C-8C37-9F06C9CDC931` |
| 2067 | `AppleHIDTransportSupport.framework/AppleHIDTransportSupport` | `5100.32.0.0.0` | `3175AEDB-1366-3690-9A3C-A549193CC86D` |
| 2221 | `MultitouchSessionFilterSupport.framework/MultitouchSessionFilterSupport` | `5100.27.0.0.0` | `C903E3D2-4FB6-3440-938B-450E0059FD0C` |

These are dyld cache image-list records. The names and versions suggest
related touch/HID and GUI userland components are represented in the target
cache, but they do not establish their dependency edges or that their
corresponding kernel providers attach successfully.

## Interpretation

The evidence now supports the following separate statements:

1. The 19H422 filesystem DMG contains a split dyld shared cache.
2. A full filesystem search did not return a standalone
   `MultitouchHID*` file or symlink.
3. The target dyld image inventory nevertheless lists the
   `MultitouchHID.plugin/MultitouchHID` image, version `5100.27.0.0.0`,
   with UUID `304953E6-6B67-3CF1-B7CA-E011978210DE`.
4. The same cache inventory includes `MultitouchSupport`,
   `MultitouchSessionFilterSupport`, `AppleHIDTransportSupport`,
   BackBoard HID frameworks, and SpringBoard-related images.

This is stronger than plist-only evidence because the shared-cache inventory
identifies a compiled image record. It is still not runtime evidence:
IOKit matching, provider attachment, plugin factory execution, HID event
delivery, and SpringBoard behavior remain untested.

## Next bounded host-side comparison

The donor comparison is now complete at the cache image-record level.
The 20H392 donor record is image-list index `2557`, version
`6140.3.0.0.0`, UUID
`78E1FB55-113A-3500-9D2D-1D8E282BED45`; the 19H422 target record above
is index `1948`, version `5100.27.0.0.0`, UUID
`304953E6-6B67-3CF1-B7CA-E011978210DE`. Their build identifiers differ;
this is not a byte-level comparison or compatibility verdict.

The next host-side task is to inspect the target-native 19H422 loader/image
record for the same full install path, including its dependency list if the
cache format and parser expose one. The read-only command and the
format-dependent output interpretation are documented in
[the target loader audit plan](iphone91-19h422-target-multitouch-loader-audit-plan.md).

No executable is to be copied to the device. No device, firmware, partition,
activation, security, or boot state was accessed or changed. No proprietary
binary, shared-cache file, or filesystem image is committed to this repository.


## Target-native PrebuiltLoaderSet metadata

The user ran `ipsw dyld image` for the exact
`MultitouchHID.plugin/MultitouchHID` path against the mounted 19H422
target cache. The command exited with status `0` and returned a
PrebuiltLoaderSet record with VM Size `0x2e9f4000`, loader reference
`index: 1947`, flags
`prebuilt|in-cache-dylib|objc|never-unload`, Info flags
`initializers|regions=5`, and exports trie offset `0x025fee90`,
size `0xf0d0`. It reported five regions and 13 dependencies (ten regular,
three weak-link). The loader reference index is distinct from the target
cache image-list index `1948`.

The target loader record has no printed UUID or source version. Those values
remain grounded in the target JSON cache image inventory already recorded
above: image-list index `1948`, version `5100.27.0.0.0`, UUID
`304953E6-6B67-3CF1-B7CA-E011978210DE`.

The target's loader dependency list is compared line by line with the
20H392 donor in
[the target/donor loader comparison](20h392-19h422-multitouch-loader-comparison.md).
The comparison is static metadata only. It does not verify dependency
resolution at runtime, plugin loading, IOKit attachment, or touch input.
The displayed section-offset rows from the command are excluded because
they contain implausibly large decoded values.


## Selected MultitouchHID dependency image records

A follow-up read-only search of the target JSON image inventory
`$HOME/19H422-dyld-images.json` found the selected loader dependency
images at these image-list records:

| Image | Index | Version | UUID |
|---|---:|---|---|
| SymptomDiagnosticReporter | 1455 | `174.140.2.0.0` | `ED77A600-C0BE-3240-9693-BF5238095816` |
| WirelessDiagnostics | 6 | `954.1.0.0.0` | `0811A81D-68D5-3FFF-AC31-635D0FE0D732` |
| CoreAccessories | 343 | `672.140.4.0.0` | `7C035F3B-B050-3B16-99B8-1E75BBEFA7DF` |
| CoreAnalytics | 262 | `155.140.4.0.0` | `742D05D9-7082-307B-A1AE-8D72120856CA` |
| MultitouchSupport | 1249 | `5100.27.0.0.0` | `0EAF98B3-8D31-3A90-A578-1787797B9467` |
| IOKit | 71 | `1955.140.2.0.0` | `4AA27953-BAC7-3BCC-A036-2E0CA754907F` |
| ProtocolBuffer | 186 | `288.32.9.15.1` | `A1947EB8-542F-3676-B3CC-EDD3B628B96F` |

The full paths and evidence interpretation are recorded in the
[target dependency image inventory](iphone91-19h422-multitouch-dependency-image-inventory.md).

This specifically resolves the earlier ambiguity around
SymptomDiagnosticReporter: it is **not listed as a direct dependency** by
the target MultitouchHID PrebuiltLoaderSet record, but it **is present as
an image-list entry** in the target dyld cache. The donor-only difference
is therefore a loader-edge difference, not evidence that the target cache
lacks the framework.

The query for `IOKit.framework` also returned a CoreAudioKit substring
match at index 732. CoreAudioKit is separate; the relevant IOKit image is
the exact `IOKit.framework/Versions/A/IOKit` record at index 71.

These cache image-list records do not prove runtime dependency resolution,
standalone filesystem presence, transitive dependency closure, or plugin
loading. The next static comparison is the equivalent selected-name lookup
against the donor 20H392 cache inventory.


## Target MultitouchSupport PrebuiltLoaderSet record

The user supplied a successful read-only
`ipsw dyld image` result for
`/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport`
from the target 19H422 cache. The record reports VM Size
`0x3d3f0000`, loader reference `index: 1248`, flags
`prebuilt|in-cache-dylib|objc|never-unload`, Info flags
`regions=5`, and exports trie offset `0x01c64b98`, size
`0x1ca8`. It contains five regions with permission sequence
`r-x`, `rw-`, `rw-`, `rw-`, `r--`.

The command's `Dependents` block lists six regular rows:
IOKit.framework/Versions/A/IOKit, libIOReport.dylib,
CoreFoundation.framework/CoreFoundation,
Foundation.framework/Foundation, libobjc.A.dylib, and libSystem.B.dylib.
It does not list `libc++.1.dylib`.

The separate target cache image inventory identifies MultitouchSupport
at image-list index 1249, version `5100.27.0.0.0`, UUID
`0EAF98B3-8D31-3A90-A578-1787797B9467`.

The side-by-side target/donor loader fields, exact region rows, dependency
lists, and parser caveat are recorded in
[the MultitouchSupport loader comparison](20h392-19h422-multitouchsupport-loader-comparison.md).
The displayed Sections values are excluded because they contain
implausibly large decoded offsets/sizes. This remains static loader metadata;
runtime resolution, loading, and touch operation are unverified.


## Target libc++ cache image record

The user searched the exact image path
`/usr/lib/libc++.1.dylib` in the existing read-only 19H422 dyld image
inventory. Exactly one record was returned:

| Field | Target 19H422 |
|---|---|
| Image-list index | 150 |
| Path | `/usr/lib/libc++.1.dylib` |
| Version | `1300.36.0.0.0` |
| UUID | `16BE14F2-A677-3DF1-984D-BBAB893EE3B9` |

This confirms that libc++ is represented in the target dyld cache image
list. It does not change the observation that the target MultitouchSupport
PrebuiltLoaderSet output does not list libc++ as a direct dependent-loader
row. Cache image-list membership and an individual image's dependent-loader
edges are separate evidence types. Runtime resolution and library loading
remain unverified. See
[the donor/target libc++ comparison](20h392-19h422-libcxx-cache-image-comparison.md).


## Target MultitouchSupport exported-name comparison

The user supplied the target-side and donor-side `Dyld Exports` output for
`MultitouchSupport`. The target image is cache index 1249, version
`5100.27.0.0.0`, UUID
`0EAF98B3-8D31-3A90-A578-1787797B9467`. The first pasted block is
treated as target because the documented command prints target before
donor; the pasted excerpt omitted the target heading and both parser
exit-code lines.

Seven names are visible in the donor list but not in the target list:
`_MTDeviceGetMaxHoverHeightValue`,
`_MTDeviceGetMultipleFirmwaresConfig`,
`_MTDeviceSetBinaryFiltersProperty`,
`_MTDeviceShouldSkipFaceDetectionMode`,
`_MTDeviceUpdateUILockState`,
`_OBJC_CLASS_$_MTAHTSupport`, and
`_OBJC_METACLASS_$_MTAHTSupport`. All seven are printed as
`regular`. The target list has a broad overlapping multitouch export
surface. Exact counts, duplicates, and target-only names remain pending
automated comparison of the saved full logs. These export records do not
prove ABI compatibility or runtime loading. See
[the target/donor export comparison](20h392-19h422-multitouchsupport-export-comparison.md).
