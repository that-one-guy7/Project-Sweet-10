# KernelCache KEXT JSON versus nested plugin metadata

## Purpose

This note records a source-level limitation discovered while reviewing the target iPhone 7 / iPhone9,1 iOS 15.8.8 (19H422) KernelCache inventory. It explains why the missing `io_kit_personalities` key in the `AppleMultitouchSPI` JSON record must not be interpreted as proof that the bundle has no nested plugin or no related IOKit role.

This is a host-side metadata audit only. The physical iPhone remains on iOS 12.1.4. No kernel, KEXT, plugin, filesystem, or boot state is changed.

## Pinned tool source

The user used ipsw 3.1.749, pinned in this project to commit:

```text
a7dfadbcaca8375b424c12a68dae40767e5e07c1
```

The reviewed implementation establishes the following path:

1. `ipsw kernel kexts --json` calls `kernelcache.KextJSON`.
2. `KextJSON` calls `GetKexts`.
3. `GetKexts` reads the KernelCache Mach-O section `__PRELINK_INFO.__info`, decodes its prelink plist, and returns the `_PrelinkInfoDictionary` bundle records.
4. `KextJSON` JSON-marshals those records.

In the pinned `pkg/kernelcache/kext.go`, the decoded `CFBundle` type declares:

```go
IOKitPersonalities map[string]any `plist:"IOKitPersonalities,omitempty" json:"io_kit_personalities,omitempty"`
```

The JSON tag includes `omitempty`. Thus, the serialized JSON omits the key when the decoded map is nil or empty. The output does not distinguish whether the original plist omitted the key or supplied an empty map.

The separate `ipsw kernel extract` implementation selects and exports a Mach-O fileset entry from the KernelCache. It is not a traversal of a filesystem KEXT bundle's `PlugIns` directory or a general filesystem bundle-resource extractor.

## What the AppleMultitouchSPI result means

The target 19H422 JSON output contained an `AppleMultitouchSPI` bundle record but did not include an `io_kit_personalities` field in that record.

The related `AppleMultitouchDriver` personality metadata supplied by the user separately references:

```text
AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin
```

That reference is a filesystem bundle/plugin path. Its existence and contents cannot be confirmed from the absence or presence of the `AppleMultitouchSPI` prelink personality map alone.

The correct evidence statement is:

- **Confirmed:** `AppleMultitouchSPI` is present in the target KernelCache KEXT inventory.
- **Confirmed:** the supplied `AppleMultitouchDriver` personality metadata references `MultitouchHID.plugin` under `AppleMultitouchSPI.kext/PlugIns`.
- **Confirmed:** the `AppleMultitouchSPI` JSON object did not serialize an `io_kit_personalities` field.
- **Confirmed:** the matching 19H422 filesystem query extracted the nested plugin `Info.plist` and `_CodeSignature/CodeResources`.
- **Confirmed:** the plugin bundle identifier is `com.apple.iokit.plugin.MultitouchHID`, version `5100.27`, supported platform `iPhoneOS`, minimum OS `15.8`, and SDK/platform build `19H402`.
- **Confirmed:** the plugin advertises type UUID `0516B563-B15B-11DA-96EB-0014519758EF`, mapped to factory UUID `0CB0FBB9-15EA-11DB-A93C-001451D47183` and `IOHIDPlugInFactory`.
- **Not established:** whether the declared `MultitouchHID` executable was extracted, can be loaded, or is instantiated by a runtime IOKit service.
- **Not established:** any runtime touch operation or successful IOKit attachment.

Do not rephrase the missing JSON field as "AppleMultitouchSPI has no personalities" or "the plugin is missing."

## Matching 19H422 filesystem result

The user successfully mounted the target 19H422 filesystem DMG on the analysis
computer using the standalone Linux build of ipsw 3.1.749. The selected
filesystem DMG was `098-68844-067.dmg`. The extracted plugin path was:

```text
/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/Info.plist
```

The broad driver-name extraction also returned the plugin's
`_CodeSignature/CodeResources`. The extracted `Info.plist` reports:

| Field | Value |
|---|---|
| Bundle identifier | `com.apple.iokit.plugin.MultitouchHID` |
| Bundle name | Multitouch HID Service Plugin |
| Declared executable | `MultitouchHID` |
| Bundle version | `5100.27` |
| Supported platform | `iPhoneOS` |
| Minimum OS | `15.8` |
| Platform / SDK build | `19H402` |
| SDK name | `iphoneos15.8.internal` |
| Required capability | `arm64` |

The plugin's `CFPlugInTypes` declares
`0516B563-B15B-11DA-96EB-0014519758EF` and maps it to factory UUID
`0CB0FBB9-15EA-11DB-A93C-001451D47183`. The factory name is
`IOHIDPlugInFactory`.

The target KernelCache's `AppleMultitouchDriver` personality maps the same
type UUID to
`AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin`. The type UUID
therefore links the parent's plugin request to the plugin's own declared
factory interface at the static metadata level.

The declared executable name is not evidence that the executable bytes were
extracted by the reported query. The extracted file list contains the
`Info.plist` and `_CodeSignature/CodeResources`, not the plugin executable.
No conclusion is made about code validity, runtime loading, IOKit attachment,
or touch delivery. The parent KEXT metadata remains sourced from the
KernelCache JSON; the unsuccessful search for parent bundle plists does not
prove those bundles are absent from the filesystem.

This closes the static filesystem-plugin metadata check. It does not establish
compatibility with the separate iOS 16.7.16 / 20H392 donor.

## Pinned source references

- [ipsw 3.1.749: `kernel_kexts.go`](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/kernel/kernel_kexts.go)
- [ipsw 3.1.749: `kernelcache/kext.go`](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/pkg/kernelcache/kext.go)
- [ipsw 3.1.749: `kernel_extract.go`](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/kernel/kernel_extract.go)
- [ipsw 3.1.749: `kernel kexts` command reference](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/www/docs/cli/ipsw/kernel/kexts.md)

## Status

**Source audit complete.** The `ipsw` JSON omission semantics and extraction boundary are confirmed from the pinned implementation.

**Filesystem metadata check complete.** The matching 19H422 plugin `Info.plist` and `CodeResources` were extracted and its type/factory UUIDs cross-checked against `AppleMultitouchDriver`. Plugin executable extraction/loading, runtime IOKit attachment, touch delivery, and 20H392 compatibility remain unverified. M6 remains in progress; M7 has not started.
