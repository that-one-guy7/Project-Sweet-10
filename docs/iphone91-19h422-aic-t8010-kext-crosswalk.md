# iPhone9,1 19H422 AIC and T8010 KEXT personality crosswalk

## Scope and artifact identity

This is a host-side, read-only cross-reference of the user's KEXT JSON output
for the iPhone 7 target reference: `iPhone9,1` / D10AP / iOS 15.8.8 build
`19H422`. The source file inspected on the user's Ubuntu host was:

`$HOME/19H422-kernel-inspect/analysis/kexts.json`

The KernelCache identity already recorded in
[the target KEXT inventory](iphone91-19h422-kernelcache-kext-inventory.md)
is 44,924,928 bytes, SHA-256
`7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`,
XNU `8020.241.44~1`, target `RELEASE_ARM64_T8010`, with 230 KEXT
entries. The installed standalone ipsw binary used for this report was
3.1.749 (`a7dfadbcaca8375b424c12a68dae40767e5e07c1`).

The supplied output reports `Matching records: 129`. That is a count of
matching JSON locations, **not 129 distinct KEXT bundles**: the search also
matched many KEXT `os_bundle_libraries` dictionaries that reference
`AppleARMPlatform`. The table below records only the distinct top-level
bundle records and personality dictionaries visibly present in the supplied
output. JSON array locations are retained as provenance, not treated as
runtime indexes.

## AIC controller: direct exact static match

| Field | Target KernelCache metadata |
|---|---|
| JSON location | `$[172]` |
| Bundle ID | `com.apple.driver.AppleInterruptController` |
| Name / executable | `AppleInterruptController` |
| Bundle path | `/System/Library/Extensions/AppleInterruptController.kext` |
| Version | `1.0.0d1` (short version `1.0.0`) |
| Minimum OS / platform | `15.8` / `iPhoneOS` |
| Required bundle class | `Root` |
| Personality | `AppleInterruptController` |
| `IOClass` | `AppleInterruptController` |
| `IONameMatch` | `aic,1` |
| `IOProviderClass` | `AppleARMIODevice` |
| Reported Apple platform library | `com.apple.driver.AppleARMPlatform` version `1.0.0` |

The independently parsed target DeviceTree records
`/arm-io/aic` with `compatible = aic,1`,
`device_type = interrupt-controller`, and
`interrupt-controller = master`. Its `reg` tuples and the separate
`/arm-io/aic-timebase` node are preserved in the
[AIC source-availability audit](aic-controller-source-availability-audit.md).

**Finding:** the target DeviceTree compatible string and target KernelCache
personality `IONameMatch` are an exact static string match. The KEXT's
declared provider class is `AppleARMIODevice`. This resolves the earlier
metadata question about the presence of the controller bundle and personality
in the 19H422 target KernelCache.

It does not prove that the service attaches at runtime, that an interrupt is
delivered, or that register offsets, IRQ mapping, CPU routing, acknowledge/EOI,
or timer behavior are correctly implemented.

## T8010 platform-family KEXT records

The same output provides the following target-native bundle/personality
metadata. Fields are reproduced only where they appeared in the supplied
output.

| Bundle | Version | Personality / `IONameMatch` | `IOProviderClass` or other match field |
|---|---:|---|---|
| `AppleARMPlatform` | `1.0.2` | No personality shown in this excerpt | Bundle/library dependency reference |
| `AppleT8010SmartIO` | `1` | No personality shown in this excerpt | Bundle presence only |
| `AppleT8010SOCTuner` | `1` | `soc-tuner,t8010` | `ApplePMGRNub` |
| `AppleT8010PMGR` | `1` | `pmgr1,t8010` | `AppleARMIODevice` |
| `AppleT8010PCIe` | `1` | `apcie,t8010` | `AppleARMIODevice` |
| `AppleT8010PMPFirmware` | `1` | RTBuddy firmware-service personality | `RTBuddy`; match category `RTBuddyFirmwareService` |
| `AppleT8010CLPC` | `1` | `clpc,t8010` | `ApplePMGRNub` |
| `AppleT8010` | `1` | `arm-io,t8010` | `IOPlatformDevice` |
| `AppleT8010` | `1` | `mcc,t8010` | `AppleARMIODevice` |
| `AppleT8010` | `1` | `error-handler,t8010` | `AppleARMIODevice` |

Additional dependency facts visible in the output:

- `AppleT8010PMGR` and `AppleT8010CLPC` list
  `com.apple.driver.ApplePMGR` in their `os_bundle_libraries`.
- `AppleT8010` lists `com.apple.driver.AppleHurricaneErrorHandler`.
- `AppleT8010PMPFirmware` declares `RTBuddyFirmwareService` and depends
  on `AppleA7IOP`, `AppleARMPlatform`, `IOSlaveProcessor`, and
  `RTBuddy` in the supplied library record.

The `AppleT8010SmartIO` excerpt contained a bundle record but did not show a
personality dictionary. That is an output limitation, not proof that no
personality exists in the full prelink data or binary.

## Interpretation and limits

1. This is metadata from the **iOS 15.8.8 / XNU 8020.241.44~1 target
   reference**, not the iOS 16.7.16 / XNU 8796.142.1.703.8~1 donor kernel.
2. A static `IONameMatch` overlap establishes a metadata relationship only.
   It does not show an IOKit provider attaches, that dependencies resolve at
   runtime, or that the device operates.
3. The 19H422 AIC KEXT is not a public XNU 8796 source implementation.
   The public XNU 8796 references to `AppleInterruptController` previously
   found in DTrace/LLDB are diagnostics, not its driver source.
4. The output does not supply interrupt specifier decoding, IRQ numbering,
   trigger modes, priorities, per-CPU routing, acknowledge/EOI behavior,
   or a validated timer callback/frequency.
5. Do not copy the iOS 15 target KEXT into the iOS 16 donor stack or infer
   cross-SoC compatibility from matching names.
6. Do not derive register constants from the XNU AIC header comment alone.
   The `AIC_BASE + 0x1000` comment still needs reconciliation with the
   target's separate AIC and AIC-timebase DeviceTree windows.
7. The target KernelCache JSON's `signature: ????` display is not a
   cryptographic signature validation result.

## Best next static inspection

The highest-value next artifact is a **single-KEXT ABI inventory** for
`com.apple.driver.AppleInterruptController` from the already extracted
19H422 KernelCache. Record its Mach-O UUID/build metadata, load commands,
linked libraries, and imported symbols if the local ipsw version supports
symbol resolution. Then compare symbol/API names and version requirements
against the pinned public XNU 8796 interfaces. Keep that comparison
descriptive: symbol-name presence is not proof of semantic or runtime
compatibility.

The official ipsw CLI documents
`ipsw kernel extract <KERNELCACHE> <KEXT> --imports -o <DIRECTORY>`;
the user's installed 3.1.749 binary should be queried with the subcommand
help first to verify that this exact flag is supported by that version.
Extract only this named KEXT for the bounded audit; do not extract or commit
the entire KernelCache/KEXT set.

## Preservation

This report uses user-supplied host output and existing repository
DeviceTree/KernelCache records only. It does not alter a device, firmware,
partition, boot state, or the user's iOS 12.1.4 installation. M6 remains
in progress; M7/SpringBoard has not started.
