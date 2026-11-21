# ARM64 interrupt and timer interface audit: XNU 7195 vs 8796

## Scope

This is a read-only comparison of Apple's public XNU tags
`xnu-7195.121.3` and `xnu-8796.141.3`. It reviews the ARM platform-expert
interrupt-controller mapping, ARM64 interrupt initialization, timebase
registration, architectural timer access, and AIC register headers.

It does not define an iPhone9,1 interrupt controller, provide interrupt IDs,
supply register addresses, or establish that the selected XNU 8796 source is
compatible with an iPhone 7.

## Executive findings

- The platform-expert functions `pe_arm_map_interrupt_controller` and
  `pe_arm_init_interrupts` are byte-identical in the two tags.
- Those functions locate an `interrupt-controller` node with
  `interrupt-controller = "master"` and a `device_type = "timer"` node,
  then map each node's `reg` range relative to the SoC base discovered from
  the `arm-io` node. This is register-window mapping, not a complete
  interrupt-routing description.
- The ARM64 `ml_init_interrupt` and `ml_init_timebase` functions are also
  byte-identical. The former performs the conditional `HAS_IPI` deferred-IPI
  timer setup for the cluster master; it should not be mistaken for the
  peripheral interrupt-controller driver.
- Both AIC headers reviewed are byte-identical between the tags. They provide
  register definitions, but do not identify which device-tree node, physical
  base, interrupt routing, or timer source a specific iPhone board uses.
- ARM64's generic decrementer access remains based on `CNTV_TVAL_EL0` when
  no CPU-specific callback is installed. The generic hardware timebase
  implementation has evolved: XNU 8796 adds a nonspeculative counter selection
  and protects the combined clock/base read against a sleep/wake race.
- XNU 8796's SoC clock discovery is more uniformly DeviceTree-driven. It
  reads the `timebase-frequency` property from running CPU nodes and uses
  fallback defaults when properties are missing. Those defaults are not
  verified iPhone9,1 hardware values.

## Interrupt-controller DeviceTree contract

The reviewed `pe_arm_map_interrupt_controller(void)` implementation is
identical in both tags. Its observable requirements are:

1. It calls `pe_arm_get_soc_base_phys()`, which obtains the SoC base from the
   DeviceTree `arm-io` node.
2. It searches for an entry with `interrupt-controller = "master"`.
3. It reads that entry's `reg` property and maps the range at
   `soc_phys + reg[0]` with length `reg[1]` into `gPicBase`.
4. It searches for a node whose `device_type` is `"timer"`.
5. It reads that node's `reg` property and maps the range at
   `soc_phys + reg[0]` with length `reg[1]` into `gTimerBase`.
6. It returns failure if the SoC base, controller mapping, or timer mapping
   is unavailable.

The helper only obtains register mappings. It does not parse a complete
interrupt specifier/routing table in this function, assign device interrupt
numbers, or prove that the mapped block is the correct controller for a
particular board. Those are separate platform/device-tree obligations.

The wrapper `pe_arm_init_interrupts(void *args)` is also identical in both
tags. When `args` is non-null, it requests the mappings and then calls
`pe_arm_init_timer(args)`.

## ARM64 interrupt initialization is a separate layer

The ARM64 `ml_init_interrupt(void)` implementation is unchanged between the
reviewed tags. It is guarded by `HAS_IPI`; for a cluster master it adjusts
the deferred IPI timer. That is CPU-to-CPU signaling support, not the same
thing as mapping the platform's peripheral interrupt controller.

This distinction matters for the project tracker: the generic XNU API existing
does not supply the controller's DeviceTree description, interrupt assignments,
per-CPU routing, or platform interrupt handler.

## Timer callback registration and architectural timer access

### Timebase registration

The reviewed `ml_init_timebase` implementation is byte-identical in both
tags. It records the supplied timebase callback operations and EOI address
for the boot CPU if no FIQ handler has already been registered.

