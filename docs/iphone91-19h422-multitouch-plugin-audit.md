# iPhone9,1 19H422 Multitouch HID plugin metadata audit

## Purpose and evidence boundary

This report records host-side, read-only metadata inspection of the iPhone 7
(iPhone9,1 / D10AP / A10-T8010) iOS 15.8.8 (19H422) reference artifacts.
It connects the target KernelCache's multitouch-related KEXT records with the
nested `MultitouchHID.plugin` Info.plist extracted from the matching 19H422
filesystem DMG.

The physical iPhone remains on iOS 12.1.4. The 19H422 KernelCache and filesystem
are reference artifacts inspected on the host; they were not installed on the
phone. This is not the iPhone X iOS 16.7.16 (20H392) donor kernel or userland.

These results establish static metadata relationships only. They do not prove
that IOKit attaches the services at runtime, that touch events reach userland,
that the plugin executable has a valid signature, or that these iOS 15.8.8
components can be transplanted into the separate 20H392 system.

## Inputs and extraction result

The target KernelCache previously inspected by the user has:

- Product: iPhone9,1 / D10AP / A10-T8010.
- IPSW: iOS 15.8.8 (19H422).
- Darwin 21.6.0; XNU `8020.241.44~1`.
- Kernel target: `RELEASE_ARM64_T8010`.
- KernelCache SHA-256: `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`.
- KEXT inventory: 230 entries.
- Inspection utility: ipsw 3.1.749.

The user first attempted filesystem extraction through the Snap-packaged ipsw.
Although the host shell confirmed `/usr/local/bin/apfs-fuse` existed and was
executable, that ipsw process reported the override path as nonexistent. The
user then used the standalone Linux ipsw 3.1.749 archive and the explicit
`IPSW_APFS_FUSE_PATH=/usr/local/bin/apfs-fuse` setting. That invocation
successfully mounted the filesystem DMG and extracted:

```text
root/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/Info.plist
root/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/_CodeSignature/CodeResources
```

The successful standalone extraction resolves the earlier host-side DMG
mount blockage. The exact internal reason the Snap process could not see the
helper path was not independently isolated. The extraction output confirms
the two listed metadata/resource files; it does not establish that the plugin
executable was extracted or that its code signature was validated.

## Target KernelCache KEXT metadata

The user supplied the relevant records from `ipsw kernel kexts --json`.

| KEXT | Bundle path | Version | Relevant metadata |
|---|---|---:|---|
| `AppleHIDTransportSPI` | `/System/Library/Extensions/AppleHIDTransport.kext/PlugIns/AppleHIDTransportSPI.kext` | 5100.32 | Personality `AppleHIDTransportDeviceSPI`; provider `AppleARMSPIDevice`; exact `IONameMatch` values include `hid-transport,k1` and `hid-transport,spi` |
| `AppleMultitouchSPI` | `/System/Library/Extensions/AppleMultitouchSPI.kext` | 5100.27 | KEXT is present; its serialized KernelCache JSON record did not include an `io_kit_personalities` field |
| `AppleMultitouchDriver` | `/System/Library/Extensions/AppleMultitouchDriver.kext` | 5100.27 | Several `IOHIDInterface` personalities; raw usage-pair identifiers include `0x0D/0x04`, `0x0D/0x20`, and `0xFF60/0x1002`; selected personalities reference the nested plugin through `IOCFPlugInTypes` |

### AppleHIDTransportSPI

The reported personality is `AppleHIDTransportDeviceSPI`:

- `IOClass`: `AppleHIDTransportDeviceSPI`.
- `IOProviderClass`: `AppleARMSPIDevice`.
- `IONameMatch`: `hid-transport,k1`, `hid-transport,spi`.
- KEXT version: `5100.32`; minimum OS: `15.8`.
- Reported bundle libraries include AppleARMPlatform, AppleHIDTransport,
  AppleInputDeviceSupport, and the BSD, IOKit, libkern, and Mach KPIs.

The target DeviceTree node `/arm-io/spi2/multi-touch` has compatible
`hid-transport,k1`. This is an exact static string overlap with the
`AppleHIDTransportSPI` personality. It remains a metadata match, not proof of
runtime provider attachment.

### AppleMultitouchDriver

The reported `AppleMultitouchDriver` personalities use
`IOProviderClass = IOHIDInterface`. The user-supplied raw metadata includes
these usage-page / usage pairs:

- `0x0D / 0x04`.
- `0x0D / 0x20`.
- Vendor-defined `0xFF60 / 0x1002`.

This audit preserves the raw identifiers rather than adding usage labels.

The supplied records for these multitouch services include
`HIDServiceSupport = true` and an `IOCFPlugInTypes` entry referring to:

```text
AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin
```

The KEXT reports version `5100.27`, minimum OS `15.8`, and dependencies
including AppleInputDeviceSupport, IOHIDFamily, IOReportFamily, and KPI
libraries. The plugin path is a static relationship declared by the HID
service personalities. It does not prove that the provider service exists or
that the plugin is loaded.

### AppleMultitouchSPI

The KEXT record reports bundle identifier
`com.apple.driver.AppleMultitouchSPI`, version `5100.27`, and minimum OS
`15.8`. Its JSON record did not expose `io_kit_personalities`. The pinned
ipsw serialization audit explains that this field is optional in the JSON
representation; its absence must not be interpreted as proof that the KEXT or
its nested plugin is absent.

## Extracted MultitouchHID.plugin Info.plist

The matching 19H422 filesystem extraction returned these fields:

