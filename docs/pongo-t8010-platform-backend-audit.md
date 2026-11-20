# PongoOS T8010 platform-backend source audit

## Scope and source pin

This audit examines the public PongoOS implementation at
[`4c9b7541629234147fcc778f0ce4162482aaccef`](https://github.com/checkra1n/PongoOS/commit/4c9b7541629234147fcc778f0ce4162482aaccef)
for concrete T8010-specific platform integration. It extends the earlier finding
that PongoOS recognizes the `t8010` SoC name: the pinned source also registers a
T8010 Hardware Abstraction Layer (HAL) platform driver and supplies resources
consumed by the USB, AES, and Reconfig Engine support paths.

This is a source audit only. It does not show PongoOS running on the user's
iPhone9,1, does not validate any hardware access at runtime, and is not a device
runbook.

## 1. DeviceTree-derived SoC selection

PongoOS's cached entry code derives the DeviceTree pointer from the incoming
Apple `boot_args.deviceTreeP`, reads `arm-io/ranges` for its I/O base, and
reads `arm-io/device_type` to derive its internal SoC name/number. Its mapping
contains a `t8010` case that sets `socnum = 0x8010`.

The independently parsed iPhone9,1 / D10AP / 19H422 static DeviceTree identifies
`/arm-io/device_type = t8010-io`. This is consistent with the string-to-number
selection path in the reviewed PongoOS source.

Important distinction: PongoOS HAL later assigns `_gPlatform.cpid = socnum`.
The T8010 platform driver's `probe` therefore matches the SoC number derived
from the supplied DeviceTree. The inspected HAL code does not independently
read the BootROM CPID fuse during this selection. This backend match is therefore
a source-level DeviceTree/SoC match, not an independent hardware identity check.

Sources: [PongoOS `entry.c`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/kernel/entry.c#L123-L156),
[HAL `hal.c`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/drivers/hal/hal.c#L180-L210),
and the [parsed iPhone9,1 DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md).

## 2. A registered A10/T8010 HAL platform driver exists

The pinned PongoOS source contains
[`src/drivers/plat/t8010.c`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/drivers/plat/t8010.c#L29-L62).
It:

- defines a platform probe for `device->cpid == 0x8010`;
- names the platform `Apple A10 (T8010)`;
- registers that platform driver with `hal_register_platform_driver()`;
- provides a `usb_regs` platform value to callers.

The HAL's initialization sequence registers platform-driver providers, sets its
platform CPID field from `socnum`, probes for a matching platform driver, and
panics if none matches. The T8010 driver is therefore an active platform
provider in this codebase, not merely a comment or a string in an unrelated
test.

The T8010 provider's USB resource record contains these values:

| Resource field | PongoOS source value |
|---|---:|
| `reg1` | `0x0e080268` |
| `reg2` | `0x0e080270` |
| `reg3` | `0x0e080290` |
| `otg_irq` | `241` |

The Synopsys OTG driver requests `usb_regs` from HAL, adds the first three
values to its DeviceTree-derived `gIOBase`, and uses `otg_irq` when it
registers the USB task on the interrupt. This establishes a concrete
T8010-specific USB resource path in the source.

It does not prove that the offsets/IRQ are correct on the user's physical
device, that the controller initializes successfully, or that USB transfers
work in a real PongoOS session.

Sources: [T8010 platform driver](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/drivers/plat/t8010.c#L29-L62),
[HAL selection](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/drivers/hal/hal.c#L180-L218),
and [Synopsys OTG resource use](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/drivers/usb/synopsys_otg.c#L1797-L1863).

## 3. Additional T8010-specific support paths

The pinned source contains two further SoC-specific paths relevant to PongoOS
initialization:

- **AES dispatch:** `aes_init()` includes SoC `0x8010` in its AES-A9
  implementation path. The AES-A9 initializer selects a T8010 clock register
  offset of `0x0e080230` relative to `gIOBase`. The PongoOS main task calls
  `aes_init()` during its initialization sequence.
- **Reconfig Engine configuration:** `recfg_soc.c` contains a configuration
  record for SoC `0x8010`. The `recfg_soc_setup()` routine selects a record
  by `socnum`, and the main task invokes that setup during initialization.

These are source-level implementation paths. They are not evidence that the
iOS kernel's AES, SEP, or Reconfig Engine dependencies are satisfied, and this
audit does not reproduce or prescribe any security-processor operation.

Sources: [PongoOS main-task initialization](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/kernel/main_task.c#L53-L85),
[AES SoC dispatch](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/drivers/aes/aes.c#L149-L172),
[T8010 AES clock selection](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/drivers/aes/aes_a9.c#L68-L88),
and [T8010 Reconfig Engine configuration](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/drivers/recfg/recfg_soc.c#L88-L98).

## 4. Updated assessment for Project Sweet-10

The evidence supports a more specific conclusion than the previous
"recognizes T8010" wording:

- The selected PongoOS revision contains a T8010-specific HAL platform driver.
- The driver is selected through PongoOS's DeviceTree-derived `socnum`.
- It provides USB register offsets and an OTG interrupt number to the generic
  Synopsys USB driver.
- The same revision includes additional T8010 cases in its AES and Reconfig
  Engine code paths.

Therefore, **PongoOS has meaningful source-level A10/T8010 platform support
that makes it a plausible pre-boot environment to investigate for iPhone9,1**.
Calling PongoOS "only a generic shell with no T8010 backend" would be inaccurate.

The evidence does **not** establish:

- that this exact PongoOS revision has been built and executed on the user's
  iPhone9,1;
- that the iPhone9,1 USB controller and interrupt setup works at runtime;
- that every PongoOS subsystem or driver supports this particular board;
- that PongoOS constructs the final runtime DeviceTree or memory map needed by
  XNU;
- that its `bootr` raw-payload path is a complete custom XNU loader;
- that XNU 8796 has a T8010 board configuration or that iOS 16 / 20H392 can
  reach SpringBoard on iPhone7.

PongoOS pre-boot viability and Sweet-10 XNU viability remain separate gates.

## 5. Project status and next evidence

| Question | Source-backed status |
|---|---|
| Does PongoOS map `t8010` to SoC number `0x8010`? | Yes, from the supplied DeviceTree |
| Is there a registered T8010 HAL platform driver? | Yes |
| Does that driver provide USB-specific resources? | Yes; source values and consumer path documented |
| Are there additional T8010 AES/Recfg code paths? | Yes |
| Has the exact pinned PongoOS build been run on this iPhone9,1? | Not verified |
| Has USB operation been observed on this device? | Not verified |
| Does this solve the XNU 8796 T8010 machine-profile gap? | No |
| Does this solve the custom XNU loader/boot-argument values? | No |

The next validation, if hardware work is later approved, is a separate controlled
PongoOS-only assessment that records the exact build revision, platform name,
and non-sensitive initialization results. That would test the pre-boot stage
without treating a successful shell as proof of an XNU boot. No such test is
performed or authorized by this document.

**Current decision:** update the project record to say that a T8010 PongoOS
backend exists in source. Keep PongoOS-on-this-device runtime validation,
custom XNU image loading, final runtime boot arguments/DeviceTree, and XNU
8796 A10/T8010 platform support open.
