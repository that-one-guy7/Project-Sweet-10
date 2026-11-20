# A10 / T8010 evidence audit in XNU

## Purpose and scope

This is a bounded, read-only source audit for Project Sweet-10's iPhone 7
(`iPhone9,1`, A10/T8010) research target. It checks whether a T8010 string or
generic ARM64 source is evidence of a complete platform implementation.

Pinned XNU baseline:
- Tag: `xnu-8796.141.3`
- Commit: `1b191cb58250d0705d8a51287127505aa4bc0789`

No device was connected. No boot, exploit, firmware, partition, or payload operation
was performed.

## Findings

### 1. The T8010 string found in newer XNU is test logic, not a platform port

A GitHub code search on the current XNU default branch located
`tests/vm_test_code_signing.c` at commit
`f6217f891ac0bb64f3d375211650a4c1ff8ca1ea`. In that file, T8010 appears in an
array named `pmap_cs_disabled_platforms`, alongside T8011, T8012, and T8015.
The surrounding test checks whether PMAP_CS is disabled by default based on a
substring in `kern.version`, unless a boot argument overrides it.

That is a code-signing test condition. It is not CPU initialization, board setup,
device-tree support, interrupt setup, or an iPhone 7 platform definition. It must
not be cited as proof that XNU supports T8010 as a bootable platform.

The same test path could not be fetched at the pinned `xnu-8796.141.3` tag
(the path returned 404). Therefore this newer test result is not attributed to
the pinned baseline.

### 2. The pinned ARM64 board configuration lists other profiles

At `xnu-8796.141.3`, `pexpert/pexpert/arm64/board_config.h` describes its
purpose as per-SoC configuration and contains conditional profiles for:
- `ARM64_BOARD_CONFIG_T6000`
- `ARM64_BOARD_CONFIG_T8101`
- `ARM64_BOARD_CONFIG_T8103`
- `ARM64_BOARD_CONFIG_BCM2837`
- `ARM64_BOARD_CONFIG_VMAPPLE`

The reviewed file does not define an `ARM64_BOARD_CONFIG_T8010` profile.
This is a concrete gap in this particular board-configuration header, not proof
that no other downstream or private source can provide additional configuration.

The ARM64 pexpert Makefile lists `board_config.h` among the private kernel
headers. `osfmk/machine/config.h` selects the ARM64 board configuration header
when compiling for `__arm64__`. Together these files show that board configuration
is a real build input, not something established by generic ARM64 assembly alone.

### 3. Generic ARM64 source does not identify iPhone9,1

The following pinned files were fetched and reviewed:
- `osfmk/arm64/start.s`
- `osfmk/arm64/cpu.c`
- `osfmk/arm64/arm_vm_init.c`
- `pexpert/arm/pe_identify_machine.c`
- `pexpert/arm/pe_init.c`
- `pexpert/conf/files.arm64`
- `config/MASTER`
- `config/MASTER.arm64`
- `config/MASTER.arm64.iPhoneOS`
- `osfmk/machine/config.h`
- `pexpert/pexpert/arm64/Makefile`

The reviewed startup, CPU, VM, and platform-expert files contain no literal
`T8010` or `iPhone9,1` identifier. They provide generic ARM64 and platform
framework code. That absence in the reviewed paths is not an exhaustive proof
about all XNU source or Apple's private build inputs.

The ARM64 `files` configuration includes shared ARM platform-expert source
files, including `pe_identify_machine.c` and `pe_init.c`. Inclusion of those
generic files does not supply the target's board constants or device-tree data.

## Evidence table

| Source | Observation | What it proves | What it does not prove |
|---|---|---|---|
| `pexpert/pexpert/arm64/board_config.h` at pinned tag | Lists T6000, T8101, T8103, BCM2837, VMAPPLE profiles; no T8010 profile in this file | Reviewed header lacks a T8010 profile | That no downstream/private config exists |
| `pexpert/pexpert/arm64/Makefile` | Exports `board_config.h` as a private kernel header | Header participates in ARM64 build inputs | Which profile a particular Apple build selected |
| `osfmk/machine/config.h` | Includes `pexpert/arm64/board_config.h` for `__arm64__` | Architecture selects board configuration header | A working iPhone9,1 config |
| `tests/vm_test_code_signing.c` at later commit | T8010 is in PMAP_CS default-disabled test list | Test recognizes T8010 as a platform string for this test condition | XNU T8010 bring-up or support in the pinned tag |
| Generic ARM64 startup/CPU/VM and pexpert files | No literal T8010 or iPhone9,1 identifier in reviewed files | These paths are generic framework code | Full source-tree absence or target compatibility |

## Source links

Pinned XNU 8796:
- [ARM64 board configuration](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/board_config.h)
- [ARM64 pexpert Makefile](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/Makefile)
- [machine config header](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/machine/config.h)
- [ARM64 source file list](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/conf/files.arm64)
- [ARM64 startup](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/start.s)
- [ARM64 CPU](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/cpu.c)
- [ARM64 VM initialization](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/arm_vm_init.c)
- [ARM platform identification](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/arm/pe_identify_machine.c)
- [ARM platform initialization](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/arm/pe_init.c)
- [ARM64 master config](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/config/MASTER.arm64)
- [iPhoneOS ARM64 master config](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/config/MASTER.arm64.iPhoneOS)

Later-branch test reference (not pinned XNU 8796):
- [T8010 PMAP_CS test condition](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/tests/vm_test_code_signing.c)

## Conclusion and next evidence gate

**Conclusion:** the reviewed XNU 8796 source does not establish iPhone9,1/T8010
platform support. The specific T8010 reference found on a later XNU branch is
test-only. The pinned ARM64 board configuration header has no T8010 profile.
This is a bounded source finding, not a claim that no compatible implementation
could exist elsewhere.

Before any compatibility claim, Sweet-10 still needs reliable, revision-matched
evidence for:
1. the actual board configuration and build inputs used by the intended kernel;
2. iPhone9,1 platform identity and device-tree schema;
3. CPU topology and feature assumptions;
4. memory map, interrupt controller, timer, and peripheral descriptions;
5. the exact kernel metadata associated with the selected 20H392 donor profile.

Keep these items marked unknown until supported by authoritative source evidence.
Do not fill the gaps with guessed constants or values copied from Qualcomm ports.
