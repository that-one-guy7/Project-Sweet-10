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
payload. The compressed payload has not yet been decompressed or parsed.
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
**All individual property-value rows above remain Unknown.** Node presence
or a third-party digest does not populate a property-value cell.

## Next research questions

1. Which of these properties are actually present in the relevant iPhone9,1 platform
   description, and what source supports that claim?
2. Are property cell widths, endianness, and address/size encodings consistent with the
   assumptions made by this XNU revision?
3. Which properties are mandatory for early initialization, and which are optional?
4. Which platform values are provided by the boot environment rather than static source?
5. Are any consumers conditional on build flags or platform-expert selection?

No individual property values are promoted yet. Project Sweet-10 has
independently verified the extracted artifact hashes, but the payload still
needs to be decompressed and parsed, and every property must be checked
against the relevant XNU consumer. The public 19H422 structural survey is
secondary evidence and does not expose the required raw values.

See the [19H422 artifact verification record](../docs/iphone91-19h422-artifact-verification.md) and run the read-only validator at `tools/verify_d10ap_19h422_artifacts.py`.