In `pe_arm_init_timer`, both versions select an empty `tbd_ops` structure
for the ARM64 path. XNU 7195 additionally contains a conditional
`ARM_BOARD_CLASS_T8002` implementation for SoC device types
`t8002-io` and `t8004-io`; that branch configures AIC timer registers and
registers T8002-specific decrementer/FIQ callbacks. The corresponding
T8002-specific branch is not present in the reviewed XNU 8796 function.

This is a source-level comparison only. It does not establish that the
T8002 branch was selected for T8010, and it must not be treated as an A10
timer implementation. In both reviewed functions, the ordinary ARM64 path
selects the empty callback structure.

### Decrementer

The generic `ml_set_decrementer(uint32_t)` function is byte-identical in both
tags. It stores the decrementer value and calls a per-CPU setter callback if
one is installed; otherwise it writes the architectural
`CNTV_TVAL_EL0` register.

The corresponding `ml_get_decrementer(void)` path reads a per-CPU callback
when present, otherwise it reads `CNTV_TVAL_EL0`. The modern and historical
implementations retain this callback-or-architectural-register structure.

The `ml_get_timer_pending()` helper checks the architectural
`CNTV_CTL_EL0` interrupt-status bit in the reviewed source.

### Hardware timebase

The historical XNU 7195 `ml_get_hwclock()` implementation executes an
instruction synchronization barrier and reads `CNTVCT_EL0`.

XNU 8796 factors this into `nonspeculative_timebase()`:
- use `ACNTVCT_EL0` when `HAS_ACNTVCT` is defined;
- otherwise use `CNTVCTSS_EL0` when the architecture feature test
  `__ARM_ARCH_8_6__` is true;
- otherwise execute an ISB and read `CNTVCT_EL0`.

XNU 8796's `ml_get_timebase()` also reads `cpu_base_timebase`, reads the
hardware clock, and retries if the base changed during the operation. Its
comment associates this with a sleep/wake race. The historical implementation
simply adds the current hardware counter to `cpu_base_timebase`.

The historical H9 header does not define `HAS_ACNTVCT`. The modern H13
header does define it. This is a concrete configuration distinction; it is
not evidence that H9 and H13 timebase behavior is interchangeable or that an
iPhone9,1 configuration should select the H13 path.

## Timebase frequency discovery

The reviewed XNU 8796 `pe_identify_machine` code starts with fallback
frequency values and scans the running CPU entries under `/cpus`. It reads
properties including:

- `timebase-frequency`
- `bus-frequency`
- `memory-frequency`
- `peripheral-frequency`
- `fixed-frequency`
- `clock-frequency`

The earlier XNU 7195 function includes hard-coded clock branches for several
legacy SoC `device_type` strings and falls back to the DeviceTree clock
properties for other platforms. The newer function uses the DeviceTree-driven
path directly.

The XNU 8796 fallback defaults include 24 MHz for timebase, 100 MHz for bus
clock rate, and 400 MHz for CPU clock rate. These are fallback values in that
source function, not verified iPhone9,1 measurements. They must not be copied
into a target profile as asserted A10 frequencies.

The real-time clock code registers a timebase-frequency callback, validates
its numerator/denominator, and derives the constants used by the clock
conversion code. Therefore an incorrect or unverified DeviceTree timebase
frequency can affect the kernel's conversion between hardware ticks and
elapsed time.

## AIC header comparison

The following public headers are byte-identical between the two tags:

- `pexpert/pexpert/arm64/AIC.h`
- `pexpert/pexpert/arm/AIC.h`

They define AIC register offsets and access helpers, including timer and
interrupt-related register names. Their presence proves only that the source
tree contains those definitions. It does not prove that the target board uses
that AIC instance, that the DeviceTree mapping points to it, or that the
interrupt routing and timer source agree with the header's assumptions.

## What remains unknown for iPhone9,1 / D10AP

