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
| Touch transport | `com.apple.driver.AppleHIDTransport` | 5100.32 | Touch node uses `hid-transport,k1` | KEXT presence; provider chain unverified |
| SPI HID transport | `com.apple.driver.AppleHIDTransportSPI` | 5100.32 | Touch node is below the SPI controller | KEXT presence; provider chain unverified |
| SPI multitouch | `com.apple.driver.AppleMultitouchSPI` | 5100.27 | `/arm-io/spi2/multi-touch` is `hid-transport,k1` | Strong subsystem correspondence; IOKit match unverified |
| Multitouch framework driver | `com.apple.driver.AppleMultitouchDriver` | 5100.27 | Target DeviceTree identifies the K1 multitouch transport | KEXT presence; binding and event path unverified |
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

The full ordered KEXT listing is retained in the user's local analysis output, not copied into the repository wholesale. No KernelCache or extracted KEXT binary is committed.

## Cross-reference to parsed target DeviceTree

The separate 19H422 DeviceTree audit records:

- Board/product identity: `D10AP` / `iPhone9,1`.
- SoC node: `/arm-io`, compatible with `arm-io,t8010`.
- Display subsystem: `/arm-io/disp0`, compatible with `disp0,t8010`.
- LCD panel: `lcd,pinot`.
- SPI controller: `/arm-io/spi2`, compatible with `spi-1,samsung`.
- Touch child: `/arm-io/spi2/multi-touch`, compatible with `hid-transport,k1`.
- Backlight node: `/arm-io/i2c0/lm3539`, compatible with `backlight,lm3539`.

The KEXT inventory and personality metadata now establish six exact static IONameMatch overlaps: display (`disp0,t8010`), Synopsys MIPI-DSI (`mipi-dsim-1,synopsys`), LCD (`lcd,pinot`), Samsung SPI (`spi-1,samsung`), K1 SPI HID transport (`hid-transport,k1`), and backlight (`backlight,lm3539`). The separate `AppleMobileDispH9P` BacklightMatching condition requiring `backlight-control = true` is not confirmed: the allowlist-filtered target output did not report that property on `/arm-io/disp0`. Other relationships and runtime attachment remain separate questions.

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

**Still open:** runtime IOKit provider attachment, the display/backlight association, nested `MultitouchHID.plugin` filesystem metadata, XNU 8796 T8010 platform implementation, and 20H392 userland service compatibility.

M6 remains in progress. M7 (SpringBoard on iPhone9,1) has not started.


## `ipsw` metadata boundary

The pinned ipsw 3.1.749 source shows that `ipsw kernel kexts --json` serializes the KernelCache's `_PrelinkInfoDictionary` records. `io_kit_personalities` is an optional, `omitempty` field in the decoded `CFBundle` record. Therefore, its absence in the `AppleMultitouchSPI` JSON object is not evidence that the related nested plugin is absent or unused. The separate `MultitouchHID.plugin` path must be verified from the matching 19H422 filesystem bundle, not inferred from the KernelCache KEXT JSON. The source-level basis and next evidence needed are recorded in [the metadata boundary audit](ipsw-kernelcache-plugin-metadata-boundary.md).


## Linux filesystem extraction status

The matching 19H422 filesystem plugin check is currently blocked at the host-side
DMG mount stage. The user's ipsw 3.1.749 attempt reached filesystem DMG
`098-68844-067.dmg`, then returned an HFS+ partition-probe error. The pinned
source shows that this can be the secondary HFS+ fallback after an earlier
APFS-FUSE failure; the APFS-FUSE failure itself has not yet been captured.
See [the Linux DMG mount fallback audit](ipsw-linux-dmg-mount-fallback-audit.md).
Do not interpret this output as evidence that the IPSW is HFS+ or corrupt.
