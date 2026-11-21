# Userland reference: iOS 16.7.16 (20H392)

## Selected reference
- Version: iOS 16.7.16
- Build: 20H392
- Reference device: iPhone X
- Model identifier used by ios-sweet's root-image instructions: iPhone10,3
- Board identity reported by ios-sweet: D22AP

Apple's developer release listing identifies iOS 16.7.16 as build 20H392 (May 11, 2026). The ios-sweet README explicitly identifies its userland as the unmodified iPhone X iOS 16.7.16 (20H392) userland.

## Important target distinction
Project Sweet-10's hardware target remains iPhone 7, iPhone9,1. Build 20H392 is a reference userland, not an iPhone7 firmware build.

Apple's iOS 16 compatibility list includes iPhone 8 and later, not iPhone 7. This project is therefore an experimental port to an unsupported target, not a normal iOS restore or installation.

## Compatibility areas to investigate
The reference userland has iPhone X identity and interaction assumptions. ios-sweet reports an iPhone X identity and gesture-based navigation without a Home button. The iPhone 7 has a different platform and Home-button/Touch ID hardware. Investigate independently:
- Device identity and MobileGestalt product/board properties.
- SpringBoard layout, Home-button and gesture behavior.
- Touch/HID event semantics and physical button reporting.
- Display dimensions, framebuffer services, and orientation.
- SEP/Touch ID, activation, power, audio, radio, and other services.
- launchd job dependencies and hardware-specific IOKit matching.

This is a research inventory, not an implementation or a claim that these services can be made compatible.

## Extracted donor KernelCache identity

The user subsequently extracted the iPhone10,3 KernelCache from the complete
20H392 IPSW and inspected it with ipsw 3.1.749. The observed identity is:

- Darwin 22.6.0.
- XNU `8796.142.1.703.8~1`.
- Kernel target `RELEASE_ARM64_T8015`.
- SHA-256:
  `2ec297bac95bcba01046fd0148e97e7e5885c05a6c18827f39f534ba375c1221`.

This is an observed iPhone X donor binary identity. The repository's pinned
public XNU candidate `xnu-8796.141.3` is not claimed to be the exact source
revision for this KernelCache; source-to-binary correspondence remains open.

## Source-derived versus unverified
Source-derived: ios-sweet identifies its userland as iPhone X 16.7.16 (20H392), and its device as iPhone X (iPhone10,3 / D22AP).

Still not verified: the exact public XNU source commit corresponding to the extracted 20H392 kernel, and whether the selected public XNU source baseline is build-compatible with that userland.

Do not treat a matching major XNU family number as proof of an exact kernel/userland match.
