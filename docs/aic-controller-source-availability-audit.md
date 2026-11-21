# AIC interrupt-controller source availability audit

## Scope

This note checks the public XNU source boundary for the AIC interrupt
controller path against the target iPhone9,1 / D10AP / 19H422 static
DeviceTree evidence already recorded in
[the parsed DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md).

This is host-side source and metadata research only. It does not describe
register writes, interrupt enabling, device operations, kernel boot, or
firmware changes. The physical iPhone 7 remains on iOS 12.1.4.

## Target facts already established from 19H422

The parsed static target DeviceTree reports:

- \`/arm-io/aic\`: \`compatible = aic,1\`,
  \`device_type = interrupt-controller\`,
  \`interrupt-controller = master\`, \`#interrupt-cells = 1\`,
  \`#main-cpus = 2\`, \`aic-version = 2\`.
- First \`reg\` entry: ARM-IO-relative offset \`0x0e100000\`,
  length \`0x8000\`.
- Second \`reg\` entry: ARM-IO-relative offset \`0x0e108000\`,
  length \`0x1000\`.
- \`/arm-io/aic-timebase\`: \`device_type = timer\`,
  \`reg\` offset \`0x0e108000\`, length \`0x1000\`.
- The pinned XNU DeviceTree consumer selects static SoC base
  \`0x0000000200000000\`, so the first mapping inputs are
  \`0x000000020e100000\` and \`0x000000020e108000\`.

These facts are already target-confirmed static IPSW evidence. They do not
show which interrupt-controller service successfully attaches at runtime,
how interrupt specifiers are decoded, how interrupts are distributed to
CPUs, or whether timer callbacks and EOI are wired correctly.

## What public XNU 8796 provides

The complete pinned XNU 8796.141.3 source tree contains these relevant
pieces:

1. **ARM64 AIC header:** \`pexpert/pexpert/arm64/AIC.h\` defines volatile
   32-bit read/write helpers using \`pic_base\` and the two
   \`kAICMainTimLo\` / \`kAICMainTimHi\` offsets. It does not contain the
   AIC interrupt source, target-routing, acknowledge, enable, or mask
   register map present in the older ARM header.
2. **Older ARM AIC header:** \`pexpert/pexpert/arm/AIC.h\` contains a larger
   set of AIC register constants, including acknowledge, IPI, timer, and
   interrupt-mask/target register names. This is a legacy ARM header; its
   existence is not proof that its definitions are the correct ARM64
   T8010 controller implementation.
3. **Generic platform-expert mapper:** \`pe_arm_map_interrupt_controller()\`
   searches the DeviceTree for \`interrupt-controller = master\`, maps its
   first \`reg\` pair to \`gPicBase\`, finds a node with
   \`device_type = timer\`, and maps its first \`reg\` pair to
   \`gTimerBase\`. This is address-window mapping, not a complete AIC
   driver.
4. **ARM64 timer callback setup:** in \`pe_arm_init_timer()\`, the
   \`__arm64__\` branch selects \`empty_funcs\` for \`tbd_funcs\`.
   The local \`eoi_addr\` and \`eoi_value\` are initialized to zero, and
   \`ml_init_timebase()\` receives those values. This source path does not
   provide a T8010-specific AIC FIQ/decrementer callback implementation.
5. **Generic IOKit interrupt framework:** \`IOInterruptController\` is an
   abstract IOKit service interface with operations such as vector
   registration, enable/disable, and IPI methods. Its generic implementation
   supplies framework behavior, not the SoC-specific AIC register logic.

Pinned source links:

- [ARM64 AIC helper header, XNU 8796.141.3](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/AIC.h)
- [ARM AIC register header, XNU 8796.141.3](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm/AIC.h)
- [DeviceTree mapping and timer setup, XNU 8796.141.3](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/arm/pe_identify_machine.c#L523-L640)
- [Generic IOKit interrupt-controller interface](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/IOKit/IOInterruptController.h)
- [Generic IOKit interrupt-controller implementation](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/Kernel/IOInterruptController.cpp)

## Evidence of a separate AppleInterruptController component

The public XNU 8796 source has two references to the name
\`AppleInterruptController\`:

- \`bsd/dev/dtrace/fbt_blacklist.c\` lists
  \`com.apple.driver.AppleInterruptController\` in the ARM driver blacklist.
- \`tools/lldbmacros/scheduler.py\` reads a debugger object as
  \`AppleInterruptController *\` and inspects its AIC base/interrupt state.

These are debugger and diagnostic references, not the implementation
source. They suggest that the Apple kernel environment has a separate
interrupt-controller driver component, but they do **not** prove that the
same bundle is present in the iPhone7 19H422 KernelCache or that it matches
the static \`aic,1\` node. The actual driver implementation is not present
in the reviewed public XNU tree paths.

References:

- [XNU DTrace driver blacklist](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/bsd/dev/dtrace/fbt_blacklist.c#L291-L295)
- [XNU LLDB scheduler diagnostics](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/tools/lldbmacros/scheduler.py#L65-L85)

## DeviceTree/header offset convention still needs reconciliation

The ARM64 AIC header comment says the AIC timebase register base in the
DeviceTree is set up as \`AIC_BASE + 0x1000\`. The parsed 19H422 tree,
however, records the first \`aic\` \`reg\` window at offset
\`0x0e100000\`, a second window at \`0x0e108000\`, and the separate
\`aic-timebase\` node at \`0x0e108000\`.

The meaning of the header's \`AIC_BASE\` label and its relationship to the
two target DeviceTree windows has not been independently resolved. Do not
collapse these addresses into one assumed base or derive a driver layout
from the comment alone. Keep the raw DeviceTree tuple boundaries and XNU
mapping inputs as recorded until the relevant private/target driver contract
is available.

## What is still unknown

- Whether the 19H422 KernelCache contains a bundle named
  \`com.apple.driver.AppleInterruptController\`.
- Whether that bundle's personalities match \`aic,1\` or another compatible
  string, and which provider class it expects.
- Whether \`AppleT8010\`, \`AppleT8010PMGR\`, \`AppleT8010CLPC\`, or another
  target KEXT owns any part of the interrupt-controller or timer interface.
- The complete target interrupt specifier format, IRQ namespace, trigger
  modes, priorities, affinity/routing and per-CPU delivery behavior.
- The acknowledge/EOI path and relationship between the AIC timer node and
  architectural \`CNTVCT_EL0\` / \`CNTV_TVAL_EL0\` handling.
- A non-zero, runtime-supplied \`timebase-frequency\` and any
  SoC-specific timer callback requirements.
- Whether the target's private Apple KEXT implementation is compatible with
  the public XNU 8796 IOKit interfaces.

## Next bounded host-side inspection

The next useful artifact is the **target 19H422 KernelCache KEXT JSON
filtered for**:

- \`AppleInterruptController\`
- \`AppleARMPlatform\`
- \`AppleT8010\`
- \`AppleT8010PMGR\`
- \`AppleT8010CLPC\`
- \`AppleT8010SOCTuner\`

For every matching record, preserve the bundle identifier, version,
personality names, provider class, \`IONameMatch\`, and any
\`IOProviderClass\` / interrupt-related properties that the existing JSON
actually contains. An absent JSON field is not proof of absence from the
KEXT binary or from runtime behavior. Do not dump unrelated private
DeviceTree/NVRAM values or upload full KernelCache/firmware binaries.

The repository already records the local read-only inventory command and
the extracted KernelCache path in
[the 19H422 KernelCache KEXT inventory](iphone91-19h422-kernelcache-kext-inventory.md).
The next comparison should determine whether the candidate controller
bundle and its personality are in the target-native KernelCache before
any AIC implementation work is proposed.

## Decision

**No AIC driver implementation is ready to be written from the current
public-source evidence.** The target's static AIC nodes/windows are known,
and XNU's generic mapper is understood. The controller implementation and
runtime interrupt/timer contract remain unverified. First inspect the
target-native KernelCache personalities for the controller and platform
bundles; then decide whether the next source task belongs in XNU
platform-expert code, an IOKit controller component, or a separate
vendor-specific driver boundary.

M6 remains in progress and M7/SpringBoard has not started. The physical
iPhone 7 remains on iOS 12.1.4.
