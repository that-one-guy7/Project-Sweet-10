# ARM64 platform-interface comparison: XNU 7195 vs 8796

## Scope

This is a read-only source comparison of public Apple XNU tags
`xnu-7195.121.3` (the historical generation containing the T8010/H9 profile)
and `xnu-8796.141.3` (the selected iOS 16-era source candidate).

It focuses on generic interfaces between the ARM64 kernel and platform-expert
code: boot arguments, device-tree intake, SoC/clock discovery, CPU topology,
CPU register mapping, and CPU lifecycle accounting. It does not implement a
machine configuration, infer hardware values for iPhone9,1, or establish that
the 8796 source can boot on an iPhone 7.

## Executive result

Several interface shapes remain recognizable across the two versions, but
their continued existence does not mean a 7195 platform implementation can be
transplanted unchanged:

- The visible `boot_args` field order in ARM64 `boot.h` is unchanged in the
  reviewed tags. This only compares the source structure; it does not verify a
  loader's handoff ABI, required revision, memory ownership, or runtime values.
- `PE_init_platform(boolean_t vm_initialized, void *args)` retains its
  signature and core DeviceTree initialization flow.
- `ml_parse_cpu_topology(void)`, `ml_map_cpu_pio(void)`, and the core
  `ml_processor_register` / `ml_init_timebase` interfaces remain.
- The modern CPU-topology parser adds CPU-mask validation and richer cluster
  accounting, and its CPU-down/up count updates are split into separate calls.
- The topology and platform-expert code still depend on detailed DeviceTree
  information. The repository has no verified iPhone9,1 values for those
  properties or register ranges.

## Interface comparison

| Area | XNU 7195.121.3 | XNU 8796.141.3 | Project implication |
|---|---|---|---|
| ARM64 `boot_args` | Contains Revision, Version, virtual/physical base, memory size, topOfKernelData, Video, machineType, DeviceTree pointer/length, CommandLine, bootFlags, memSizeActual | Same visible field sequence in the reviewed `pexpert/pexpert/arm64/boot.h` | A shared struct layout is not proof of the exact handoff contract or compatible values |
| Platform entry | `PE_init_platform(boolean_t, void *)` initializes stored boot args and DeviceTree, calls `pe_identify_machine` before VM initialization, and performs interrupt/debug setup later | Same signature and same broad ordering in the reviewed function | Existing generic entry point remains; required iPhone 7 DeviceTree and boot inputs are unknown |
| SoC and clock discovery | `pe_identify_machine` gets SoC base information from `arm-io`; legacy SoC-type branches exist, otherwise it reads clock properties from running CPU nodes under `/cpus` | Legacy SoC-type branches are gone in the reviewed function; it uses the DeviceTree-driven clock path | Do not copy clock defaults or legacy SoC constants. The actual target DeviceTree must provide trustworthy values |
| CPU topology | `ml_parse_cpu_topology` iterates `/cpus`, reads CPU identity/cache/register properties and builds logical clusters | Same core parser and many same property names, with additional cpumask handling, validation state, die/cluster counters | Property names are evidence of parser expectations, not evidence that the target tree has valid values |
| CPU PIO mapping | `ml_map_cpu_pio` maps per-CPU/per-cluster implementation register ranges after VM initialization | Same function and stated ordering contract | Register ranges must be grounded in target evidence; do not infer them from another SoC |
| Processor registration | `ml_processor_info` and `ml_processor_register` provide the platform-to-XNU processor registration contract | Reviewed struct field order and registration signature remain the same | The generic registration interface remains, but target-specific callbacks and data are not supplied by this audit |
| CPU lifecycle accounting | `ml_cpu_up/down` update machine CPU counts as part of lifecycle work | Adds separate `ml_cpu_up_update_counts(int)` and `ml_cpu_down_update_counts(int)` routines; lifecycle/count work is split | This is a real semantic evolution, not just a header rename; platform integration needs review against 8796 behavior |
| Interrupt/timebase hooks | `ml_init_interrupt`, `ml_init_timebase`, and related machine-layer declarations exist | The core declarations remain; modern header also includes additional interrupt/PAC and timing hooks | Signature continuity does not establish the target interrupt controller, timer frequency, or wiring |

## DeviceTree contract observed in the CPU topology parser

The reviewed implementations of `ml_parse_cpu_topology` in both tags:

1. Look up the `/cpus` node and iterate its child entries.
2. Read each CPU child's `reg` property as a mandatory physical CPU identifier.
3. Read optional cache metadata: `l2-access-penalty`, `l2-cache-size`,
   `l2-cache-id`, `l3-cache-size`, and `l3-cache-id`.
4. Read optional per-CPU register ranges: `cpu-uttdbg-reg`,
   `cpu-impl-reg`, and `coresight-reg`.
5. Read `cluster-type` to classify the CPU as the default SMP type or as
   `E` / `P` where present.
