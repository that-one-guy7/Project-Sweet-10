# iPhone9,1 / 19H422 target BuildManifest audit

## Source and identity

This audit parses the repository's current `main:BuildManifest.plist`.

- Repository path: `BuildManifest.plist`
- Git blob SHA: `1a00587e7bcf3208a95ae160d5d19099953b27fe` (Git object identifier; not an IPSW archive SHA-256)
- Product version: `15.8.8`
- Product build: `19H422`
- Supported product types: `iPhone9,1`, `iPhone9,3`
- BuildIdentity entries: 4

The manifest is a target-build manifest, not the previously reviewed 20H392 iPhone X donor manifest.

## Correct identity selection

| Identity index (zero-based) | DeviceClass | Board ID | Chip ID | Variant | RestoreBehavior | Sweet-10 relevance |
|---:|---|---|---|---|---|---|
| 0 | `d101ap` | `0x0C` | `0x8010` | Customer Erase Install (IPSW) | Erase | iPhone9,3 sibling |
| **1** | **`d10ap`** | **`0x08`** | **`0x8010`** | Customer Erase Install (IPSW) | Erase | **Exact iPhone9,1 target** |
| 2 | `d101ap` | `0x0C` | `0x8010` | Customer Upgrade Install (IPSW) | Update | iPhone9,3 sibling |
| **3** | **`d10ap`** | **`0x08`** | **`0x8010`** | Customer Upgrade Install (IPSW) | Update | **Exact iPhone9,1 target** |

The target product type is `iPhone9,1`, corresponding to the `d10ap` identity. Entries 1 and 3 are the correct board-specific records. Entries 0 and 2 are the `d101ap` sibling identity and must not be used for target DeviceTree or SEP selection.

## Target component records

Both iPhone9,1 identities (1 and 3) declare the same OS image and KernelCache path. Their DeviceTree and SEP payload paths are the `d10ap` variants.

| Manifest key | Identity 1/3 path | Notes |
|---|---|---|
| `OS` | `098-68844-067.dmg` | Same path and digest in both iPhone9,1 identities |
| `KernelCache` | `kernelcache.release.iphone9` | Same path and digest in all four identities |
| `DeviceTree` | `Firmware/all_flash/DeviceTree.d10ap.im4p` | Exact target board tree |
| `SystemVolume` | `Firmware/098-68844-067.dmg.root_hash` | Separate root-hash metadata payload |
| `Ap,SystemVolumeCanonicalMetadata` | `Firmware/098-68844-067.dmg.mtree` | Separate filesystem canonical-metadata payload |
| `StaticTrustCache` | `Firmware/098-68844-067.dmg.trustcache` | Trust-cache payload associated with OS DMG |
| `RestoreRamDisk` | Identity 1: `098-68700-067.dmg`; identity 3: `098-68739-067.dmg` | Erase and Update variants differ |
| `SEP` | `Firmware/all_flash/sep-firmware.d10.RELEASE.im4p` | Exact target board variant |
| `AOP` | `Firmware/AOP/aopfw-t8010aop.im4p` | T8010-labelled AOP firmware component |
| `AVE` | `Firmware/ave/AppleAVE2FW_H9.im4p` | H9-labelled AVE component |

The OS image declares `HashMethod=sha2-384`. The BuildManifest's `Digest` values are preserved as Base64 in the companion JSON. This document does not reinterpret those values as ordinary file SHA-256 hashes. The manifest's `Trusted` property is recorded as metadata, not re-verified by this audit.

The `MinimumSystemPartition` value is 7260 and `OSVarContentSize` is 268353536 in the identity metadata. They are recorded values, not a measurement of the current mounted image or a recommendation to resize anything.

## Volume-layout conclusion: what is and is not proven

The target BuildManifest's four BuildIdentity component dictionaries include an `OS` component whose path is `098-68844-067.dmg`. The target build's repository manifest does not contain a BuildIdentity component key named `Cryptex1,SystemOS` or `SystemOS`.

This is narrower than saying the complete IPSW archive contains no supplementary system image: BuildManifest component records are not a full archive listing. The manifest itself does, however, give a direct target-specific OS filesystem image to associate with the existing mount and target cache research.

Project notes already identify the local target mount path as `$HOME/19H422-full-fs-mount`, with the filesystem hierarchy under its child `root/`; the dyld cache path previously used is:
```
$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64
```
The new manifest audit connects that existing mount to the target's declared `OS` component, subject to the user's existing extraction/mount provenance. It does not prove the full APFS volume/snapshot topology or rule out other supplementary archive members.

## Online source cross-check

The current public `ipsw` implementation's dyld extraction path chooses a `SystemOS` DMG when one is declared; if the lookup returns `ErrorCryptexNotFound`, it falls back to the filesystem OS DMG. This behavior is visible in `dmgPathForDscStep` in [blacktop/ipsw `pkg/dyld/extract.go`](https://github.com/blacktop/ipsw/blob/master/pkg/dyld/extract.go). Its public CLI docs distinguish `ipsw mount fs` (filesystem DMG) from `ipsw mount sys` (SystemOS DMG), and note the SystemOS selector when multiple such images exist.

The `ipsw` dyld guide says that on macOS 12+/iOS 15+ caches use PrebuiltLoaderSets rather than the older prebuilt-loader metadata form. Apple's shared-cache layout documentation explains that the cache builder copies dylib segments into cache mappings. These sources support keeping the OS filesystem inventory and the dyld shared-cache image inventory as separate evidence collections.

**Version caveat:** the online source links above track the current public `ipsw` source/docs and Apple's current published dyld documentation. They are not claimed to be the exact source snapshot for the project's pinned IPSW 3.1.749 binary or the dyld binary shipped in 19H422. No command change is proposed based solely on current-main documentation.

Sources:
- [ipsw dyld extraction implementation](https://github.com/blacktop/ipsw/blob/master/pkg/dyld/extract.go), specifically `dmgPathForDscStep`.
- [ipsw mount documentation](https://blacktop.github.io/ipsw/docs/cli/ipsw/mount/).
- [ipsw dyld guide](https://blacktop.github.io/ipsw/docs/guides/dyld/).
- [Apple dyld shared-cache layout](https://github.com/apple-oss-distributions/dyld/blob/main/doc/CacheLayout.md).

## Next static research action

The next useful operation is a read-only, recursive basename inventory of the selected GUI framework candidates under the already-mounted target OS root, reporting all matching paths and not following symlinks. It should also record any unreadable directories so a partial walk cannot be misreported as complete absence. This expands the prior exact-path probe without assuming the donor's separate SystemOS/Cryptex layout applies to 19H422.

M6 remains in progress; M7/SpringBoard has not started. The physical iPhone 7 remains on iOS 12.1.4. No device, firmware, partition, security, or boot state was accessed or changed.
