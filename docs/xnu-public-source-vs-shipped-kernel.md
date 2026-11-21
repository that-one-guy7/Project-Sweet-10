# Public XNU source versus shipped KernelCache identities

## Purpose

This note cross-checks the public XNU machine-configuration lists against the
build identities already recorded from the iPhone 7 target and iPhone X donor
KernelCaches. It clarifies what the missing T8010 profile in the public
`xnu-8796.141.3` source does and does not establish.

This is read-only source and artifact research. It does not modify a kernel,
create a target configuration, or describe device operations.

## Public-source comparison

The three public XNU tags previously pinned by Project Sweet-10 show this
transition:

| Public XNU tag | Normal ARM64 machine list | T8010 profile in board header | H9 header |
|---|---|---|---|
| `xnu-7195.121.3` | Includes `T8010` | Present; includes `H9.h`, with `MAX_CPUS=3`, one CPU cluster, and `MAX_L2_CLINE=7` | Present |
| `xnu-8019.80.24` | `BCM2837 T6000 T8101 VMAPPLE` | Absent | Absent at historical path |
| `xnu-8796.141.3` | `BCM2837 T6000 T8101 T8103 VMAPPLE` | Absent | Absent at historical path |

In `xnu-7195.121.3`, `makedefs/MakeInc.def` includes T8010 in the normal
ARM64 machine list and maps it to
`-DARM64_BOARD_CONFIG_T8010 -mcpu=hurricane`. The corresponding
`board_config.h` block includes `H9.h`. This is a complete, visible
public-source selection chain for that historical source snapshot.

The later `xnu-8019.80.24` and `xnu-8796.141.3` snapshots omit T8010 from the
normal machine list and do not contain the historical T8010 board block or
H9 header at the audited paths. The selected 8796 source also omits T8015
from its normal ARM64 list and has no T8015 board block in its ARM64
`board_config.h`.

References:
- [XNU 7195.121.3 MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/makedefs/MakeInc.def)
- [XNU 7195.121.3 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/board_config.h)
- [XNU 7195.121.3 H9.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)
- [XNU 8019.80.24 MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-8019.80.24/makedefs/MakeInc.def)
- [XNU 8019.80.24 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8019.80.24/pexpert/pexpert/arm64/board_config.h)
- [XNU 8796.141.3 MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/makedefs/MakeInc.def)
- [XNU 8796.141.3 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/board_config.h)

## What the shipped KernelCaches report

The project has independently inspected two existing KernelCaches:

| Field | iPhone 7 target, 19H422 | iPhone X donor, 20H392 |
|---|---|---|
| Hardware identity | `iPhone9,1` / D10AP / A10-T8010 | `iPhone10,3` / D22AP / A11-T8015 |
| Kernel XNU version string | `xnu-8020.241.44~1` | `xnu-8796.142.1.703.8~1` |
| Reported kernel build target | `RELEASE_ARM64_T8010` | `RELEASE_ARM64_T8015` |

These values are recorded in the
[20H392 donor / 19H422 target KernelCache comparison](20h392-19h422-multitouch-kernelcache-comparison.md).
They are identities read from the already-inspected kernel artifacts, not
proof that either kernel is suitable for the other board.

## The important distinction

The iPhone X donor KernelCache reports a T8015 build target, but the public
`xnu-8796.141.3` source snapshot does not expose a normal T8015 machine
selection either. The donor's reported XNU version,
`8796.142.1.703.8~1`, is also not identical to the pinned public source tag,
`xnu-8796.141.3`.

This is an important provenance limitation: the public 8796 source snapshot
does not, by itself, reproduce the complete board-selection configuration
reported by the shipped 20H392 donor kernel. A shipped Apple kernel can
therefore identify a T8015 build even though that public source tag does not
contain the corresponding T8015 selection. The public source snapshot is not
a complete record of every product-specific input used for the shipped
KernelCache.

The same caution applies to T8010. The stock iPhone 7 19H422 KernelCache
reports `RELEASE_ARM64_T8010`, but its XNU version is
`8020.241.44~1`, not 8796. That confirms the inspected stock target kernel
was built for T8010 in its own XNU generation. It does not show that the
selected iOS 16-era 8796 source contains a usable T8010 profile.

## Interpretation of the embedded XNU label

