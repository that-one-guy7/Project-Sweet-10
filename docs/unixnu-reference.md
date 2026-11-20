# UniXNU architecture and profile research reference

## Scope

This is a source/documentation review of [UniXNU/UniXNU](https://github.com/UniXNU/UniXNU), reviewed at repository revision `8542980d02b4d2cc5c32ee3542de1760b2562aac` (2026-11-19). It records architectural and evidence-management practices that may inform Project Sweet-10. It does not copy code, firmware, device constants, boot instructions, or target-specific payload data.

Primary upstream references:
- [UniXNU README](https://github.com/UniXNU/UniXNU/blob/8542980d02b4d2cc5c32ee3542de1760b2562aac/README.md)
- [UniXNU architecture overview](https://unixnu.com/porting/)
- [UniXNU build documentation](https://github.com/UniXNU/UniXNU/blob/8542980d02b4d2cc5c32ee3542de1760b2562aac/docs/building.md)
- [UniXNU requirements](https://unixnu.com/guide/requirements)
- [Xiaomi 13 Pro (nuwa) device record](https://github.com/UniXNU/UniXNU/blob/8542980d02b4d2cc5c32ee3542de1760b2562aac/docs/devices/nuwa.md)
- [OnePlus 6 (enchilada) device record](https://github.com/UniXNU/UniXNU/blob/8542980d02b4d2cc5c32ee3542de1760b2562aac/docs/devices/enchilada-dragon120820.md)

## Architecture lessons

UniXNU documents a six-layer design: boot image, UEFI firmware, boot manager, XNU loader, kernel, and userland. It assigns common ARM64/build functionality to the shared project, reusable platform functionality to SoC-level repositories, and board configuration/integration to device repositories.

Useful project-management lessons for Sweet-10:

1. Keep generic ARM64 source analysis separate from SoC-specific and board-specific evidence.
2. Track the loader-to-kernel handoff as its own contract rather than treating a working kernel build as proof of a working boot path.
3. Treat userland selection, kernel source, kernelcache/prelink inputs, device tree, and hardware support as distinct compatibility gates.
4. Pin every source dependency and record the effective source revision and configuration in build reports.
5. Keep each board's status separate; a milestone on one device must not be attributed to another device using the same OS profile.

## 20H392 profile evidence and XNU candidate

The UniXNU `nuwa` device record says its locally authored `ios-16.7.16-20H392` profile uses:
- XNU tag `xnu-8796.141.3`;
- source commit `1b191cb58250d0705d8a51287127505aa4bc0789`;
- donor device class `d22ap` (iPhone X);
- BuildManifest-derived device-tree and trust-cache hashes; and
- a kernelcache hash and prelink-root inventory.

That source commit matches Project Sweet-10's existing candidate pin. This is useful independent corroboration that the candidate is relevant to an iPhone X 20H392 profile.

**Evidence limitation:** this is a downstream project's profile report, not an Apple-published build-to-source mapping. The profile was authored locally; UniXNU's reviewed upstream OS-profile tree does not itself ship that iOS 16 profile. A separate device-port record notes that its local 20H392 profile did not yet have a kernelcache hash pinned. Therefore, profile completeness and donor-image identity must be checked per port; do not turn one downstream report into a universal claim about every 20H392 image.

## Portability boundary

UniXNU is designed around a UEFI environment for non-Apple ARM64 hardware. Its public device records describe Android-based Qualcomm and other non-Apple platforms. Its architecture is useful as a comparison for separation of responsibilities, reproducibility, and evidence tracking; its UEFI integration, SoC support, device trees, drivers, memory maps, and board configuration are not iPhone 7 A10 implementation evidence.

The reviewed UniXNU repository search did not return an `iPhone9,1`, `T8010`, or A10 target record. This is a bounded search result, not proof that no related work exists elsewhere.

## Project decision

- Retain `xnu-8796.141.3` / `1b191cb58250d0705d8a51287127505aa4bc0789` as the source-review candidate.
- Upgrade its evidence label from "only a family-based candidate" to "corroborated by a downstream iPhone X 20H392 profile report; Apple-side mapping still not independently verified."
- Keep the exact donor image, BuildManifest identity, kernelcache hash, and XNU revision linked in one evidence record before claiming an exact match.
- Do not copy UniXNU's UEFI, Qualcomm, or board-specific implementation into Sweet-10.

This is a documentation-only review. No device interaction, firmware modification, boot attempt, partition write, or proprietary binary was used.