| Info.plist key | Observed value |
|---|---|
| `CFBundleIdentifier` | `com.apple.iokit.plugin.MultitouchHID` |
| `CFBundleName` | `Multitouch HID Service Plugin` |
| `CFBundleExecutable` | `MultitouchHID` |
| `CFBundlePackageType` | `BNDL` |
| `CFBundleShortVersionString` / `CFBundleVersion` | `5100.27` |
| `MinimumOSVersion` | `15.8` |
| `CFBundleSupportedPlatforms` | `iPhoneOS` |
| `UIRequiredDeviceCapabilities` | `arm64` |
| `CFPlugInDynamicRegistration` | `NO` |

The plugin declares this type-to-factory mapping:

- Plug-in type UUID: `0516B563-B15B-11DA-96EB-0014519758EF`.
- Factory UUID: `0CB0FBB9-15EA-11DB-A93C-001451D47183`.
- Factory function name: `IOHIDPlugInFactory`.

The type UUID matches the key used by the `AppleMultitouchDriver`
personalities' `IOCFPlugInTypes` dictionaries. The factory UUID matches the
key in the plugin plist's `CFPlugInFactories` dictionary. This provides a
complete static metadata cross-reference between the service personality's
plugin type and the nested plugin's declared factory.

The plist also reports `DTPlatformVersion = 15.8`,
`DTPlatformBuild = 19H402`, and
`DTSDKName = iphoneos15.8.internal`. The
`BuildMachineOSBuild = 20A241133` field is build-machine metadata; it is not
evidence that this is the 20H392 donor plugin. The source IPSW and inspected
KernelCache are the iPhone9,1 19H422 target reference.

## Static relationship summary

The supplied evidence now supports this metadata-only sequence:

1. Target DeviceTree: `/arm-io/spi2/multi-touch` is compatible with
   `hid-transport,k1`.
2. Target KernelCache: `AppleHIDTransportSPI` declares an
   `AppleARMSPIDevice` personality matching `hid-transport,k1`.
3. Target KernelCache: `AppleMultitouchDriver` declares upper-level
   `IOHIDInterface` personalities and associates the
   `0516B563-B15B-11DA-96EB-0014519758EF` plugin type with the nested
   `MultitouchHID.plugin` path.
4. Target filesystem: that plugin path contains an Info.plist declaring the
   same plugin type UUID and mapping its factory UUID to
   `IOHIDPlugInFactory`.

The chain is internally consistent at the static metadata level. It does not
establish that the SPI transport actually publishes the expected HID
interface, that the HID personality matches a live interface, that the
plugin factory executes, or that touch events reach applications.

## Evidence classification

| Evidence | Status |
|---|---|
| Target KernelCache contains the three named KEXT records | Confirmed by user-supplied ipsw JSON output |
| `AppleHIDTransportSPI` matches target `hid-transport,k1` | Exact static `IONameMatch` overlap confirmed |
| `AppleMultitouchDriver` references `MultitouchHID.plugin` | Confirmed in supplied KEXT personality metadata |
| Nested plugin Info.plist exists in the matching 19H422 filesystem | Confirmed by successful host-side extraction |
| Plugin bundle identifier, version, minimum OS, platform, and factory mapping | Confirmed in extracted Info.plist |
| Plugin standalone file in complete 19H422 filesystem | No matching regular file or symlink named `MultitouchHID*` returned; the dyld shared-cache inventory separately lists the compiled image |
| Code signature cryptographically validated | Not tested; extracting `_CodeSignature/CodeResources` alone is not validation |
| Target dyld shared-cache image | Image index 1948; path ends in `MultitouchHID.plugin/MultitouchHID`; version `5100.27.0.0.0`; UUID `304953E6-6B67-3CF1-B7CA-E011978210DE` |
| Runtime IOKit matching, provider attachment, plugin load, or touch operation | Not tested |
| Compatibility with iPhone X 20H392 donor kernel/userland | Not established |

## Full target-filesystem executable search

The user successfully mounted the complete 19H422 iPhone9,1 filesystem DMG
read-only with ipsw 3.1.749. The selected component was
`098-68844-067.dmg`, mounted at:

```text
/home/hey/19H422-full-fs-mount
```

The mount was confirmed by `findmnt` as FUSE with read-only options. The
user found the target extension directory at:

```text
/home/hey/19H422-full-fs-mount/root/System/Library/Extensions
```

A filename-only search was then run over the complete mount point, including
regular files and symlinks, for case-insensitive names matching
`MultitouchHID*`. It returned no paths. The command suppressed permission
and traversal diagnostics, so this is recorded as “no matching path returned
by the completed search,” not as a cryptographic or runtime result.

Together with the earlier target bundle extraction, this means the target
plugin Info.plist is present in the extracted metadata set, but no matching
plugin executable file or symlink was located anywhere in the mounted
19H422 filesystem DMG under the declared executable-name prefix. This does
not establish absence from every other IPSW component, an unmounted image,
or another shared-cache representation.

The target plugin image is now located in the 19H422 dyld shared-cache
image inventory (index 1948, version `5100.27.0.0.0`, UUID
`304953E6-6B67-3CF1-B7CA-E011978210DE`). The complete filesystem search
found no separate file, but the shared-cache entry demonstrates that the
compiled image is represented in the cache. See
[the 19H422 dyld shared-cache audit](iphone91-19h422-dyld-cache-multitouch-audit.md).

The next bounded static check is to query the separate 20H392 donor
SystemOS cache for its `MultitouchHID` image path, version, and UUID and
compare those records. Keep A11/T8015 donor and A10/T8010 target evidence
separate. Cache image metadata does not prove that a plugin loads at runtime,
that a provider attaches, or that touch events reach applications.

No device connection, firmware update, restore, partition write, exploit, or
boot operation is part of this report. No KernelCache, KEXT executable,
plugin executable, raw DeviceTree, or filesystem image is committed.

See also [the 19H422 dyld shared-cache multitouch image audit](iphone91-19h422-dyld-cache-multitouch-audit.md).
