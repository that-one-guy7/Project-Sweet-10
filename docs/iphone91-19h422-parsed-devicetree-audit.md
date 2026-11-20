# iPhone9,1 / D10AP / 19H422 parsed DeviceTree audit

## Scope and provenance

Project Sweet-10 independently decompressed and parsed the user-supplied `DeviceTree.d10ap.raw` produced from the SHA-256-verified `DeviceTree.d10ap.im4p` component in the iPhone 7 Global iOS 15.8.8 (`19H422`) IPSW.

| Measurement | Result |
|---|---|
| Input filename | `DeviceTree.d10ap.raw` |
| Input length | 160,572 bytes |
| Input SHA-256 | `39331154d60f05923da0b2c5dc9ac6395da6a8276f0952e997dbdcfa81c2420e` |
| Parsed nodes including root | 227 |
| Descendant nodes excluding root | 226 |
| Bytes consumed | 160,572 |
| Trailing bytes | 0 |
| Parse result | Complete |

The count of 226 in the earlier public survey is consistent with its `walk()` function not emitting the root node. Project Sweet-10 counts the root explicitly, giving 227.

The parser follows the public Apple flattened-tree layout used by the pinned Ios-emul survey parser: little-endian node property/child counts, fixed 32-byte property-name fields, four-byte property-value padding, and recursive child nodes. The new project parser adds explicit bounds checks, duplicate-property checks, full-input-consumption validation, tests, and an allowlist-only output mode.

**Privacy warning:** the original raw tree contains device-specific fields and machine-specific blobs, including identifiers, network-address fields, boot metadata, and NVRAM-related data. The raw tree is intentionally not committed to GitHub. The checked-in JSON summary is allowlist-filtered and omits arbitrary property values and unique identifiers.

## Device and SoC identification

The root properties identify:

- `compatible`: `D10AP`, `iPhone9,1`, `AppleARM`
- `model`: `iPhone9,1`
- `target-type`: `D10`
- root `device_type`: `bootrom`

The `/arm-io` node identifies:

- `compatible`: `arm-io,t8010`
- `device_type`: `t8010-io`
- `#address-cells`: 2
- `#size-cells`: 2

This is direct target-side evidence for the A10/T8010 platform identity. It does not provide an XNU 8796 T8010 machine configuration; the missing T8010 normal ARM64 machine profile remains a separate source/build blocker.

## CPU nodes

The `/cpus` parent advertises one address cell and zero size cells. It contains two CPU children:

| Node | `reg` | `cpu-id` | `state` | `compatible` |
|---|---:|---:|---|---|
| `/cpus/cpu0` | 0 | 0 | `running` | `apple,hurricane-zephyr`, `ARM,v8` |
| `/cpus/cpu1` | 1 | 1 | `waiting` | `apple,hurricane-zephyr`, `ARM,v8` |

This is what the extracted tree describes. It must not be extrapolated into a claim about the total physical core count, cluster topology, or final enabled CPU count.

`/cpus/cpu0` contains 8-byte values for `timebase-frequency`, `bus-frequency`, `memory-frequency`, `peripheral-frequency`, `fixed-frequency`, and `clock-frequency`. Every one of those values is zero in this static component. `/cpus/cpu1` does not provide those frequency properties in the extracted tree.

### Why the zero clock fields matter

Pinned XNU `xnu-8796.141.3` `pe_identify_machine()`:

1. Finds `/cpus`.
2. Iterates its child nodes.
3. Skips CPUs unless `state` is `running`.
4. Reads the running CPU's frequency properties.
5. For an 8-byte property, reads it as a native `uint64_t`.

The function initializes fallback clock defaults before examining the tree, but then overwrites those fields when the properties are present. The values in this static tree are present and zero, so this file alone does not supply usable clock frequencies to that code path.

This is a concrete reason not to treat the extracted IPSW component as the final runtime DeviceTree. The values may be supplied or replaced by a later boot stage, but Project Sweet-10 has not inspected a final iBoot/PongoOS handoff tree. The runtime values remain **unknown**.

