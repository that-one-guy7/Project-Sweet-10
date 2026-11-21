# Independent UniXNU cross-check of the iOS 16.7.16 XNU baseline

## Scope

This note records a read-only cross-project comparison of the same iPhone X
20H392 donor KernelCache already inventoried by Project Sweet-10. It asks
whether another public port independently pins that exact artifact alongside
the same public XNU source candidate, and what its validation report actually
proves.

The external port is OnePlus 13 CPH2653 / SM8750. It is not an iPhone 7,
A10/T8010, or Apple T8015 target. No code, binary, configuration, or device
state was copied or changed.

## Exact source and donor-artifact cross-check

The pinned external device-port snapshot is
[`lihenggui/UniXNU_dodge_SM8750` at
`6a527866e43734680f3b92ec7445d3d518ca70cd`](https://github.com/lihenggui/UniXNU_dodge_SM8750/tree/6a527866e43734680f3b92ec7445d3d518ca70cd).
Its iOS profile
[`profiles/os/ios-16.7.16-20H392/profile.toml`](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/6a527866e43734680f3b92ec7445d3d518ca70cd/profiles/os/ios-16.7.16-20H392/profile.toml)
records:

| Profile field | Recorded value |
|---|---|
| Userland reference | iOS 16.7.16 / 20H392 |
| Donor product | iPhone10,3 |
| Donor device class | D22AP |
| Darwin version | 22.6.0 |
| Public XNU tag | `xnu-8796.141.3` |
| Public XNU commit | `1b191cb58250d0705d8a51287127505aa4bc0789` |
| `[kernel.prelink].kernelcache_sha256` | `2ec297bac95bcba01046fd0148e97e7e5885c05a6c18827f39f534ba375c1221` |

The SHA-256 value is identical to the extracted iPhone10,3 / 20H392 donor
KernelCache already recorded in
[Project Sweet-10's donor/target comparison](20h392-19h422-multitouch-kernelcache-comparison.md).
This is a useful independent downstream co-pin: the same donor artifact
digest and the same XNU tag/commit appear together in another project's
profile.

It is not an Apple source-to-binary attestation. The profile is authored by
the downstream project, not published as an Apple build manifest. It shows
how that project chose to pair its source baseline and prelink input; it
does not reveal Apple's exact internal source commit or private build inputs.

## What the patch report validates

The matching immutable report is
[`reports/public/ios16-rebased-patches.json`](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/6a527866e43734680f3b92ec7445d3d518ca70cd/reports/public/ios16-rebased-patches.json).
It records:

- Result: `PASS`.
- Baseline tag: `xnu-8796.141.3`.
- Baseline revision: `1b191cb58250d0705d8a51287127505aa4bc0789`.
- Rebased patch count: 62.
- Scope: strict ordered application on a clean pinned source.
- Explicit exclusions: compilation, binary ABI, and hardware validation are separate.

The report therefore establishes a patch-application check only. It does not
establish that the patched source compiled, that a resulting kernel matches
the donor kernel ABI, or that it works on any physical board. The external
device record also identifies the work as a OnePlus 13 / SM8750 port.

## Four XNU-specific profile patches

The external iOS profile includes four patches under
`profiles/os/ios-16.7.16-20H392/patches/xnu/`:

| Patch | Bounded source-level purpose |
|---|---|
| `xnu-8796.141.3-security-init.patch` | Adds a profile-specific early security-initializer hook to the native-prelink path |
| `xnu-8796.141.3-sparse-index.patch` | Extends the kalloc type-view parser to consume the profile's sparse prelink component index |
| `xnu-8796.141.3-typed-delete-and-uio-alignment.patch` | Adjusts typed-pointer compatibility and explicit alignment of UIO stack buffers |
| `xnu-8796.141.3-vfs-getvfs-with-vfsops.patch` | Backports `vfs_getvfs_with_vfsops` from public XNU 10063.141.1 and adds the symbol to `BSDKernel.exports`; this is a downstream root-stack adaptation, not proof that public XNU 8796 has an Apple-side missing-symbol defect |

These are adaptations for that project's source, toolchain, prelink, and root
integration. Their presence is not proof that Apple omitted the same logic
from its internal 20H392 source, and they are not an A10/T8010 patch recipe.
In particular, the VFS helper is a project-specific extension recorded by
that port; it must not be generalized into an Apple kernel ABI requirement
without separate evidence.

## Important build-configuration boundary

The profile's candidate kernel output path is:

`build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped`

That is not `RELEASE_ARM64_T8015` and is not an iPhone9,1/T8010 build.
The profile uses the original iPhone X KernelCache as a prelink input while
building a separate downstream kernel for its own platform. The path is
recorded to prevent this result from being mistaken for a T8015 or T8010
configuration.

The profile also records a separate `trustcache_tag` of
`xnu-8796.101.5`; that input is not the XNU source tag or commit for the
kernel baseline.

## Conclusions for Project Sweet-10

1. Retain `xnu-8796.141.3` /
   `1b191cb58250d0705d8a51287127505aa4bc0789` as the public source-review
   candidate. An independent downstream port co-pins that revision with the
   exact donor KernelCache digest already recorded by Sweet-10.
2. Keep G1 open. This is downstream profile corroboration, not an Apple
   source-to-binary record or disclosure of product-specific source inputs.
3. Treat the 62-patch report as clean patch-application evidence only. It
   does not validate compilation, ABI, or hardware behavior.
4. Do not import the four external patches wholesale. Their functions are
   tied to the other project's prelink/root design and compiler choices.
5. Do not infer T8010 support from the profile. Its platform is SM8750 and
   its candidate kernel path uses `DEVELOPMENT_ARM64_BCM2837`, not a
   T8010/T8015 machine target.

The physical iPhone 7 remains on iOS 12.1.4. SpringBoard has not been reached
on iPhone9,1, and no successful iOS 16 boot is claimed.

## References

- [UniXNU main device record for dodge](https://github.com/UniXNU/UniXNU/blob/8542980d02b4d2cc5c32ee3542de1760b2562aac/docs/devices/dodge.md)
- [Exact downstream 20H392 profile](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/6a527866e43734680f3b92ec7445d3d518ca70cd/profiles/os/ios-16.7.16-20H392/profile.toml)
- [Strict patch-application report](https://github.com/lihenggui/UniXNU_dodge_SM8750/blob/6a527866e43734680f3b92ec7445d3d518ca70cd/reports/public/ios16-rebased-patches.json)
- [Project Sweet-10 baseline lock](../xnu/BASELINE.lock.json)
- [Project Sweet-10 kernel readiness gate](kernel-implementation-readiness.md)

This is documentation and static-source research only. No device operation,
firmware change, partition change, kernel build, or boot attempt was performed.
