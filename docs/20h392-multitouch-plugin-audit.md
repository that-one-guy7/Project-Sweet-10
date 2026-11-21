# 20H392 donor Multitouch HID plugin metadata audit

## Purpose and evidence boundary

This report records the user's read-only inspection of the nested
`MultitouchHID.plugin/Info.plist` in the mounted iPhone X iOS 16.7.16
(20H392) donor filesystem and compares it with the already inspected iPhone 7
iOS 15.8.8 (19H422) target-reference plugin.

The physical iPhone 7 remains on iOS 12.1.4. These files were read from host
mounts only; neither donor nor target filesystem was installed on the phone.
The donor is iPhone10,3 / D22AP / A11-T8015. The target is iPhone9,1 / D10AP /
A10-T8010.

This audit establishes static plist metadata and matching plugin-interface
identifiers only. It does not establish binary compatibility, successful
plugin loading, runtime IOKit attachment, touch-event delivery, or
cross-board support.

## Donor artifact and provenance

The user found the donor plist in the mounted filesystem tree at:

```text
20H392/mnt/root/root/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/Info.plist
```

Observed file details:

- Size: 1,126 bytes.
- SHA-256: `6700b351288f1420754edcc8107a118b935d7ce250653f737ff448f9ddb7f3b1`.
- Source release: iOS 16.7.16, build 20H392, donor product iPhone10,3.
- Inspection method: Python standard-library `plistlib` reading the mounted file.

The donor KernelCache independently reports Darwin 22.6.0 and
`xnu-8796.142.1.703.8~1/RELEASE_ARM64_T8015`, SHA-256
`2ec297bac95bcba01046fd0148e97e7e5885c05a6c18827f39f534ba375c1221`.
The filesystem plist and KernelCache are separate donor artifacts; the
KernelCache identity is included only to identify the same donor build context.

## Direct comparison

| Info.plist field | Target: iPhone9,1 / 19H422 | Donor: iPhone10,3 / 20H392 |
|---|---|---|
| `CFBundleIdentifier` | `com.apple.iokit.plugin.MultitouchHID` | `com.apple.iokit.plugin.MultitouchHID` |
| `CFBundleName` | `Multitouch HID Service Plugin` | `Multitouch HID Service Plugin` |
| `CFBundleVersion` | `5100.27` | `6140.3` |
| `CFBundleShortVersionString` | `5100.27` | `6140.3` |
| `MinimumOSVersion` | `15.8` | `16.7` |
| `CFBundleSupportedPlatforms` | `iPhoneOS` | `iPhoneOS` |
| `CFBundleExecutable` | `MultitouchHID` | Not included in the user's printed donor-field subset |
| Plugin type UUID | `0516B563-B15B-11DA-96EB-0014519758EF` | `0516B563-B15B-11DA-96EB-0014519758EF` |
| Factory UUID | `0CB0FBB9-15EA-11DB-A93C-001451D47183` | `0CB0FBB9-15EA-11DB-A93C-001451D47183` |
| Factory function | `IOHIDPlugInFactory` | `IOHIDPlugInFactory` |

The target Info.plist extraction previously confirmed its bundle identifier,
version, minimum OS, platform, type UUID, factory UUID, and factory function.
A target Info.plist SHA-256 was not included in the user's supplied output
and is therefore not recorded here.

## Plug-in interface mapping

The donor plist reports:

```text
CFPlugInTypes:
  0516B563-B15B-11DA-96EB-0014519758EF:
    - 0CB0FBB9-15EA-11DB-A93C-001451D47183

CFPlugInFactories:
  0CB0FBB9-15EA-11DB-A93C-001451D47183:
    IOHIDPlugInFactory
```

The same type UUID and factory UUID/function were observed in the 19H422
target plugin plist. The type UUID also matches the key used by the
`AppleMultitouchDriver` `IOCFPlugInTypes` entries in both target and donor
KernelCache JSON records.

This is a strong, exact static interface-metadata match across the two
inspected builds. It means the two plist declarations describe the same
CoreFoundation plug-in type/factory identifiers. It does not prove that
their executable implementations are byte-identical, ABI-compatible beyond
the declared interface, or usable with each other's kernels and hardware.

