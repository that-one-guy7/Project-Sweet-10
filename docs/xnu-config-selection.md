# XNU 8796 ARM64 configuration selection audit

Pinned source: Apple XNU `xnu-8796.141.3`, commit
`1b191cb58250d0705d8a51287127505aa4bc0789`.

This is a source-level build-system audit. It does not define a new iPhone9,1 machine
configuration and does not establish that the pinned source can boot on A10.

## Configuration layers observed

The XNU tree has several distinct configuration inputs:

1. `config/MASTER` is the machine-independent master configuration.
2. `config/MASTER.arm64` supplies generic ARM64-specific configuration.
3. `config/MASTER.arm64.iPhoneOS` supplies the iPhoneOS ARM64 configuration.
4. `config/MASTER.arm64.t8110.iPhoneOS` is an additional SoC-named iPhoneOS
   configuration present in this source revision.
5. The `doconf` configuration process combines selected master files to produce
   a concrete configuration. The master-file comments describe this mechanism.

The presence of the t8110 file is not evidence that it is suitable for T8010. Its
name explicitly identifies a different SoC family. Do not rename it or reuse its
SoC-specific content as an A10 configuration.

## Build-time validation

The pinned `makedefs/MakeInc.kernel` validates four independent selections before
kernel build rules proceed:

- `CURRENT_ARCH_CONFIG` must be in `SUPPORTED_ARCH_CONFIGS`.
- `CURRENT_KERNEL_CONFIG` must be in `SUPPORTED_KERNEL_CONFIGS`.
- `CURRENT_MACHINE_CONFIG` must be in
  `SUPPORTED_$(CURRENT_ARCH_CONFIG)_MACHINE_CONFIGS`.
- `PLATFORM` must be in `SUPPORTED_PLATFORMS`.

This means that selecting ARM64 alone does not select a valid board or platform.
The supported ARM64 machine-configuration list is defined in the pinned source's
makedefs/MakeInc.def, not merely supplied as an unspecified build-environment value.
For normal builds (neither simulator nor host project names), xnu-8796.141.3 sets
SUPPORTED_ARM64_MACHINE_CONFIGS to BCM2837, T6000, T8101, T8103, and VMAPPLE.
T8010 is absent. The kernel make fragment then rejects a CURRENT_MACHINE_CONFIG
that is not in the corresponding supported list. This is a concrete build-system
gate for the selected baseline, not just a missing board header.

## Platform-expert build fragments

The pinned `pexpert/Makefile` includes `conf` as a component directory.
Within that directory:

- `Makefile.arm64` is present but contains only its begin/end markers; it adds no
  ARM64-specific make rules in this revision.
- `files.arm64` lists the ARM platform-expert sources compiled for ARM64, including
  `pe_identify_machine.c` and `pe_init.c`.
- `Makefile.template` contains generated placeholders such as `%OBJS`, `%CFILES`,
  `%MACHDEP`, and `%RULES`; comments state that the configuration tool fills them.

This explains why looking for a standalone `pexpert/arm64/board_config.h` was
misleading: that path is not present in the inspected tree. The actual generated
configuration and include provenance must be followed through the build system.

## What is established and what is not

Established from the pinned source:
- The four build selections above are validated independently.
- Generic ARM64 and iPhoneOS ARM64 master configuration files exist.
- A t8110-named iPhoneOS master file exists.
- The ARM64 platform-expert file list includes shared ARM source files.
- The ARM64 platform-expert make fragment is empty in this revision.

Not established:
- That this XNU revision contains a supported T8010/iPhone9,1 machine configuration.
- That the t8110 configuration is relevant to A10.
- The exact build settings used for the 20H392 iPhone X kernel.
- The exact XNU commit shipped in 20H392.
- Any iPhone9,1 memory map, interrupt topology, device-tree contents, or peripheral
  compatibility.

## Decision

Do not add a guessed T8010 machine configuration yet. First locate the authoritative
build settings and exact kernel metadata for the selected 20H392 reference, then compare
the source's supported machine configuration list against evidence for iPhone9,1.

## Pinned source links

- [MASTER](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/config/MASTER)
- [MASTER.arm64](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/config/MASTER.arm64)
- [MASTER.arm64.iPhoneOS](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/config/MASTER.arm64.iPhoneOS)
- [MASTER.arm64.t8110.iPhoneOS](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/config/MASTER.arm64.t8110.iPhoneOS)
- [MakeInc.kernel](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/makedefs/MakeInc.kernel)
- [pexpert Makefile](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/Makefile)
- [pexpert Makefile.template](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/conf/Makefile.template)
- [pexpert files.arm64](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/conf/files.arm64)
- [pexpert Makefile.arm64](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/conf/Makefile.arm64)


## Versioned machine-configuration allowlist

The source-level list was compared in the same file, makedefs/MakeInc.def, across
three Apple-published XNU tags:

| XNU tag | Normal ARM64 machine-configuration allowlist |
|---|---|
| xnu-7195.121.3 | T7000, T7001, S8000, S8001, T8010, T8011, BCM2837, T8020, T8101, T8103 |
| xnu-8019.80.24 | BCM2837, T6000, T8101, VMAPPLE |
| xnu-8796.141.3 | BCM2837, T6000, T8101, T8103, VMAPPLE |

The xnu-7195 list contains T8010. The xnu-8019 and xnu-8796 lists do not.
The exact source change or tag at which T8010 was removed or refactored has not
been identified. This comparison establishes only what each tagged MakeInc.def
declares for normal ARM64 builds; simulator and host project-name conditions
have their own NONE lists.

The pinned xnu-8796.141.3 MakeInc.kernel checks CURRENT_MACHINE_CONFIG against
SUPPORTED_$(CURRENT_ARCH_CONFIG)_MACHINE_CONFIGS and emits an unsupported
configuration error when the value is not included. Therefore, the standard
pinned source rules do not offer T8010 as a normal ARM64 machine selection.
Overriding or patching that list would bypass a check, not create the missing
SoC implementation, CPU configuration dependencies, board configuration,
device tree, or platform services.

## How embedded product selection is resolved

The pinned makedefs/MakeInc.top can use EMBEDDED_DEVICE_MAP and the device_map.db
under the SDK platform bundle to query target product types, kernel architecture,
and KernelPlatform. It uses those results to form build-target configuration
triplets. The default database path is derived in makedefs/MakeInc.cmd from
PLATFORMPATH/usr/local/standalone/firmware/device_map.db.

The use is conditional: the source only runs these product-map queries when
EMBEDDED_DEVICE_MAP is supplied. The attached 20H392 BuildManifest is not this
database and does not expose its full product-to-KernelPlatform mappings.
Accordingly, this audit has not established whether a particular installed SDK
database contains an iPhone9,1 target or what KernelPlatform it would assign.

The make rules also derive PLATFORMPATH and PLATFORM from the selected SDK through
xcrun. iPhoneOS is listed among the supported embedded platform names, but this
does not add T8010 to the ARM64 machine allowlist or prove that the required
iPhoneOS platform SDK and target metadata are installed on a particular host.

## Revised decision

Treat T8010 as an explicitly missing machine selection in the selected XNU 8796
source baseline. Do not choose T8010 by hand, rename the t8110 config, or change
the allowlist merely to make configuration validation pass. The next research
gate is to identify the historical T8010 dependencies and establish whether an
iPhone9,1 target mapping and complete platform implementation can be supported
in a separate, reviewable source port.
