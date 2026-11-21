# Corrected T8010 XNU public-source history

## Important correction

The previous version of this document incorrectly stated that current public XNU `main` had restored the T8010 board profile. A direct read of the current `apple-oss-distributions/xnu` repository disproves that statement.

The earlier web result came from the separate archived `apple/darwin-xnu` repository and must not be treated as the current public source tree. The current source of record used for this comparison is `apple-oss-distributions/xnu`.

## Direct source comparison

The same two files were read at each exact ref: `pexpert/pexpert/arm64/board_config.h` and `makedefs/MakeInc.def`.

| XNU ref | T8010 board block in board_config.h | T8010 in normal ARM64 allowlist | Result |
|---|---|---|---|
| `xnu-7195.121.3` | Present; includes `H9.h` | Present; `MACHINE_FLAGS_ARM64_T8010 = -DARM64_BOARD_CONFIG_T8010 -mcpu=hurricane` | T8010 public profile present |
| `xnu-8019.80.24` | Absent | Absent; allowlist is `BCM2837 T6000 T8101 VMAPPLE` | Removed by this source generation |
| `xnu-8796.141.3` | Absent | Absent; allowlist is `BCM2837 T6000 T8101 T8103 VMAPPLE` | Still absent in pinned baseline |
| current `main` | Absent | Absent; allowlist is `T6000 T6020 T6030 T6031 T6041 T8101 T8103 T8112 T8122 T8132 VMAPPLE` | Not restored in current public main |

### Exact historical T8010 profile found in 7195

The 7195 `board_config.h` T8010 block:
- includes `pexpert/arm64/H9.h`;
- sets `MAX_CPUS 3`;
- sets `MAX_CPU_CLUSTERS 1`;
- sets `MAX_L2_CLINE 7`;
- under DEVELOPMENT/DEBUG, enables `PMAP_CS` and sets `PMAP_CS_ENABLE 0`.

The 7195 `MakeInc.def` normal ARM64 allowlist includes T8010 and defines the T8010 build flags with `-mcpu=hurricane`.

This is evidence of a historical public configuration, not a complete iPhone 7 platform implementation.

## What changed, and what it means

The T8010 board configuration and build allowlist are both absent from 8019, 8796 and current public main. Therefore the evidence does **not** support the earlier idea that simply moving to current public XNU would restore T8010 support.

The path-history endpoint for `board_config.h` at `xnu-8019.80.24` reports the first 8019 import in this path history as `xnu-8019.41.5` (commit `e6231be02a03711ca404e5121a151b24afbff733`, dated 2022-02-04 by the author metadata), whose parent is the public `xnu-7195.50.7.100.1` import (commit `bb611c8fecc755a0d8e56e2fa51513527c5b7a0e`). The T8010 block is already absent in the 8019.41.5 snapshot. This narrows the public snapshot boundary, but these are bulk source imports rather than a commit-by-commit development history; they do not identify the internal change that removed the profile.

The absence from public XNU does not prove Apple never maintained T8010 support internally. Apple's shipped iPhone9,1 19H422 kernel metadata is separately recorded as `8020.241.44~1 / RELEASE_ARM64_T8010`, showing that Apple shipped a T8010-targeted kernel in the iOS 15 generation. Public source snapshots and Apple's complete private build inputs are not interchangeable.

## Does changing iOS version solve the project?

Not automatically.

1. A fully matched iPhone9,1 iOS 15 kernel and userland is the closest stock-generation reference for the hardware, but it changes the project's goal away from the 20H392 iOS 16.7.16 donor userland.
2. Reusing the old 7195 T8010 board block with a newer XNU is not a safe or sufficient compatibility fix. The board header is only one part of the platform configuration; surrounding machine, CPU, interrupt, power, memory, device-tree, and kernel-interface changes still matter.
3. Keeping 20H392 means the missing public T8010 profile remains an open source-porting question. The historical 7195 profile can be studied as evidence, but should not be copied wholesale or treated as a working port.

**Revised recommendation:** keep the intended 20H392 research target documented, but do not claim that a newer public XNU revision has a T8010 profile. Before proposing any source change, establish the exact historical removal point and inventory the platform-specific files/configuration that changed between 7195 and 8019. This is static source research only.

## Additional T8010 reference in current public XNU

A follow-up inspection found one important nuance: current public XNU still contains a T8010 string in a test concerning PMAP code-signing support. In `tests/vm_test_code_signing.c` at commit `f6217f891ac0bb64f3d375211650a4c1ff8ca1ea`, the test lists `T8010`, `T8011`, `T8012`, and `T8015` as SoCs where PMAP_CS is disabled by default unless an explicit `pmap_cs=1` boot argument is present.

This is **not** a T8010 board configuration or a normal ARM64 build allowlist entry. It is a test's description of a feature policy for kernels whose reported platform string matches those SoCs. It therefore does not contradict the missing T8010 board block and build allowlist reported above, and it does not establish that current public XNU can build for or boot on T8010.

A bounded check of `osfmk/arm64/cpu.c` at the same four refs also found no T8010-specific conditional in that file; the later three snapshots contain a `T6000`-specific `wfe_allowed` conditional. This observation is limited to that file and those refs, not a complete source-tree search.

The test file was not found at the three older pinned tags through the repository contents API, so it is recorded only as a current-main observation, not as a historical change.

| Current-main evidence | Git blob SHA | Interpretation |
|---|---|---|
| `tests/vm_test_code_signing.c` | `c728d9325e4d897c40c5bbc6f29900841bddea4a` | T8010 appears in PMAP_CS default-policy test logic only |
| `osfmk/arm64/cpu.c` | `b58e288185b247a95815a1624190e173254ce491` | Selected CPU source contains a T6000 conditional, not a T8010 conditional |

