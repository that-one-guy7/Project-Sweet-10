# iPhone9,1 device-tree property inventory

Purpose: track the properties consumed by the pinned XNU source and the evidence
needed to assess the iPhone7 target. This is an evidence template, not a device-tree
dump or a set of values to inject.

## Rules

- Record property names, data types, units, consumer, source URL/revision, and confidence.
- Do not guess addresses, interrupt IDs, frequencies, memory ranges, or device compatibles.
- Do not commit full device-tree dumps, unique device identifiers, calibration values,
  or other private device data.
- An XNU consumer does not prove that the target's device tree contains that property.
- Keep unknown fields marked unknown until supported by a trustworthy source.

## Property inventory

| Node/path | Property | XNU consumer | Expected meaning/type from source | iPhone9,1 evidence | Status |
|---|---|---|---|---|---|
| `/cpus` children | `state` | `pe_identify_machine.c` | CPU state string; source selects `running` | `cpu0=running` (`reg=0`); `cpu1=waiting` (`reg=1`) in the hash-verified 19H422 base tree | Verified in static artifact; final runtime state still unverified |
| `/cpus/cpu0` | `timebase-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Present, 8-byte value `0` in static 19H422 component | Static value verified; usable runtime frequency unknown |
| `/cpus/cpu0` | `bus-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Present, 8-byte value `0` in static component | Static value verified; usable runtime frequency unknown |
| `/cpus/cpu0` | `memory-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Present, 8-byte value `0` in static component | Static value verified; usable runtime frequency unknown |
| `/cpus/cpu0` | `peripheral-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Present, 8-byte value `0` in static component | Static value verified; usable runtime frequency unknown |
| `/cpus/cpu0` | `fixed-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Present, 8-byte value `0` in static component | Static value verified; usable runtime frequency unknown |
| `/cpus/cpu0` | `clock-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Present, 8-byte value `0` in static component | Static value verified; usable runtime frequency unknown |
| `/arm-io` | `device_type` / `compatible` | `pe_identify_machine.c` | SoC device type and compatible string | `t8010-io`; `arm-io,t8010` | Verified in hash-verified static artifact |
| `/arm-io` | `ranges` | `pe_identify_machine.c` | Address-range data used to derive SoC physical base | 48 bytes; XNU's `ranges_prop[1]` interpretation yields `0x0000000200000000` | Verified for static artifact and pinned XNU consumer; runtime tree still to verify |
| `/pram` | `reg` | `pe_init.c` | Region address/size cells used for panic area | 16 bytes, all zero in static component | Static placeholder; not a usable panic region |
| `/chosen` | `embedded-panic-log-size` | `pe_init.c` | 32-bit panic log length | Property absent from static component | Absent in base tree; iBoot may populate final runtime tree |

## Additional properties parsed from the target component

The independently parsed `19H422` base tree also contains:

| Node/path | Property | Parsed value | Evidence status |
|---|---|---|---|
| `/arm-io/aic` | `compatible`, `device_type` | `aic,1`; `interrupt-controller` | Verified |
| `/arm-io/aic` | `interrupt-controller` | `master` | Verified |
| `/arm-io/aic` | `#interrupt-cells`, `#main-cpus`, `aic-version`, `#shared-timestamps` | `1`, `2`, `2`, `16` | Verified as static tree properties |
| `/arm-io/aic` | `reg` | First pair offset `0x0e100000`, length `0x8000`; second pair offset `0x0e108000`, length `0x1000` | Verified; first pair is what the pinned generic XNU mapper reads |
| `/arm-io/aic-timebase` | `device_type`, `reg` | `timer`; offset `0x0e108000`, length `0x1000` | Verified as static tree properties |
| `/cpus/cpu0`, `/cpus/cpu1` | `reg`, `cpu-id` | CPU0 = `0`; CPU1 = `1` | Verified as static tree properties |
| `/memory`, `/vram` | `reg` | All-zero values in the static component | Static values verified; not a runtime memory map |

