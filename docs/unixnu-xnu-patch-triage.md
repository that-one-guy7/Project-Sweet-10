# Static triage of the downstream UniXNU Darwin 22 XNU patches

## Scope and pinned source

This note reviews the four XNU-specific patches in the immutable UniXNU
OnePlus 13 / SM8750 port snapshot
[`6a527866e43734680f3b92ec7445d3d518ca70cd`](https://github.com/lihenggui/UniXNU_dodge_SM8750/tree/6a527866e43734680f3b92ec7445d3d518ca70cd),
under its iOS 16.7.16 / 20H392 profile. The profile pairs public
`xnu-8796.141.3` / commit
`1b191cb58250d0705d8a51287127505aa4bc0789` with the iPhone10,3 donor
KernelCache digest already recorded by Project Sweet-10.

This is a static review of patch intent and touched interfaces. The external
report says the ordered patch series applies to a clean pinned source tree;
that is patch-application evidence, not a build, ABI, or runtime result.
No patch was applied to Sweet-10 and no source, kernel, firmware, or device
state was modified.

## Patch-by-patch findings

| Patch | Files / interface area | What the diff changes | Sweet-10 relevance |
|---|---|---|---|
| `security-init` | `libkern/c++/OSKext.cpp`, native-prelink kext start path | Adds a profile-specific early initializer hook associated with an explicitly linked security component and the MACF initialization phase. It validates the prelink property and target address before invoking the component initializer. | Not a general T8010 fix. It changes security initialization ordering and assumes the external port's native-prelink metadata and component contract. Do not transplant without independent evidence of the same prelink format, security component, and required initialization order. |
| `sparse-index` | `osfmk/kern/kalloc.c`, kalloc type-view parser | Adds support for a `__macho_list` index of sparse prelinked component headers while retaining the existing contiguous-layout path when no index is present. The new path adds bounds, ordering, alignment, and Mach-O load-command checks. | A prelink-layout compatibility change, not a CPU/board implementation. It is relevant only if Sweet-10 independently establishes that its selected prelink contains this sparse index and that the stock parser cannot consume it. |
| `typed-delete-and-uio-alignment` | BSD VFS, UIO, NFS, socket and file-I/O sources | Changes the `uio_stackbuf_t` typedef to a byte-sized type and applies explicit `_Alignas(union iovecs)` at stack-buffer declarations. The patch description also mentions typed-pointer checks and C/ASM feature flags; the reviewed diff's visible changes are the UIO alignment edits. | Primarily compiler/layout compatibility. It is not evidence of an A10 issue. Any consideration would require identifying the exact compiler diagnostic or layout failure in a reproducible baseline and auditing every affected declaration. |
| `vfs-getvfs-with-vfsops` | `bsd/sys/mount.h`, `bsd/vfs/vfs_subr.c`, `config/BSDKernel.exports` | Adds an exported filesystem lookup helper that checks the found mount's operations table against the caller's expected table. The patch identifies the implementation as a backport from public XNU `10063.141.1`. | A downstream VFS/root-stack interface extension. It is not an A10 board feature and does not establish that Apple 20H392's private source lacked this helper. |

## Interpretation

The four patches fall into three distinct classes:

1. **Prelink representation and lifecycle:** the security initializer and
   sparse-index patches depend on the downstream port's native-prelink
   arrangement. They should be evaluated only against independently
   established prelink metadata and component requirements.
2. **Toolchain and data-layout adaptation:** the UIO patch changes how stack
   buffers are aligned. Its necessity is compiler- and source-context
   dependent, not a board-support signal.
3. **Root/VFS integration:** the VFS helper extends an interface used by that
   downstream root stack. Its presence is not evidence of an upstream Apple
   defect or an iPhone kernel requirement.

None of the four patches adds a T8010 machine profile, H9 CPU description,
A10 interrupt/timer implementation, iPhone9,1 device-tree contract, or
Apple-specific peripheral driver. They therefore do not close the missing
T8010 support gap in public XNU 8796.

The external profile's candidate kernel output path remains
`DEVELOPMENT_ARM64_BCM2837`, not `RELEASE_ARM64_T8015` or a T8010
configuration. The 62-patch clean-application report must not be described as
a successful kernel build or hardware validation.

## Decision for Project Sweet-10

- Keep all four patches as **reference material only**.
- Do not copy them into the Sweet-10 baseline or treat them as an iPhone 7
  patch recipe.
- If a future source investigation identifies one of these exact interfaces
  as a blocker, first record the matching upstream source behavior, the
  downstream dependency that requires it, and a minimal host-side test.
- Keep G1 open: the exact Apple source revision and product-specific build
  inputs for the 20H392 donor are still unknown.
- Keep G2 open: the historical T8010/H9 implementation's full dependency and
  migration graph remains incomplete.
- Keep G3 open: no reproducible unmodified iPhoneOS ARM64 baseline build has
  been established.

The physical iPhone 7 remains on iOS 12.1.4. SpringBoard has not been reached,
and no successful iOS 16 iPhone9,1 boot is claimed.

## Immutable references

- [Downstream profile snapshot](https://github.com/lihenggui/UniXNU_dodge_SM8750/tree/6a527866e43734680f3b92ec7445d3d518ca70cd/profiles/os/ios-16.7.16-20H392)
- [Security-init patch](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/6a527866e43734680f3b92ec7445d3d518ca70cd/profiles/os/ios-16.7.16-20H392/patches/xnu/xnu-8796.141.3-security-init.patch)
- [Sparse-index patch](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/6a527866e43734680f3b92ec7445d3d518ca70cd/profiles/os/ios-16.7.16-20H392/patches/xnu/xnu-8796.141.3-sparse-index.patch)
- [Typed-delete and UIO-alignment patch](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/6a527866e43734680f3b92ec7445d3d518ca70cd/profiles/os/ios-16.7.16-20H392/patches/xnu/xnu-8796.141.3-typed-delete-and-uio-alignment.patch)
- [VFS helper patch](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/6a527866e43734680f3b92ec7445d3d518ca70cd/profiles/os/ios-16.7.16-20H392/patches/xnu/xnu-8796.141.3-vfs-getvfs-with-vfsops.patch)
- [Strict 62-patch application report](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/6a527866e43734680f3b92ec7445d3d518ca70cd/reports/public/ios16-rebased-patches.json)
- [Project Sweet-10 UniXNU baseline cross-check](unixnu-20h392-xnu-baseline-crosscheck.md)

This document is static source research only. It does not provide device
boot, exploit, firmware installation, partition modification, or recovery
instructions.
