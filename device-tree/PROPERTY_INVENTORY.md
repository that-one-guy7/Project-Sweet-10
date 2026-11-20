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
| `/cpus` children | `state` | `pe_identify_machine.c` | CPU state string; source selects `running` | Not collected | Unknown |
| `/cpus` children | `timebase-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Not collected | Unknown |
| `/cpus` children | `bus-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Not collected | Unknown |
| `/cpus` children | `memory-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Not collected | Unknown |
| `/cpus` children | `peripheral-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Not collected | Unknown |
| `/cpus` children | `fixed-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Not collected | Unknown |
| `/cpus` children | `clock-frequency` | `pe_identify_machine.c` | 32- or 64-bit frequency value | Not collected | Unknown |
| node named `arm-io` | `device_type` | `pe_identify_machine.c` | String copied as SoC device type | Not collected | Unknown |
| node named `arm-io` | `ranges` | `pe_identify_machine.c` | Address-range data used to derive SoC physical base | Not collected | Unknown |
| `pram` | `reg` | `pe_init.c` | Region address/size cells used for panic area | Not collected | Unknown |
| `/chosen` | `embedded-panic-log-size` | `pe_init.c` | 32-bit panic log length | Not collected | Unknown |

## Artifact identity evidence (metadata only)

Public firmware metadata now establishes that `Firmware/all_flash/DeviceTree.d10ap.im4p`
component records exist for `iPhone9,1` / CPID `0x8010` / BDID `0x08`
in builds `15A372` (11.0), `15A402` (11.0.1), and `19A346` (15.0).
The checked records include separate `DeviceTree` and `RestoreDeviceTree`
names and per-build digest strings. This establishes artifact identity only;
no DeviceTree payload or individual property value was parsed.

A newer stock iPhone 7 Global reference is listed as iOS 15.8.8 build
`19H422` for `iPhone9,1`. The checked fwkeydb snapshot does not include a
`19H422` record, so its DeviceTree digest and contents remain unknown.

See [public iPhone9,1 stock DeviceTree artifact evidence](../docs/iphone91-stock-firmware-device-tree-evidence.md).
All property rows above remain **Unknown** pending parsing and provenance checks.

## Next research questions

1. Which of these properties are actually present in the relevant iPhone9,1 platform
   description, and what source supports that claim?
2. Are property cell widths, endianness, and address/size encodings consistent with the
   assumptions made by this XNU revision?
3. Which properties are mandatory for early initialization, and which are optional?
4. Which platform values are provided by the boot environment rather than static source?
5. Are any consumers conditional on build flags or platform-expert selection?

No individual property values are supplied because the project has not yet
parsed an authenticated, build-matched iPhone9,1 DeviceTree. Artifact-level
metadata is now available; see the section above for its limits.