Source: [pinned XNU `pe_identify_machine.c`](https://github.com/apple-oss-distributions/xnu/blob/1b191cb58250d0705d8a51287127505aa4bc0789/pexpert/arm/pe_identify_machine.c#L50-L165).

## ARM-IO ranges and SoC physical base

The `/arm-io` node advertises two address cells and two size cells. Its 48-byte `ranges` property is recorded below as six little-endian 64-bit words, grouped into two `(child address, parent address, size)` entries:

| Entry | Child address | Parent address | Size |
|---|---:|---:|---:|
| 0 | `0x0000000000000000` | `0x0000000200000000` | `0x0000000100000000` |
| 1 | `0x0000000600000000` | `0x0000000600000000` | `0x0000000200000000` |

The pinned XNU function `pe_arm_get_soc_base_phys()` obtains `/arm-io`'s `ranges` property as a `uintptr_t` array and assigns `ranges_prop[1]` to `gPESoCBasePhys`. Under the native 64-bit interpretation used by that ARM64 source, the value selected from this tree is:

`gPESoCBasePhys = 0x0000000200000000`

This is a source-to-artifact comparison, not an instruction to write or map hardware registers on a device.

Source: [pinned XNU `pe_arm_get_soc_base_phys()`](https://github.com/apple-oss-distributions/xnu/blob/1b191cb58250d0705d8a51287127505aa4bc0789/pexpert/arm/pe_identify_machine.c#L180-L194).

## AIC interrupt controller and timer

The extracted `/arm-io/aic` node reports:

- `compatible`: `aic,1`
- `device_type`: `interrupt-controller`
- `interrupt-controller`: `master`
- `#address-cells`: 0
- `#interrupt-cells`: 1
- `#main-cpus`: 2
- `aic-version`: 2
- `#shared-timestamps`: 16

Its 32-byte `reg` property is four little-endian 64-bit words, representing two entries:

| Entry | ARM-IO-relative offset | Length |
|---|---:|---:|
| AIC register window | `0x000000000e100000` | `0x8000` |
| Additional window | `0x000000000e108000` | `0x1000` |

The `/arm-io/aic-timebase` node reports `device_type = timer` and a single `reg` entry:

- ARM-IO-relative offset: `0x000000000e108000`
- Length: `0x1000`

The pinned XNU `pe_arm_map_interrupt_controller()` searches for `interrupt-controller = "master"`, reads the first `reg` pair and maps `soc_phys + reg[0]` for `reg[1]` bytes. It then searches for `device_type = "timer"` and maps that node's first `reg` pair in the same way.

Using the `gPESoCBasePhys` value selected by XNU from this tree, the address inputs to those source-level mappings resolve to:

| XNU mapping input | Derived physical address | Length |
|---|---:|---:|
| AIC first register window | `0x000000020e100000` | `0x8000` |
| AIC timebase window | `0x000000020e108000` | `0x1000` |

The mapping inputs are supported by the tree bytes and the pinned XNU pointer accesses. This does **not** establish that the AIC driver is fully compatible with the selected XNU revision, that interrupt routing is complete, or that the machine can boot.

Source: [pinned XNU `pe_arm_map_interrupt_controller()` and timer setup](https://github.com/apple-oss-distributions/xnu/blob/1b191cb58250d0705d8a51287127505aa4bc0789/pexpert/arm/pe_identify_machine.c#L523-L590).

## Memory and panic-region properties: static values are incomplete

The extracted component has the following static contents:

- `/memory/reg`: 8 bytes, all zero.
- `/pram/reg`: 16 bytes, all zero.
- `/vram/reg`: 16 bytes, all zero.
- `/chosen/embedded-panic-log-size`: absent.
- `/chosen/memory-map`: has `MemoryMapReserved-*` entries, but this component does not establish the final runtime memory map required by a booted kernel.

Pinned XNU `PE_get_panic_region()` requires `/pram/reg` and `/chosen/embedded-panic-log-size`. Its source comment explicitly says those panic-region properties are populated by `UpdateDeviceTree()` in iBoot. The required `/chosen` property is absent from this extracted component, and the `/pram` values are zero.

Therefore, this static IPSW DeviceTree is **not sufficient evidence for the final memory map or panic-log handoff**. The project must separately establish the final DeviceTree and `boot_args` that would be supplied to XNU.

Sources:
- [pinned XNU `PE_get_panic_region()`](https://github.com/apple-oss-distributions/xnu/blob/1b191cb58250d0705d8a51287127505aa4bc0789/pexpert/arm/pe_init.c#L101-L142)
- [pinned XNU ARM64 `boot_args`](https://github.com/apple-oss-distributions/xnu/blob/1b191cb58250d0705d8a51287127505aa4bc0789/pexpert/pexpert/arm64/boot.h#L50-L73)

## Display and input node inventory

The tree also identifies these target nodes:

| Path | Evidence from the tree | Interpretation limit |
|---|---|---|
| `/arm-io/disp0` | `compatible = disp0,t8010`; `device_type = display-subsystem`; `reg` contains nine entries | Node presence and resource descriptions only; no display driver or mode is validated |
| `/arm-io/mipi-dsim/lcd` | `compatible = lcd,pinot`; `device_type = lcd` | Panel identification string only; no initialization sequence is established |
| `/arm-io/spi2` | `compatible = spi-1,samsung`; `device_type = spi`; its own `reg` window is present | Controller identity only; bus configuration is not validated |
| `/arm-io/spi2/multi-touch` | `compatible = hid-transport,k1`; `device_type = multi-touch`; `force-supported` marker present | HID transport/node presence only; no touchscreen protocol or working input path is proven |
| `/arm-io/i2c0/lm3539` | `compatible = backlight,lm3539`; `device_type = backlight` | Backlight component identity only |

A useful parser warning appears in the touchscreen path: the parent `/arm-io/spi2` advertises `#address-cells = 1` and `#size-cells = 7`, and the child `multi-touch` `reg` field is 32 bytes. This is not a normal 16-byte `(u64 address, u64 size)` record. Do not apply the earlier third-party survey's fixed-width `reg` size heuristic to this node.

## What this advances

**Now verified from the exact target artifact:**

- Root identity and A10/T8010-compatible `/arm-io`.
- Two CPU nodes and their static `state`/`reg` values.
- `/arm-io/ranges` and the SoC base selected by the pinned XNU source.
- AIC controller metadata and register windows consumed by the generic XNU mapper.
- AIC-timebase node and its register window consumed by the generic XNU mapper.
- Display, LCD, SPI touchscreen, and backlight node identities.

**Still open:**

1. Whether a final boot-time DeviceTree has non-zero clock, RAM, panic, and memory-map values.
2. The full A10 CPU topology, feature registers, secondary CPU startup contract, and interrupt routing.
3. A10 board configuration and machine selection in the pinned XNU 8796 build.
4. The exact XNU entry state, `boot_args` population, DeviceTree handoff lifetime, memory ownership, and cache/MMU state for a custom loader.
5. Full AIC/timer behavior and peripheral-driver compatibility.
6. A reproducible XNU baseline build and later userland compatibility.

The static DeviceTree audit does not change the earlier finding that public XNU 8796 omits T8010 from its normal ARM64 machine allowlist. Do not patch a made-up T8010 profile from these values alone.

## Reproduction

The privacy-filtered inspector is:

`tools/inspect_apple_dt.py`

Run from the repository root:

```bash
python3 tools/inspect_apple_dt.py DeviceTree.d10ap.raw \
  --output research/iphone91-19h422-devicetree-summary.json
```

The output includes only explicitly allowlisted paths and property names. It does not dump the full tree or emit unique IDs, MAC addresses, NVRAM proxy data, boot nonce, or random seed.

Run the test suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

No raw DeviceTree binary is committed. No device was connected, updated, restored, or booted during this analysis.