6. Read optional cluster-level register ranges repeated in the CPU nodes:
   `acc-impl-reg` and `cpm-impl-reg`.
7. Read `die-cluster-id` and `cluster-core-id` with MPIDR-derived fallbacks.

The parser also relies on compile-time limits such as `MAX_CPUS`,
`MAX_CPU_CLUSTERS`, and `MAX_CPU_CLUSTER_PHY_ID`. These limits must agree
with the selected machine configuration and the data represented by the tree.

The 8796 parser additionally accepts a `cpumask` selection input, detects
conflicting CPU-count and CPU-mask inputs, and tracks CPU/cluster type counts.
This is a difference in the generic parser's validation and accounting. This
document does not prescribe device boot arguments or device operations.

## DeviceTree contract observed in platform-expert initialization

In both versions, `PE_init_platform` initializes Secure DeviceTree handling
from the boot-argument structure's `deviceTreeP` and `deviceTreeLength`
fields. Before VM initialization it calls `pe_identify_machine`; later it
calls the ARM platform interrupt/debug initialization functions.

The reviewed function also reads root-level `device-tree` properties
`target-type` and `model`, and reads values under `/chosen` including
`debug-enabled`, `firmware-version`, `unique-chip-id`, and
`dram-vendor-id`. The newer version also has conditional support for a
`system-firmware-version` value in a particular build environment.

In XNU 8796, `pe_identify_machine` obtains the SoC base from the `arm-io`
node and uses running CPU nodes under `/cpus` for clock metadata. The reviewed
clock properties include `timebase-frequency`, `bus-frequency`,
`memory-frequency`, `peripheral-frequency`, `fixed-frequency`, and
`clock-frequency`. The code has fallback defaults when values are not found;
those defaults are generic fallback behavior, not approved iPhone9,1 hardware
constants.

## Important source-level differences

### Legacy clock identification is removed from the reviewed function

XNU 7195's `pe_identify_machine` contains hard-coded clock branches for a set
of legacy SoC device-type strings, then falls back to DeviceTree for other
platforms. XNU 8796's corresponding function uses the DeviceTree-driven path
directly. This is an example of a generic platform interface becoming more
uniform while the exact target data still needs to exist.

### CPU topology is more expressive in XNU 8796

The newer parser adds cpumask validation and bookkeeping for CPU and cluster
types, and the newer machine-routines implementation separates the CPU state
transition from active-count bookkeeping with `ml_cpu_up_update_counts` and
`ml_cpu_down_update_counts`. It is therefore not accurate to characterize the
modern source as simply retaining all old platform semantics unchanged.

### Register mapping is data-driven

The declaration comment for `ml_map_cpu_pio` says it is called after
`arm_vm_init()` because it cannot be part of `ml_parse_cpu_topology()`.
Its implementation maps the register ranges previously collected from CPU
and cluster DeviceTree entries. The parser/mapper interface remains, but the
specific register ranges are hardware descriptions and are not supplied by
generic code.

## What remains unknown for iPhone9,1 / D10AP

This comparison does not establish:

- The exact boot-argument revision/version and values required for the target.
- A complete iPhone9,1 DeviceTree or validated `/cpus` subtree.
- The actual MPIDR values, CPU node count/order, cluster topology, or cache data.
- Target values for `arm-io` `device_type` / `ranges` and the clock properties.
- Per-CPU/per-cluster implementation, UTTDBG, CoreSight, ACC, or CPM register ranges.
- The interrupt controller, interrupt assignments, timer source, or target frequency.
- The selected XNU 8796 machine configuration or target SDK device-map record.
- Whether the 20H392 iPhone X kernel's source/build metadata corresponds to the
  pinned XNU tag. Its supplied BuildManifest identities are iPhone X A11/T8015,
  not iPhone9,1/A10/T8010.

## Decision

The generic ARM64 interfaces are useful for defining the evidence the project
must collect, but they are not an implementation plan by themselves. Keep the
iPhone9,1 platform values marked unknown until they are tied to a reliable,
revision-matched source. Do not substitute Qualcomm, iPhone X, or virtual-board
values, and do not treat the unchanged `boot_args` structure as validation of
a device handoff.

This audit makes no kernel changes and contains no device, firmware, or boot
procedure.

## Source files

### XNU 7195.121.3

- [ARM64 boot arguments](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/boot.h)
- [Platform initialization](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/arm/pe_init.c)
- [Machine identification and clock discovery](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/arm/pe_identify_machine.c)
- [ARM64 machine routines](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/machine_routines.c)
- [Machine-layer interface declarations](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm/machine_routines.h)

### XNU 8796.141.3

- [ARM64 boot arguments](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/boot.h)
- [Platform initialization](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/arm/pe_init.c)
- [Machine identification and clock discovery](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/arm/pe_identify_machine.c)
- [ARM64 machine routines](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines.c)
- [Machine-layer interface declarations](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm/machine_routines.h)
- [ARM64 board configuration](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/board_config.h)