## Follow-up: later public XNU 10002 tags

To check whether the public T8010 machine profile reappeared in a later XNU source generation, the same build-selection files were inspected at four published tags in `apple-oss-distributions/xnu`. The exact historical `pexpert/pexpert/arm64/H9.h` path was also checked at each ref.

| Public tag | Tag date | Resolved commit | T8010 board block in `board_config.h` | T8010 in normal ARM64 allowlist | `H9.h` at historical path |
|---|---|---|---|---|---|
| `xnu-10002.1.13` | 2023-09-26 | `1031c584a5e37aff177559b9f69dbd3c8c3fd30a` | Absent | Absent | Not found |
| `xnu-10002.41.9` | 2023-11-01 | `699cd48037512bf4380799317ca44ca453c82f57` | Absent | Absent | Not found |
| `xnu-10002.61.3` | 2023-12-15 | `0f4c859e951fba394238ab619495c4e1d54d0f34` | Absent | Absent | Not found |
| `xnu-10002.81.5` | 2024-01-31 | `5e3eaea39dcf651e66cb99ba7d70e32cc4a99587` | Absent | Absent | Not found |

All four `MakeInc.def` snapshots list the same normal ARM64 machine set:
`BCM2837 T6000 T8101 T8103 VMAPPLE`. None contains a T8010 machine flag.
The first tag has its own `board_config.h` blob; the last three tags have
identical blob hashes for both inspected files, so the repeated result is not
four independent source-file revisions.

| Tag | `board_config.h` blob SHA | `MakeInc.def` blob SHA |
|---|---|---|
| `xnu-10002.1.13` | `d0670940fb14fe976fe56c9f68d70465a294bfea` | `99f65e14c88262163ce16048d79a974b67996326` |
| `xnu-10002.41.9` | `cd5e4f8bd47b98cbb0def1e1f5fcd9f96b0fc498` | `50eb4ec248859aca3664cca05e6a37714812a222` |
| `xnu-10002.61.3` | `cd5e4f8bd47b98cbb0def1e1f5fcd9f96b0fc498` | `50eb4ec248859aca3664cca05e6a37714812a222` |
| `xnu-10002.81.5` | `cd5e4f8bd47b98cbb0def1e1f5fcd9f96b0fc498` | `50eb4ec248859aca3664cca05e6a37714812a222` |

Direct source links:
- [10002.1.13 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-10002.1.13/pexpert/pexpert/arm64/board_config.h) · [MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-10002.1.13/makedefs/MakeInc.def)
- [10002.41.9 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-10002.41.9/pexpert/pexpert/arm64/board_config.h) · [MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-10002.41.9/makedefs/MakeInc.def)
- [10002.61.3 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-10002.61.3/pexpert/pexpert/arm64/board_config.h) · [MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-10002.61.3/makedefs/MakeInc.def)
- [10002.81.5 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-10002.81.5/pexpert/pexpert/arm64/board_config.h) · [MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-10002.81.5/makedefs/MakeInc.def)

This extends the public-source observation: T8010 is absent from the two
audited build-selection files not only in the inspected 8019/8796 snapshots
and current main, but also in these four later 10002 tags. The scope remains
strictly bounded to those two files and the exact historical H9 header path.
It is **not** a full-tree search, does not rule out T8010 strings or
product-specific configuration elsewhere, and does not recover Apple's
private/product build inputs. It does not establish source-to-binary
provenance, a build, ABI compatibility, hardware support, or runtime behavior.

## Reproducibility

Files read directly from `apple-oss-distributions/xnu`:

| Ref | File | Git blob SHA |
|---|---|---|
| 7195.121.3 | `pexpert/pexpert/arm64/board_config.h` | `0990f9885ea9adb9ca453e3a57241f0d0155fa78` |
| 7195.121.3 | `makedefs/MakeInc.def` | `bf2b6f8a805da4a8abce2590a118dea390ca9f7d` |
| 8019.80.24 | `pexpert/pexpert/arm64/board_config.h` | `259962b3430420e9b90222b4a42282eb6c623209` |
| 8019.80.24 | `makedefs/MakeInc.def` | `3a15620d70d85af974fd296c9e87666a5867f1ff` |
| 8796.141.3 | `pexpert/pexpert/arm64/board_config.h` | `945453413cd8f055449a654639fbea6a083e74cc` |
| 8796.141.3 | `makedefs/MakeInc.def` | `5bd6f23dd10c3316ba0ac3ca5a1515256753975e` |
| current main | `pexpert/pexpert/arm64/board_config.h` | `159356da70e354cb4affbf7951c02aa2ab8c87e1` |
| current main | `makedefs/MakeInc.def` | `cccb411ec9b9fa0d842cc6bbcb02b6e1b7e0355f` |

## Related Qualcomm comparison

The `ios-sweet` Redmi Note 10 Pro port is a distinct Qualcomm platform project. Its README and engineering notes describe custom SWEET platform work and hardware-specific adaptations; this is not evidence that Android itself makes XNU compatible or that T8010 support is unnecessary. See the upstream [README](https://github.com/dipa-studio/ios-sweet) and [NOTES](https://github.com/dipa-studio/ios-sweet/blob/main/NOTES.md).

## Project status

- Hardware target: iPhone9,1 / D10AP / T8010.
- Intended donor userland reference: iPhone10,3 / D22AP / iOS 16.7.16 / 20H392.
- Pinned public XNU baseline: 8796.141.3; T8010 board profile absent.
- Historical public T8010 profile: 7195.121.3.
- First SpringBoard milestone: not reached; M7 has not started.
- Physical iPhone 7 remains on iOS 12.1.4. No device, firmware, partition, security or boot state was changed.