This audit does not establish:

- The final runtime iPhone9,1 DeviceTree and whether its AIC/timebase nodes
  retain the same properties and values as the static 19H422 IPSW component.
- The target interrupt specifiers, IRQ numbers, trigger modes, priorities,
  CPU routing, per-core delivery, or IPI delivery mechanism.
- The AIC driver's complete source/initialization contract and whether the
  selected XNU 8796 build has a compatible implementation for this target.
- The relationship between the static `aic-timebase` register window and
  the architectural generic timer at runtime.
- The target's validated `timebase-frequency`, counter behavior, timer
  interrupt source, EOI requirements, or CPU-specific decrementer callbacks.
- Which CPU-specific decrementer callbacks, if any, are required by an A10
  implementation.
- The exact interrupt/timer configuration used by the 20H392 iPhone X kernel;
  its BuildManifest identities are A11/T8015 iPhone X devices, not iPhone9,1.

## Decision

The interrupt mapping wrapper and ARM64 timer APIs remain useful generic
interfaces. The later parsed 19H422 DeviceTree audit supplies static AIC and
AIC-timebase node identities and the first register windows consumed by the
generic mapper; it does **not** supply a complete interrupt/timer driver
contract. Keep the static mapping inputs separate from the still-unknown
runtime IRQ routing, EOI, timebase frequency, and callback selection.

Do not infer IRQ IDs or runtime behavior from the compatible string alone.
The values below are host-side static IPSW evidence, not a device
configuration, kernel patch, or boot procedure.

## Source files

### XNU 7195.121.3

- [Platform interrupt/timer mapping and clock discovery](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/arm/pe_identify_machine.c)
- [ARM64 machine routines](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/machine_routines.c)
- [ARM64 real-time clock](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm/rtclock.c)
- [ARM64 AIC register definitions](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/AIC.h)
- [ARM AIC register definitions](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm/AIC.h)
- [Historical H9 CPU configuration](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)

### XNU 8796.141.3

- [Platform interrupt/timer mapping and clock discovery](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/arm/pe_identify_machine.c)
- [ARM64 machine routines](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/machine_routines.c)
- [ARM64 real-time clock](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm/rtclock.c)
- [ARM64 AIC register definitions](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/AIC.h)
- [ARM AIC register definitions](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm/AIC.h)
- [Modern H13 CPU configuration](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/H13.h)

No device operation, firmware modification, or boot procedure is included.


## Target static DeviceTree evidence update

The separate [parsed iPhone9,1 19H422 DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md)
now supplies a bounded set of target-reference mapping inputs that were not
part of this original XNU source-only comparison:

- `/arm-io/aic` has `compatible = aic,1`,
  `device_type = interrupt-controller`,
  `interrupt-controller = master`, and `#interrupt-cells = 1`.
- Its first `reg` pair is ARM-IO-relative offset
  `0x0e100000`, length `0x8000`. It also has a second pair
  at offset `0x0e108000`, length `0x1000`.
- `/arm-io/aic-timebase` has `device_type = timer` and a
  `reg` pair at offset `0x0e108000`, length `0x1000`.
- The same parsed artifact and the pinned XNU `pe_arm_get_soc_base_phys()`
  source select the static SoC base `0x0000000200000000`.
- The address inputs to the generic first-window mappings are therefore
  `0x000000020e100000` for the AIC window and
  `0x000000020e108000` for the timebase window.

The pinned XNU 8796 generic mapper searches for the master interrupt-controller
node and the `device_type = timer` node, then maps their first `reg` pairs.
That confirms a static property-to-source mapping relationship. It does not
prove runtime register access, a complete AIC interrupt implementation,
interrupt specifier decoding, IRQ routing, EOI behavior, timer counter
semantics, or a valid runtime timebase frequency. The static CPU0
`timebase-frequency` property is zero in the extracted IPSW DeviceTree, so
the runtime value remains unknown.
