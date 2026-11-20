# iOS 16.7.16 (20H392) restore identity audit

## Purpose

This is a read-only identity audit for the selected iOS 16 userland reference,
build `20H392`, and the iPhone 7 research target `iPhone9,1` (board
`D10AP`, SoC `T8010`).

It distinguishes a shared marketing release/build number from the
device-specific restore images and hardware identities. It does not establish
that an iPhone 7 can run this release.

## Findings

### 1. The indexed 20H392 full-restore set contains six iPhone product types

The iOS 16.7.16 firmware index lists six full-restore targets for build
`20H392`:

| Product type | Device family | Board config | SoC / CPID |
|---|---|---|---|
| `iPhone10,1` | iPhone 8 (Global/CDMA) | `D20AP` | A11 / `0x8015` |
| `iPhone10,2` | iPhone 8 Plus (Global/CDMA) | `D21AP` | A11 / `0x8015` |
| `iPhone10,3` | iPhone X (Global/CDMA) | `D22AP` | A11 / `0x8015` |
| `iPhone10,4` | iPhone 8 (GSM) | `D201AP` | A11 / `0x8015` |
| `iPhone10,5` | iPhone 8 Plus (GSM) | `D211AP` | A11 / `0x8015` |
| `iPhone10,6` | iPhone X (GSM) | `D221AP` | A11 / `0x8015` |

The product-type list is reported by the iOS 16.7.16 firmware index. Board
configuration and CPID mappings are cross-checked against the device lookup
and libirecovery's device table. These are third-party reference datasets;
the authoritative final check for a particular image remains its own
BuildManifest and component metadata.

Sources:
- [IPSW Downloads: iOS 16.7.16 restore list](https://ipsw.me/iOS/16.7.16/)
- [Beta Profiles: 20H392 device identifiers](https://betaprofiles.dev/ipsw/ios/16-7-16-20h392/)
- [IPSWDownload model finder: A11 board and CPID mappings](https://ipswdownload.com/tools/model-finder/)
- [libirecovery device identity table](https://cgit.sukimashita.com/libirecovery.git/tree/src/libirecovery.c?id=dc2e4c2628284b1f0cd1cebdd09b1b6c0738a1db)

### 2. iPhone 7 identity is a different hardware family

The device table identifies `iPhone9,1` as iPhone 7 / `d10ap` / T8010
(`0x8010`). The same source lists iPhone 8 and iPhone X product types as
T8015 (`0x8015`). The 20H392 full-restore index lists the six
`iPhone10,x` targets above and does not list `iPhone9,1`.

Sources:
- [blacktop/ipsw device list](https://blacktop.github.io/ipsw/docs/guides/device_list/)
- [libirecovery device identity table](https://cgit.sukimashita.com/libirecovery.git/tree/src/libirecovery.c?id=dc2e4c2628284b1f0cd1cebdd09b1b6c0738a1db)
- [IPSW Downloads: iOS 16.7.16 restore list](https://ipsw.me/iOS/16.7.16/)

This establishes a restore-image identity mismatch between the selected donor
family and the iPhone 7 target. It does not mean the userland cannot be studied
as a reference, but it does mean an iPhone 8/X kernelcache, DeviceTree, or
BuildManifest must not be relabeled as an iPhone 7 artifact.

### 3. Build number equality is not kernel/platform compatibility

A shared marketing version and build number do not collapse distinct
product-type images into one interchangeable firmware. Each restore image has
device-specific manifest entries and components. A valid source mapping must
name the exact product type and component (for example, kernelcache) rather
than infer it from `20H392` alone.

The Linux kernel's Apple T8015 device-tree family also explicitly describes
the iPhone 8 / 8 Plus / X device set as A11 hardware. This is useful
independent corroboration of the T8015 family boundary, not evidence of XNU
support or a transferable iPhone 7 implementation.

Source:
- [Linux: t8015-common.dtsi](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/apple/t8015-common.dtsi)

## What remains unverified

This index-level audit does not unpack or validate a full IPSW. The following
remain open and must not be guessed:

1. The exact `BuildManifest.plist` contents for each donor IPSW.
2. The exact kernelcache component path, digest, and build metadata for the
   selected donor product type.
3. Whether Apple's published XNU source revision maps exactly to that
   kernelcache.
4. Any corresponding iPhone9,1 / T8010 iOS 16 kernel or restore image.
5. Any iPhone9,1 device-tree, board configuration, or boot compatibility.

## Conclusion

**20H392 is a useful iOS 16 userland reference, not an iPhone 7 firmware
identity.** The indexed restore set covers six iPhone 8/X product types
(`iPhone10,1` through `iPhone10,6`), all in the A11/T8015 family. The
iPhone 7 target `iPhone9,1` is T8010 and is not in that indexed restore set.

Keep the project metadata explicit: userland reference = `20H392`;
donor restore product type = must be named per artifact; target hardware =
`iPhone9,1 / D10AP / T8010`. Do not substitute donor kernel or device-tree
artifacts for target-specific evidence.
