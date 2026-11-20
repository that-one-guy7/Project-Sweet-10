# XNU 8796 ARM64 platform source map

Pinned source: Apple XNU tag `xnu-8796.141.3`, commit
`1b191cb58250d0705d8a51287127505aa4bc0789`.

This note records a read-only source review. It is not a boot recipe, a device-tree
specification, or proof that the selected source supports iPhone9,1.

## Files reviewed

| XNU path | Role visible in source | Project Sweet-10 implication |
|---|---|---|
| `osfmk/arm64/start.s` | ARM64 reset-vector and early CPU-start assembly; selects per-CPU data using MPIDR_EL1 and dispatches a reset handler | The entry contract and CPU identity must be understood before platform work; no iPhone7 values are inferred here |
| `osfmk/arm64/cpu.c` | ARM64 CPU lifecycle, idle, power-state and inter-processor coordination code | CPU bring-up is broader than identifying an ARM64 core; platform callbacks and topology remain to be established |
| `osfmk/arm64/arm_vm_init.c` | Bootstrap page tables, physical/virtual memory bounds, kernel layout and KASLR-related state | Memory map and early translation assumptions are foundational and cannot be copied from SWEET |
| `pexpert/arm/pe_identify_machine.c` | Reads device-tree CPU nodes and clock properties; looks up `arm-io` and its `ranges` property | The expected device-tree schema and address interpretation must be documented from the target's own evidence |
| `pexpert/arm/pe_init.c` | Platform-expert initialization; handles panic region discovery through `pram` and `/chosen` properties among other setup | The boot environment must provide a compatible platform description; the presence of generic code does not prove target compatibility |
| `osfmk/arm64/machine_cpuid.h` | Defines ARM64 feature-register data structures | Feature detection is architectural; the actual target register values and enabled feature assumptions still require evidence |

## Concrete source observations

### Device-tree consumers

The reviewed `pe_identify_machine.c`:
- Looks up the `/cpus` node and iterates its children.
- Selects CPU entries whose `state` property is `running`.
- Reads optional `timebase-frequency`, `bus-frequency`, `memory-frequency`,
  `peripheral-frequency`, `fixed-frequency`, and `clock-frequency` properties.
- Looks up a node named `arm-io`, then reads `device_type` and `ranges`.

The reviewed `pe_init.c` contains panic-region discovery that looks for `pram`,
its `reg` property, and `/chosen/embedded-panic-log-size`. This is one example of
why the device-tree contract is consumed by multiple early platform components.

These observations describe XNU source expectations. They do not establish that a
particular property exists, has a particular value, or is encoded identically in an
iPhone9,1 device tree.

### CPU startup and memory

The reviewed `start.s` defines low reset and exception vectors and uses
`MPIDR_EL1` to match a physical CPU identifier against per-CPU data. The reviewed
`arm_vm_init.c` establishes bootstrap page-table state and tracks physical and
virtual memory bounds. These are separate concerns from a board-specific driver.

## Include/configuration caveat

Some ARM64 files include `pexpert/arm64/board_config.h`. A direct lookup at the
pinned tag did not establish this as a normal tracked file at that path. It may be
generated or supplied through the build configuration. The exact source/build
provenance of this header is therefore an open investigation item, not an assumed
file to edit.

## Review status

- [x] Identify core ARM64 startup, CPU, VM, and platform-expert source files.
- [x] Record device-tree property names consumed by reviewed platform code.
- [ ] Trace build-time generation and selection of board configuration headers.
- [ ] Establish the exact 20H392 kernel build metadata.
- [ ] Establish iPhone9,1 device-tree facts from reliable, lawful sources.
- [ ] Compare every required XNU property with evidence for the target.
- [ ] Reproduce an unmodified source build.

## Upstream source links

- [start.s](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/start.s)
- [cpu.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/cpu.c)
- [arm_vm_init.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/arm_vm_init.c)
- [pe_identify_machine.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/arm/pe_identify_machine.c)
- [pe_init.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/arm/pe_init.c)
- [machine_cpuid.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_cpuid.h)
