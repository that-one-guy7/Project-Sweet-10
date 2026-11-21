# T8010 XNU source-version options for Project Sweet-10

## Question

Would selecting a different XNU/iOS generation fix the missing T8010 board configuration in the pinned public `xnu-8796.141.3` baseline, and why did the Qualcomm-based `ios-sweet` port reach SpringBoard?

## Short conclusion

The missing `ARM64_BOARD_CONFIG_T8010` in the pinned `xnu-8796.141.3` tree is revision-specific, not a permanent limitation of public XNU. The older audited `xnu-7195.121.3` tree contains the T8010/H9 profile, and the current public XNU `main` branch again contains both the T8010 board block and an ARM64 machine allowlist entry for T8010.

That does **not** mean the current `main` kernel can be paired directly with iOS 16.7.16 userland. Kernel source revision, kernel build configuration, shipped-kernel identity, and userspace ABI are separate compatibility questions.

## Source evidence matrix

| Source / binary reference | T8010 evidence | Interpretation |
|---|---|---|
| Public `xnu-7195.121.3` | Historical T8010/H9 profile present in audited source | Useful historical source reference; substantially older than iOS 16 |
| Public `xnu-8019.80.24` | T8010 profile absent in audited ARM64 machine/board paths | Public source gap; not proof that Apple’s private build inputs lacked it |
| Pinned public `xnu-8796.141.3` | T8010 profile absent from audited ARM64 machine allowlist and `board_config.h` | Blocks a stock T8010 configuration using this exact public tree |
| iPhone9,1 19H422 shipped KernelCache | Reports `8020.241.44~1 / RELEASE_ARM64_T8010` | Confirms Apple shipped an iOS 15-generation T8010 kernel for this device; does not supply its complete corresponding source tree |
| Current public XNU `main` | `makedefs/MakeInc.def` lists T8010 in `SUPPORTED_ARM64_MACHINE_CONFIGS`; `board_config.h` has `ARM64_BOARD_CONFIG_T8010` including `H9.h` | Proves the T8010 profile exists in a later public source revision; not proof of iOS 16 userland compatibility |

Current public source references:
- [XNU current ARM64 board configuration](https://github.com/apple-oss-distributions/xnu/blob/main/pexpert/pexpert/arm64/board_config.h), T8010 block and H9 include.
- [XNU current build machine allowlist](https://github.com/apple-oss-distributions/xnu/blob/main/makedefs/MakeInc.def), `SUPPORTED_ARM64_MACHINE_CONFIGS` and `MACHINE_FLAGS_ARM64_T8010`.
- [Pinned XNU 8796.141.3 board configuration](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/board_config.h).
- [Historical XNU 7195.121.3 board configuration](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/board_config.h).

## Would a different iOS version fix it?

There are three different choices, with different outcomes:

### 1. Use a native iPhone 7 iOS 15 kernel and matching iOS 15 userland

This is the generation Apple shipped for iPhone9,1: the project’s 19H422 BuildManifest identifies iPhone9,1 / d10ap, and the target KernelCache is recorded as `RELEASE_ARM64_T8010`. A fully matched iOS 15 stack is a much less speculative compatibility target for this hardware.

However, this is no longer the project’s original goal of running the iPhone X’s iOS 16.7.16 (20H392) userland on iPhone7. It is a different project target. No change to the user’s physical phone is proposed.

### 2. Keep iOS 16.7.16 userland and use an older T8010-capable XNU

This may make the T8010 board definition easier to source, but it introduces a major kernel/userspace generation mismatch. Kernel interfaces, IOKit/KPI expectations, platform services, and private userland assumptions must be checked; a board macro from an older tree is not a compatibility bridge by itself.

### 3. Keep the XNU 8796 / 20H392 goal and use other XNU revisions as source references

This preserves the intended iOS 16 generation. The historical 7195 T8010/H9 implementation and current public `main` T8010 block are possible source references for a carefully reviewed forward-port. The actual patch would still need to be checked against the 8796 kernel interfaces and target-specific 19H422 hardware evidence. The public 19H422 KernelCache’s T8010 version stamp provides a useful target-era comparison, but does not reveal Apple’s complete private source inputs.

**Recommended research direction:** do not switch the userland target yet. Keep 20H392 as the explicit experimental target, and perform a source-level T8010 profile comparison across 7195, 8796, and current public XNU main. Decide whether the missing profile is a bounded configuration gap or whether required platform code and interfaces changed enough that a larger port is needed. Do not infer compatibility from one macro/header.

## Why the Qualcomm Android-device port reached SpringBoard

The reference is not “iOS running on top of Android”. The Redmi Note 10 Pro (`sweet`) is Qualcomm SM7150 / Snapdragon 732G hardware. The project replaces the Android kernel/userland path with a custom XNU port and iOS userland. It keeps a stock device bootloader as the first-stage loader, then uses its own shim, generated Apple Device Tree, custom XNU patches, platform drivers and an iPhone X 20H392 root filesystem.

The upstream README describes this architecture and reports six of eight CPU cores, Qualcomm GICv3 interrupts/timers, a custom UFS host driver, software rendering, touch input, and SpringBoard on that hardware. It does not reuse Apple's T8010 board profile because it is a different SoC; it adds its own `SWEET` machine configuration and Qualcomm-specific adaptations.

The same project's notes show it had to adapt:
- XNU's VMAPPLE timer path to the Qualcomm GICv3 interrupt group/IRQ arrangement.
- XNU's VMAPPLE PSCI call from `hvc` to Qualcomm's `smc`.
- CPU feature/compiler assumptions for Qualcomm Kryo.
- Boot memory-map and device-tree data for the Qualcomm platform.

The port's README also explicitly lists major missing features: Wi-Fi, Bluetooth, cellular, audio, camera, sensors, GPS, SEP/Face ID and GPU support; some daemons crash/relaunch, and the project describes its security model as mostly switched off. Therefore, it is not evidence that porting to a non-Apple Android device is easy or that the same issues are absent.

References:
- [ios-sweet README](https://github.com/dipa-studio/ios-sweet), device, architecture, working-state and limitation tables.
- [ios-sweet engineering notes](https://github.com/dipa-studio/ios-sweet/blob/main/NOTES.md), XNU timer, PSCI, CPU, MMU and platform adaptation notes.

## What the latest 19H422 framework scan adds

The recursive scan under the mounted 19H422 OS root visited 104,017 directories and 382,833 entries with no reported walk or stat errors. It found only the `ExtensionFoundation.framework` directory name under PrivateFrameworks, not the `ExtensionFoundation` executable. Sixteen other selected 20H392 GUI framework binary/bundle names had no match in that tree.

These are userland filesystem inventory findings, not evidence about the T8010 XNU board profile. They help explain why the iOS 16 donor's GUI framework dependencies do not map one-to-one onto the stock iOS 15.8.8 target filesystem.

## Project decision

- Keep target hardware: iPhone9,1 / D10AP / T8010.
- Keep userland research reference: iPhone10,3 / D22AP / iOS 16.7.16 / 20H392.
- Keep the source lock for XNU 8796 as the current-generation baseline, but do not call it target-ready.
- Add a distinct T8010 source-reference comparison before writing platform implementation.
- Keep static metadata, source configuration, build result, and physical runtime evidence as separate proof levels.

The physical iPhone 7 remains on iOS 12.1.4. No device, firmware, partition, security, or boot state was changed.