A follow-up review of Apple's public `xnu-8796.141.3` version-stamping
logic shows that the embedded `xnu-8796.142.1.703.8~1` text should not be
treated automatically as a Git tag. `config/version.c` places
`KERNEL_BUILD_OBJROOT` in the kernel version string. In the public
`config/newvers.pl`, when `RC_XBS` is defined, an `RC_STRING` is
constructed from `RC_ProjectNameAndSourceVersion` and
`RC_ProjectBuildVersion`; in the build-object-path-under-`OBJROOT`
branch, that value becomes the leading object-root label. Thus the donor
string is consistent with an XBS project/source-version label plus build
number, but the donor's exact build environment has not been recovered.
The exact source commit and the product-specific build inputs remain unknown.

The public tag-ref query for `xnu-8796` returned the tags
`xnu-8796.101.5`, `xnu-8796.121.2`, and `xnu-8796.141.3`; it did not
return an `xnu-8796.142.*` tag. This does not exclude private Apple source
or separately published build records. See
[Interpreting the 20H392 XNU version-stamp string](xnu-kernel-version-stamp-provenance.md)
for the bounded source analysis and official source links.

## Independent downstream co-pin of the 20H392 donor

A separate UniXNU port for OnePlus 13 / SM8750 publishes a local
iPhone10,3 / D22AP / iOS 16.7.16 (20H392) profile. Its profile pairs
`xnu-8796.141.3` / commit
`1b191cb58250d0705d8a51287127505aa4bc0789` with the same
`[kernel.prelink].kernelcache_sha256` already recorded for the donor
KernelCache in this repository:
`2ec297bac95bcba01046fd0148e97e7e5885c05a6c18827f39f534ba375c1221`.
The external port's patch-application report records 62 patches applied in
order to a clean checkout of that pinned public source.

This is stronger downstream artifact co-pinning than the earlier version
string comparison alone, but it is not an Apple source-to-binary attestation.
The report explicitly separates patch application from compilation, binary
ABI, and hardware validation. The downstream profile's candidate kernel
output path is `DEVELOPMENT_ARM64_BCM2837`, not
`RELEASE_ARM64_T8015` or an iPhone9,1/T8010 build. Its port-specific
security-init, sparse-index, typed-delete/UIO-alignment, and VFS helper
patches must not be treated as general Apple source requirements or copied
wholesale into Sweet-10.

See [the detailed UniXNU 20H392 cross-check](unixnu-20h392-xnu-baseline-crosscheck.md)
for the immutable profile, report, and patch references. The exact Apple
source revision and product-specific inputs remain unknown.

## Bounded conclusions

What the evidence establishes:

1. Public XNU `xnu-7195.121.3` exposes a normal T8010 ARM64 machine
   selection and its matching H9 board/CPU configuration.
2. Public XNU `xnu-8019.80.24` and `xnu-8796.141.3` do not expose that
   T8010 selection at the audited paths.
3. The inspected iPhone X 20H392 KernelCache reports
   `RELEASE_ARM64_T8015`, while the public `xnu-8796.141.3` tag does not
   expose a T8015 selection.
4. The pinned public `xnu-8796.141.3` tag is not proven to be the exact
   source used for the donor KernelCache whose embedded XNU version string is
   `8796.142.1.703.8~1`.

What the evidence does **not** establish:

- that Apple's private or product-specific source inputs lacked T8015;
- that no later/private XNU 8796 implementation could support T8010;
- that adding back the old T8010 name, H9 header, or compiler flag would
  recreate a valid later-generation A10 platform;
- that the 20H392 donor kernel can run on iPhone9,1; or
- that iOS 16 userland or SpringBoard is compatible with iPhone9,1.

Do not treat an allowlist change, a copied H9 header, or a generic ARM64
compile as a target-support result.

## Next evidence gate

Keep the exact source-to-binary mapping open. The next useful evidence is
authoritative provenance for the 20H392 kernel's exact XNU source revision
and product-specific configuration inputs, followed by a source-level
comparison of those inputs with the known T8010 requirements. The 20H392
BuildManifest identifies iPhone X restore identities; it is not an iPhone 7
target map. The selected public tag remains a research candidate, not a
verified reproduction of the donor kernel build.

The kernel readiness requirements remain tracked in
[kernel-implementation-readiness.md](kernel-implementation-readiness.md).
No kernel implementation, firmware operation, device boot, or partition
change is claimed by this report.