The pinned XNU `pe_arm_get_soc_base_phys()` selects the second 64-bit word of `/arm-io/ranges`; `pe_arm_map_interrupt_controller()` reads the first `reg` pair of the `interrupt-controller=master` node and the first pair of the `device_type=timer` node. Based on those source accesses, the corresponding mapping inputs are `0x000000020e100000` / `0x8000` for the AIC and `0x000000020e108000` / `0x1000` for the timer. These are source-correlated artifact values, not proof of a functioning controller or timer.

The `/arm-io/spi2/multi-touch` node is present with `compatible=hid-transport,k1`; its parent advertises `#address-cells=1` and `#size-cells=7`. Its 32-byte `reg` property must not be treated as two 64-bit address/size pairs.

See the [parsed DeviceTree audit](../docs/iphone91-19h422-parsed-devicetree-audit.md) for node details, the XNU source cross-check, and the runtime-value limitations.

## Artifact and structural evidence

Public firmware metadata establishes that
`Firmware/all_flash/DeviceTree.d10ap.im4p` component records exist for
`iPhone9,1` / CPID `0x8010` / BDID `0x08` in builds `15A372`,
`15A402`, and `19A346`. Those older entries have separate per-build
digest pairs.

For iOS 15.8.8 build `19H422`, the supplied standalone BuildManifest and
D10AP DeviceTree IM4P have been independently hashed. Their SHA-256 values
match the pinned Orchard metadata. The component SHA-384 also matches the
48-byte `Digest` value in the D10AP BuildManifest identities. The full IPSW
archive itself was not supplied and its archive hash remains unverified.

The supplied component parses as an IM4P `dtre` wrapper with description
`EmbeddedDeviceTrees-6331.140.11.700.2` and an LZFSE-family `bvx2`
payload. The decompressed DeviceTree has now been independently parsed:
227 nodes including root, with no trailing bytes.
A separate public 19H422 survey file reports 226 nodes, two
`apple,hurricane-zephyr` CPU nodes, an `arm-io,t8010` node, an
`aic,1` child, and an `aic-timebase` child. Its script emits node names,
compatible strings, and register-pair count/size summaries only. It does
not publish raw `reg` values, `ranges`, interrupt properties, timer
`device_type`, or CPU clock/topology values. Project Sweet-10 has not
independently parsed the raw component. Its printed `reg` totals are not
validated extents: the generator assumes fixed 16-byte little-endian
64-bit address/size pairs and does not inspect parent cell-count properties.
See the [survey methodology review](../docs/iphone91-19h422-survey-methodology-review.md).

Under the generic Devicetree specification, the parent node's
`#address-cells` and `#size-cells` determine the number of 32-bit cells
used for each child's `reg` address and size. The Apple payload's exact
encoding must be confirmed independently before promoting any such value.

See [19H422 DeviceTree structure audit](../docs/iphone91-19h422-device-tree-structure-audit.md)
and [public iPhone9,1 stock DeviceTree artifact evidence](../docs/iphone91-stock-firmware-device-tree-evidence.md).
Selected property values are now populated from the independently parsed
19H422 component and cross-checked with the pinned XNU 8796 consumers. Keep
runtime-dependent fields explicitly unresolved: CPU clocks are zero in this
static tree, `/memory` and `/pram` regions are zero, and
`/chosen/embedded-panic-log-size` is absent.

## Next research questions

1. Which of these properties are actually present in the relevant iPhone9,1 platform
   description, and what source supports that claim?
2. Are property cell widths, endianness, and address/size encodings consistent with the
   assumptions made by this XNU revision?
3. Which properties are mandatory for early initialization, and which are optional?
4. Which platform values are provided by the boot environment rather than static source?
5. Are any consumers conditional on build flags or platform-expert selection?

Some individual properties are now verified against the static target artifact and the relevant generic XNU consumers. This does not establish final runtime values: iBoot's `UpdateDeviceTree()` may populate properties absent or zero in the embedded component. The public survey remains secondary evidence and its fixed-width `reg` size totals remain heuristics.

See the [19H422 artifact verification record](../docs/iphone91-19h422-artifact-verification.md), [parsed DeviceTree audit](../docs/iphone91-19h422-parsed-devicetree-audit.md), and run `tools/inspect_apple_dt.py` for a privacy-filtered summary.
