# iPhone9,1 19H422 KernelCache KEXT inventory

## Purpose and evidence boundary

This is a read-only inventory of the iPhone 7 target's extracted iOS 15.8.8 (19H422) KernelCache. It records the kernel build identity and KEXT bundle IDs reported by ipsw, then cross-references candidate hardware KEXTs with the separately parsed target DeviceTree.

The physical iPhone remains on iOS 12.1.4. The 19H422 IPSW and its extracted files are host-side reference artifacts only. They are not installed on the phone and are not the iPhone X iOS 16.7.16 (20H392) donor kernel or userland.

This report does not establish that the 19H422 kernel can be substituted into an iOS 16 system, that a KEXT will bind at runtime, or that the device can boot a custom kernel.

## Artifact identity

The user supplied the output of a read-only inspection using ipsw 3.1.749.

| Field | Observed value |
|---|---|
| IPSW | iPhone 7 iOS 15.8.8 (19H422) |
| Product | iPhone9,1 |
| Extracted KernelCache | `kernelcache.release.iPhone9,1_3` |
| Reported size | 44,924,928 bytes |
| SHA-256 | `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee` |
| File identification | Mach-O 64-bit ARM64 executable; flags `NOUNDEFS|PIE` |
| ipsw version | 3.1.749, commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1` |
| Darwin version | 21.6.0 |
| XNU version | `xnu-8020.241.44~1` |
| Kernel build target | `RELEASE_ARM64_T8010` |
| KEXT inventory count | 230 |

The exact kernel version line reported by the tool was:

```text
Darwin Kernel Version 21.6.0: Fri Mar 6 20:59:07 PST 2026; root:xnu-8020.241.44~1/RELEASE_ARM64_T8010
```

The output directly identifies an iOS 15-generation T8010 release kernel. This is valuable target-native reference evidence. It is a different XNU branch/build from the iOS 16-generation 20H392 donor selected for Sweet-10.

### Relationship to the XNU 8796 source audit

The repository's public-source review found that the reviewed XNU 8796.141.3 normal ARM64 machine allowlist omits T8010, while an older public XNU 7195 snapshot contains T8010/H9 definitions. The 19H422 kernel version string now supplies independent evidence that Apple's iOS 15 target kernel was built as `RELEASE_ARM64_T8010`.

These results are not contradictory: the production 19H422 kernel is reported as XNU 8020.241.44, not the candidate XNU 8796.141.3. The target KernelCache does not reveal the full source tree or prove that its T8010 configuration can be carried forward into XNU 8796. The XNU 8796 T8010 platform gap therefore remains open.

## Target KEXT candidates found

The user-supplied complete ipsw listing reported 230 KEXT entries. The following entries are present in that target KernelCache. Their embedded IOKit personality metadata has now been inspected for the candidate display, touch/HID, SPI, and backlight bundles. Exact name-level overlaps are summarized in the [target IOKit personality crosswalk](iphone91-19h422-iokit-personality-crosswalk.md).

| Subsystem | Bundle identifier | Reported version | Related 19H422 DeviceTree evidence | Evidence level |
|---|---|---:|---|---|
| Display pipeline | `com.apple.driver.AppleMobileDispH9P` | 140.0.0 | `/arm-io/disp0` is `disp0,t8010` | KEXT presence; provider role still needs personality validation |
| LCD panel | `com.apple.driver.ApplePinotLCD` | 1.0.0 | MIPI-DSI child panel is `lcd,pinot` | Strong name-level correspondence; IOKit match unverified |
| MIPI-DSI | `com.apple.driver.AppleSynopsysMIPIDSI` | 1.0.0 | `/arm-io/mipi-dsim` is `mipi-dsim-1,synopsys` | Exact static `IONameMatch` overlap confirmed; runtime provider attach untested |
| SPI controller | `com.apple.driver.AppleSamsungSPI` | 1 | `/arm-io/spi2` reports Samsung SPI | Strong name-level correspondence; personality match unverified |
| Touch transport | `com.apple.driver.AppleHIDTransport` | 5100.32 | General HID transport layer | KEXT present; target-specific runtime role unverified |
| SPI HID transport | `com.apple.driver.AppleHIDTransportSPI` | 5100.32 | `/arm-io/spi2/multi-touch` is `hid-transport,k1` | Exact static `IONameMatch` overlap; provider attachment untested |
| SPI multitouch | `com.apple.driver.AppleMultitouchSPI` | 5100.27 | Nested `MultitouchHID.plugin` metadata extracted | KEXT present; no personality object in this JSON record; plugin/runtime loading untested |
| Multitouch framework driver | `com.apple.driver.AppleMultitouchDriver` | 5100.27 | `IOHIDInterface` personalities reference the nested plugin path | Static type-UUID linkage verified; runtime binding/event path untested |
| Backlight | `com.apple.driver.AppleLMBacklight` | 1 | `/arm-io/i2c0/lm3539` reports `backlight,lm3539` | Candidate only; do not infer an LM3539 match from the bundle name |

Additional target-platform KEXTs in the same inventory include:

| Bundle identifier | Reported version | Note |
|---|---:|---|
| `com.apple.driver.AppleT8010` | 1 | T8010 platform-family bundle present |
| `com.apple.driver.AppleT8010PMGR` | 1 | T8010 power-management family bundle present |
| `com.apple.driver.AppleT8010CLPC` | 1 | T8010 platform-control family bundle present |
| `com.apple.driver.AppleT8010SOCTuner` | 1 | T8010 SoC tuning family bundle present |
| `com.apple.AGXG9P` | 190.23 | GPU family bundle present; detailed device/provider matching not inspected |
| `com.apple.iokit.IOGPUFamily` | 35.29 | GPU framework-family bundle present |
| `com.apple.driver.AppleInterruptController` | 1.0.0d1 | Target-native AIC KEXT; exact `aic,1` personality / `AppleARMIODevice` provider match is documented in the [AIC KEXT inventory](iphone91-19h422-aic-kext-inventory.md) |
| `com.apple.driver.AppleT8010PCIe` | 1 | T8010 PCIe bundle and `apcie,t8010` personality are documented in the [AIC/T8010 KEXT inventory](iphone91-19h422-aic-kext-inventory.md) |

The full ordered KEXT listing is retained in the user's local analysis output, not copied into the repository wholesale. No KernelCache or extracted KEXT binary is committed.

## Cross-reference to parsed target DeviceTree

The separate 19H422 DeviceTree audit records:

- Board/product identity: `D10AP` / `iPhone9,1`.
- SoC node: `/arm-io`, compatible with `arm-io,t8010`.
- AIC node: `/arm-io/aic`, compatible with `aic,1`; target-native `AppleInterruptController` KEXT metadata has an exact `IONameMatch=aic,1` personality overlap. Runtime attachment remains unverified; see the [AIC/T8010 KEXT inventory](iphone91-19h422-aic-kext-inventory.md).
- Display subsystem: `/arm-io/disp0`, compatible with `disp0,t8010`.
- LCD panel: `lcd,pinot`.
- SPI controller: `/arm-io/spi2`, compatible with `spi-1,samsung`.
- Touch child: `/arm-io/spi2/multi-touch`, compatible with `hid-transport,k1`.
- Backlight node: `/arm-io/i2c0/lm3539`, compatible with `backlight,lm3539`.

The KEXT inventory and personality metadata now establish six exact static IONameMatch overlaps: display (`disp0,t8010`), Synopsys MIPI-DSI (`mipi-dsim-1,synopsys`), LCD (`lcd,pinot`), Samsung SPI (`spi-1,samsung`), K1 SPI HID transport (`hid-transport,k1`), and backlight (`backlight,lm3539`). The separate `AppleMobileDispH9P` BacklightMatching condition requiring `backlight-control = true` is not confirmed: the allowlist-filtered target output did not report that property on `/arm-io/disp0`. Other relationships and runtime attachment remain separate questions.

## Target multitouch plugin metadata

The standalone Linux ipsw 3.1.749 binary mounted the target 19H422 filesystem
DMG and extracted the nested `MultitouchHID.plugin/Info.plist` and
`_CodeSignature/CodeResources`. The plugin metadata identifies bundle
`com.apple.iokit.plugin.MultitouchHID`, version `5100.27`, platform
`iPhoneOS`, and minimum OS `15.8`.

The plugin declares type UUID
`0516B563-B15B-11DA-96EB-0014519758EF` and maps it to factory UUID
`0CB0FBB9-15EA-11DB-A93C-001451D47183` / `IOHIDPlugInFactory`.
The target `AppleMultitouchDriver` personality's `IOCFPlugInTypes` map
references the same type UUID and the nested plugin path. Separately,
`AppleHIDTransportSPI` names the target DeviceTree compatible
`hid-transport,k1`.

The detailed field inventory, extraction record, and evidence limitations are
in the [dedicated 19H422 multitouch plugin metadata audit](iphone91-19h422-multitouch-plugin-audit.md).
The parent KEXT metadata in this report comes from the KernelCache JSON. The
absence of an optional `io_kit_personalities` field from the
`AppleMultitouchSPI` JSON record does not establish that the plugin is absent.

This is static metadata only. It does not prove that a provider attaches, the
plugin executable loads, or touch events reach userland.

## Evidence levels and limits

Keep these levels separate:

1. **KEXT presence:** the bundle ID appears in the KernelCache inventory. This is now confirmed for the identifiers listed above.
2. **Personality metadata in the JSON:** eight of the nine requested candidate KEXT records contained an `io_kit_personalities` field in the user's output. `AppleMultitouchSPI` did not. This is only a statement about the serialized KernelCache prelink metadata returned by the tool; it does not prove the filesystem bundle has no nested plugin or that the driver has no related role. See the [KernelCache/plugin metadata boundary note](ipsw-kernelcache-plugin-metadata-boundary.md).
3. **Match-property overlap:** exact `IONameMatch` overlap is confirmed for six target nodes: display, Synopsys MIPI-DSI, Pinot LCD, Samsung SPI, K1 SPI HID transport, and LM3539 backlight. The display `backlight-control` property condition is not present in the allowlisted `/arm-io/disp0` output.
4. **Provider relationship:** the relevant IOKit service actually matches and attaches to the intended hardware. Static metadata alone may support a candidate relationship, but runtime binding and working hardware operation have not been validated.

Do not state that display, touch, or backlight is working. Do not infer that these iOS 15 KEXTs can be copied into, substituted for, or used as drop-in drivers in the 20H392 donor system. The donor's XNU/userland generation and board are different.

## Reproduction

The target personality report was exported from the already extracted 19H422
KernelCache with ipsw 3.1.749:

```sh
KC="$HOME/19H422-kernel-inspect/19H422__iPhone9,1_3/kernelcache.release.iPhone9,1_3"
OUT="$HOME/19H422-kernel-inspect/analysis"
mkdir -p "$OUT"
ipsw kernel kexts --json "$KC" > "$OUT/kexts.json"
```

The user's JSON output is summarized in the
[IOKit personality crosswalk](iphone91-19h422-iokit-personality-crosswalk.md).
No KEXT binary or KernelCache is committed to the repository.


## Status

**Completed:** the user supplied the KernelCache file identity, SHA-256, exact Darwin/XNU version, T8010 release target string, ipsw version, and 230-entry KEXT inventory. Candidate target hardware KEXTs are now cross-referenced against the sanitized 19H422 DeviceTree.

**Still open:** runtime IOKit provider attachment and event delivery, the display/backlight association, plugin executable extraction/loading, XNU 8796 T8010 platform implementation, and 20H392 userland service compatibility.

M6 remains in progress. M7 (SpringBoard on iPhone9,1) has not started.


## `ipsw` metadata boundary

The pinned ipsw 3.1.749 source shows that `ipsw kernel kexts --json` serializes the KernelCache's `_PrelinkInfoDictionary` records. `io_kit_personalities` is an optional, `omitempty` field in the decoded `CFBundle` record. Therefore, its absence in the `AppleMultitouchSPI` JSON object is not evidence that the related nested plugin is absent or unused. The user has now extracted the nested `MultitouchHID.plugin/Info.plist` from the matching 19H422 filesystem. Its bundle identity, version, minimum OS, plug-in type UUID, and factory mapping are recorded in the [multitouch plugin metadata audit](iphone91-19h422-multitouch-plugin-audit.md). The plugin executable and cryptographic signature remain unverified. The source-level serialization boundary is recorded in [the metadata boundary audit](ipsw-kernelcache-plugin-metadata-boundary.md).


## Linux filesystem extraction status

The initial Snap-packaged `ipsw` run could not see the host executable at
`/usr/local/bin/apfs-fuse`, even though the host shell confirmed that path
existed and was executable. The Snap connection listing showed `home`
connected and `fuse-support` disconnected. The confined Snap reported the
explicit `IPSW_APFS_FUSE_PATH` as a non-existent file.

The user then downloaded and extracted the official standalone Linux archive
for ipsw `3.1.749`. With that standalone binary and the same 19H422 IPSW, the
filesystem DMG `098-68844-067.dmg` mounted successfully through the APFS-FUSE
path, and ipsw extracted the nested `MultitouchHID.plugin/Info.plist`.
A broader driver-name query also extracted `_CodeSignature/CodeResources`.

This establishes that the standalone binary can mount and inspect this image
in the user's host environment. It does not fully diagnose the Snap sandbox
failure or identify the installed APFS-FUSE build/version. The parent KEXT
metadata used by this report is read from the KernelCache JSON, not inferred
from the filesystem query's lack of parent-bundle plist matches.

See the [Linux DMG mount fallback audit](ipsw-linux-dmg-mount-fallback-audit.md)
for the source-level explanation and the observed Snap-versus-standalone
difference. No full filesystem image, KernelCache, KEXT executable, or plugin
executable is committed to the repository.
