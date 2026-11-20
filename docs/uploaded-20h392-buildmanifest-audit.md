# Uploaded 20H392 BuildManifest audit

## Scope and provenance

This audit records the user-supplied `BuildManifest.plist` inspected on
2026-11-20. The supplied file is a standalone plist, not the complete IPSW
archive. Its SHA-256 is:

`2d1452103a2f5ad71cb78d94454977fc70632472201980a468c247fba14b10b7`

The archive filename, full IPSW size, and full-archive SHA-256 are therefore
not available from this upload. No archive components were extracted or
executed, and no device was connected.

## Manifest-level identity

| Field | Observed value |
|---|---|
| ProductVersion | `16.7.16` |
| ProductBuildVersion | `20H392` |
| ManifestVersion | `0` |
| SupportedProductTypes | `iPhone10,6`, `iPhone10,3` |
| BuildIdentities | 4 |

The product types and device classes identify this as an iPhone X restore
manifest, not an iPhone 7 manifest. The two product types correspond to
device classes `d221ap` and `d22ap` represented in the identity entries.

## BuildIdentity inventory

All four entries report chip ID `0x8015`. Entries 0 and 2 report board ID
`0x0E` and device class `d221ap`; entries 1 and 3 report board ID `0x06`
and device class `d22ap`.

| Index | DeviceClass | ApBoardID | ApChipID | Variant | RestoreBehavior |
|---:|---|---|---|---|---|
| 0 | `d221ap` | `0x0E` | `0x8015` | Customer Erase Install (IPSW) | Erase |
| 1 | `d22ap` | `0x06` | `0x8015` | Customer Erase Install (IPSW) | Erase |
| 2 | `d221ap` | `0x0E` | `0x8015` | Customer Upgrade Install (IPSW) | Update |
| 3 | `d22ap` | `0x06` | `0x8015` | Customer Upgrade Install (IPSW) | Update |

The four entries are two board variants, each represented by erase and
upgrade identities. They are not four separate hardware models.

## KernelCache and DeviceTree metadata

Every identity names the same KernelCache path:

`kernelcache.release.iphone10b`

Every identity also reports the same KernelCache digest:

`64904730143fc2411c6b82c0611379050b15d8402d5403ca38c48eb4a42d3568152d785bf9e2c3797f9113771bf003e3`

The DeviceTree components are board-specific:

| DeviceClass | DeviceTree path | Digest |
|---|---|---|
| `d221ap` | `Firmware/all_flash/DeviceTree.d221ap.im4p` | `32f6aba57a60a5f643e19ebf74e8d579584e166088e0654df2f9be66bc12b53e276576945dcc31c601a35d941617d2ea` |
| `d22ap` | `Firmware/all_flash/DeviceTree.d22ap.im4p` | `e2574f463f5b5bbb45ba8c939e107865c27b4e5d06600cda77bfa033959ca88562045dd389a3a96afd6c9e7bad5dac94` |

The plist does not provide a `Size` field for these KernelCache or DeviceTree
component records. This audit records the values actually present and does
not infer missing sizes.

## Comparison with the project target

The project target remains:

- Product type: `iPhone9,1`
- Board: `D10AP`
- SoC: A10 / T8010
- Chip ID: `0x8010`

The uploaded manifest's supported product types are only `iPhone10,6` and
`iPhone10,3`, and every BuildIdentity reports chip ID `0x8015`. It contains
no `iPhone9,1` / `D10AP` / `0x8010` identity.

**Conclusion:** this is useful evidence for the selected iOS 16.7.16
(`20H392`) userland/reference build and for the iPhone X donor identity. It
is not an iPhone 7 restore manifest. Its KernelCache and DeviceTree must not
be relabeled or treated as iPhone9,1 components.

## What this evidence does not establish

This standalone plist does not establish:

1. That an iPhone9,1 IPSW or iOS 16 restore identity exists.
2. That the iPhone X KernelCache can initialize A10/T8010 hardware.
3. That the pinned Apple XNU source revision maps exactly to this KernelCache.
4. Any iPhone9,1 DeviceTree, board configuration, boot handoff, or platform
   support.
5. A working iOS 16 boot or SpringBoard on iPhone9,1.

The next research step is to keep the iPhone X donor identity separate from
the target and continue source-level investigation of the missing A10/T8010
platform integration. Any further claims must be tied to independently
verified iPhone9,1 evidence. No device-side action is part of this audit.
