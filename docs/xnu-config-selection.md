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
The supported machine-configuration list is supplied by the build environment and
must be traced to its authoritative build settings. Do not assume a machine name
from a different XNU release or a downstream fork is accepted by this revision.

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
