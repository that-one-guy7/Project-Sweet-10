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
- **Not established:** whether the corresponding plugin is present in the target 19H422 root filesystem, its bundle identifier/version/executable, its plugin interface metadata, or whether any runtime service loads it.
- **Not established:** any runtime touch operation or successful IOKit attachment.

Do not rephrase the missing JSON field as "AppleMultitouchSPI has no personalities" or "the plugin is missing."

## Correct next evidence source

The next artifact to inspect is the **matching iPhone9,1 / D10AP / 19H422 filesystem bundle** containing:

```text
AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/Info.plist
```

The inspection should record only the small set of bundle metadata fields needed to identify the plugin, such as `CFBundleIdentifier`, `CFBundleName`, `CFBundleExecutable`, `CFBundleVersion`, and any explicit plugin/interface type identifiers. Do not publish the complete plist, executable, or filesystem image. Do not substitute the iPhone X 20H392 donor's similarly named file for target-native 19H422 evidence.

If the matching 19H422 filesystem has not been extracted on the host, this check remains pending. It does not require changing or updating the physical phone.

## Pinned source references

- [ipsw 3.1.749: `kernel_kexts.go`](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/kernel/kernel_kexts.go)
- [ipsw 3.1.749: `kernelcache/kext.go`](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/pkg/kernelcache/kext.go)
- [ipsw 3.1.749: `kernel_extract.go`](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/kernel/kernel_extract.go)
- [ipsw 3.1.749: `kernel kexts` command reference](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/www/docs/cli/ipsw/kernel/kexts.md)

## Status

**Source audit complete.** The `ipsw` JSON omission semantics and extraction boundary are confirmed from the pinned implementation.

**Filesystem check pending.** The matching 19H422 `MultitouchHID.plugin` bundle has not yet been inspected. M6 remains in progress; M7 has not started.