## Interpretation

The confirmed commonality is:

- Same plugin bundle identifier.
- Same supported platform (`iPhoneOS`).
- Same plugin type UUID.
- Same factory UUID.
- Same factory function name.
- The donor and target parent KEXT personality metadata both reference the
  same plugin type UUID.

The confirmed differences are:

- Donor version `6140.3` versus target version `5100.27`.
- Donor minimum OS `16.7` versus target minimum OS `15.8`.

The differing version and minimum OS values show that the donor plugin is a
later build. The shared UUIDs establish interface identifier continuity, not
binary or runtime compatibility. The donor kernel targets A11/T8015, while
the project hardware target is A10/T8010. The XNU 8796 T8010 machine-profile
gap remains independent and unresolved.

No claim is made that the donor plugin should be copied onto the target, that
the 20H392 parent driver can bind to the target controller, or that the
target will expose the same HID descriptors or runtime service graph.

## Executable-file availability check

On 2026-11-20, the user searched both mounted donor filesystem trees:

- `$HOME/20H392/mnt/root/root`
- `$HOME/20H392/systemos-mnt/root/root`

The recursive search included regular files and symlinks and looked for names
matching `MultitouchHID*`. It returned no paths in either tree. A direct
listing of the donor plugin directory then showed only:

- `Info.plist` (1,126 bytes).
- `_CodeSignature/CodeResources` (2,467 bytes).

The earlier target plugin directory listing showed only `Info.plist`
(1,117 bytes). This target result is limited to the inspected plugin
directory; a recursive search of the entire target mounted filesystem has
not been recorded.

Therefore, neither plugin executable is currently available for a Mach-O
comparison from the inspected bundle directories. The donor search covers
the two stated mounted trees, not every possible IPSW component or an
unmounted/shared-cache representation. The target finding is narrower and
must not be generalized to its entire filesystem. The presence of
`CodeResources` is not proof of a valid code signature and does not supply
the executable bytes.

## Evidence classification

| Claim | Status |
|---|---|
| Donor plugin Info.plist exists in the mounted 20H392 filesystem | Confirmed by user-supplied path and successful plist read |
| Donor plist size and SHA-256 | Confirmed: 1,126 bytes; hash recorded above |
| Donor bundle ID/version/minimum OS/platform | Confirmed from printed plist fields |
| Donor type UUID/factory UUID/factory function | Confirmed from printed plist fields |
| Donor and target plugin type UUIDs match | Exact string equality confirmed |
| Donor and target factory UUIDs/functions match | Exact string equality confirmed |
| Donor `MultitouchHID*` file/symlink in the two searched mounted roots | Not found by the user's recursive search on 2026-11-20 |\n| Donor plugin directory contents | Only `Info.plist` and `_CodeSignature/CodeResources` listed |\n| Target plugin directory contents | Only `Info.plist` listed; no whole-target-root search recorded |\n| Plugin executable bytes or Mach-O identity | Not available from the inspected plugin directories; comparison blocked |
| Code signature validity | Not tested |
| Runtime plug-in load or IOKit attachment | Not tested |
| Touch-event delivery on iPhone9,1 | Not tested |
| Cross-board or cross-kernel compatibility | Not established |

## Next bounded host-side research

The plugin plist comparison is complete, but the expected executable was
not found in either searched donor mount tree, and the target plugin directory
listing also did not contain it. The next bounded host-side check is to read
the donor plist's `CFBundleExecutable` value and inspect the
`_CodeSignature/CodeResources` manifest to determine which bundle resources
it records. Separately, perform a filename-only recursive search of the
complete target mounted filesystem for the target's declared executable.
Only if actual executable files are located should their Mach-O metadata be
compared. Do not infer signature validity from the existence of
`CodeResources`; it is not a cryptographic verification result.

Any executable comparison remains descriptive. It must not be used as a
basis for copying donor binaries to the iPhone 7 or claiming runtime
compatibility. No device, firmware, partition, activation, security, or boot
state was accessed or changed. No binary, filesystem image, KernelCache, or
raw DeviceTree is committed to the repository.
