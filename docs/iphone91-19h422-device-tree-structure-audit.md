# iPhone9,1 / D10AP / 19H422 DeviceTree structure audit

## Summary

A public DeviceTree survey file exists for the exact target and stock build:

- Product: `iPhone9,1`
- Board: `d10ap` / D10AP
- SoC-compatible string in the survey: `arm-io,t8010`
- Firmware: iOS 15.8.8, build `19H422`
- Survey header: root compatible `D10AP, iPhone9,1, AppleARM`
- Reported node count: 226

The survey provides a useful **structural inventory**. It shows that the tree has two CPU nodes, an `arm-io` node compatible with T8010, an `aic` child, and an `aic-timebase` child. It does not publish raw property bytes, physical register addresses, interrupt specifiers, clock values, or complete CPU topology data.

The extracted BuildManifest and D10AP DeviceTree component have now been independently hashed by Project Sweet-10. Both SHA-256 values match the pinned Orchard metadata, and the component SHA-384 matches the D10AP BuildManifest Digest field. The IM4P wrapper and LZFSE marker are verified, but the compressed payload has not yet been decompressed or parsed; no node-property values are promoted. See the [artifact verification record](iphone91-19h422-artifact-verification.md).

## Source A: public 19H422 tree survey

The file
[`iPhone9,1-d10ap-19H422.txt`](https://github.com/vytska69/Ios-emul/blob/4e2afb56f076473c54c720a607bb44cffc0ab04e/research/devicetrees/iPhone9,1-d10ap-19H422.txt)
is in the public `vytska69/Ios-emul` repository. Its addition is recorded in the same pinned commit as the survey generator. Its header identifies
`iPhone9,1`, `d10ap`, iOS 15.8.8 (`19H422`), root-compatible strings
`D10AP, iPhone9,1, AppleARM`, and 226 nodes.

The relevant entries in that summary are:

| Survey path | Published compatible | Register summary | What is supported |
|---|---|---|---|
| `/cpus/cpu0` | `apple,hurricane-zephyr,ARM,v8` | No non-empty reg block reported | CPU node and compatible string appear in the survey |
| `/cpus/cpu1` | `apple,hurricane-zephyr,ARM,v8` | No non-empty reg block reported | Second CPU node and compatible string appear in the survey |
| `/arm-io` | `arm-io,t8010` | 4 reg pairs; total reported size `0x16000` | T8010 arm-io node and summarized reg extent |
| `/arm-io/aic` | `aic,1` | 2 reg pairs; total reported size `0x9000` | AIC child and summarized reg extent |
| `/arm-io/aic-timebase` | No compatible string shown | 1 reg pair; total reported size `0x1000` | Timer-named child and summarized reg extent |
| `/pram` | No compatible string shown | 1 reg pair; total reported size `0x0` | Node exists in the survey; usable region values are not established |
| `/chosen` | No compatible string shown | Not applicable | Node exists; child/property values are not included |

The survey script's `walk()` function emits only node path, decoded
`compatible` strings, and a summary of `reg` pair count and total size. It
does not emit the `reg` address values, `ranges`, `interrupts`,
`interrupt-controller`, `device_type`, or clock-frequency properties.
The `0x0` total for CPU/pram summary rows must not be interpreted as a
verified hardware address or usable memory range.

**Additional parser caveat:** the script computes `reg` summaries using a
fixed 16-byte record and reads each size as a little-endian 64-bit integer.
It does not resolve the parent node's `#address-cells` / `#size-cells`
or validate that this fixed layout matches the Apple payload. Therefore
its pair counts and total-size figures are heuristics, not verified register
extents. See the [survey methodology review](iphone91-19h422-survey-methodology-review.md)
for the exact limitation and the validation needed before using any values.

### Survey-generation method

The same repository contains
[`scripts/dt-survey.py`](https://github.com/vytska69/Ios-emul/blob/4e2afb56f076473c54c720a607bb44cffc0ab04e/scripts/dt-survey.py).
The inspected script documents this process:

1. Queries the public IPSW.me device API for firmware metadata.
2. Uses HTTP range access through `RemoteZip` to read the IPSW ZIP central
   directory, `BuildManifest.plist`, and selected DeviceTree component,
   rather than downloading the entire multi-gigabyte archive.
3. Matches BuildIdentity device classes to the product's board list and
   prefers an erase identity.
4. Reads that identity's DeviceTree component path, unwraps IMG4/IM4P,
   rejects an encrypted payload, optionally decompresses LZFSE, and parses
   the flattened DeviceTree structure.
5. Writes node paths, compatible strings, and register-pair count/size
   summaries.

This gives a plausible, inspectable extraction route and ties the survey
format to a named script. However, the script does not independently
recompute and compare the full IPSW SHA-256 or the DeviceTree component
SHA-256 before writing the summary. The summary is therefore useful
secondary evidence, not a cryptographic verification by Project Sweet-10.
The script's fixed-width `reg` calculation is also not schema-aware; its
reported sizes must not be treated as decoded hardware windows until the
Apple payload encoding is independently established.

The inventory was added in a GitHub Actions bot commit
[`4e2afb56f076473c54c720a607bb44cffc0ab04e`](https://github.com/vytska69/Ios-emul/commit/4e2afb56f076473c54c720a607bb44cffc0ab04e),
whose file list includes the D10AP survey. The repository README describes
an emulator project; it does not report that this iPhone9,1 configuration
has booted. Do not interpret the DeviceTree survey as a successful iPhone 7
boot test.

## Source B: 19H422 firmware and component digest metadata

The public Orchard D10 recipe at pinned revision
[`7d33160c1ab73d365a7911f90ecdf5592749dcae`](https://github.com/OrchardLinux/orchard/tree/7d33160c1ab73d365a7911f90ecdf5592749dcae/devices/d10)
publishes the following values in `devices/d10/boot.json`:

| Item | Published value |
|---|---|
| Product | `iPhone9,1` |
| iOS version / build | `15.8.8 / 19H422` |
| IPSW filename | `iPhone_4.7_P3_15.8.8_19H422_Restore.ipsw` |
| IPSW SHA-256 | `4d480918c4a3e6fa69177db706086d3bf00d6f83f311e55974fe54e90c170aab` |
| BuildManifest SHA-256 | `1eb426fd4da23fc8d133a06c15f697924537d09b9dc192e49e23accf8dd9d015` |
| DeviceTree path | `Firmware/all_flash/DeviceTree.d10ap.im4p` |
| DeviceTree SHA-256 | `906a2708d3d15828c447ee1d7211f628dfeec7653a343384f3845153178c5906` |

The published full-archive SHA-256 agrees with the IPSW.me listing for
`iPhone9,1 / 19H422`. Project Sweet-10 did not receive the full archive, so
that archive hash remains unverified locally. However, the supplied standalone
BuildManifest and D10AP DeviceTree IM4P were independently hashed, and both
component SHA-256 values match Orchard's published metadata. The component's
SHA-384 also matches the D10AP BuildManifest Digest. The raw LZFSE payload
remains to be decompressed and parsed; see the [artifact verification record](iphone91-19h422-artifact-verification.md).

- [Orchard D10 boot metadata](https://github.com/OrchardLinux/orchard/blob/7d33160c1ab73d365a7911f90ecdf5592749dcae/devices/d10/boot.json)
- [Orchard D10 firmware metadata](https://github.com/OrchardLinux/orchard/blob/7d33160c1ab73d365a7911f90ecdf5592749dcae/devices/d10/firmware.json)
- [IPSW.me iPhone9,1 / 19H422 archive listing](https://ipsw.me/download/iPhone9%2C1/19H422/)

Orchard's compatibility documentation explicitly distinguishes known boot
metadata from a board having actually booted: a `boot.json` means Apple boot
files are known, not that a method runs on the board. Its D10 row is marked
experimental. This source is not evidence that an iPhone 7 has booted
Orchard, XNU 8796, or Project Sweet-10.

## Source C: unversioned iPhone9,1 device model

The [hack-different/apple-knowledge iPhone9,1 YAML](https://github.com/hack-different/apple-knowledge/blob/7e30ba57ac24c6da9e123a3b2732b5d9810d4114/_data/devices/iPhone9,1.yaml)
is a useful independent model-data cross-check. It identifies the root as
`D10AP`, `iPhone9,1`, `AppleARM`, and describes an `arm-io` node
compatible with `arm-io,t8010`, an AIC node with compatible `aic,1`,
`interrupt-controller: master`, and an `aic-timebase` node with
`device_type: timer`.

However, the YAML is not pinned to build `19H422` or another named IPSW
build. Some clock properties and mutable/machine-specific fields are zero
or represented by placeholders. It corroborates node/property naming at
the device-model level, but it is not used here to supply 19H422 property
values, register addresses, interrupt IDs, or frequencies.

## Comparison with XNU 8796 interfaces

The existing
[ARM64 interrupt and timer interface audit](interrupt-timer-interface-audit.md)
documents the XNU 8796 generic DeviceTree contract:

- The platform code obtains the SoC base from `/arm-io`.
- It looks for an `interrupt-controller` node with
  `interrupt-controller = "master"`.
- It looks for a node with `device_type = "timer"`.
- It reads both nodes' `reg` properties to map register windows relative
  to the SoC base.

The 19H422 survey supports the presence of `/arm-io`, `/arm-io/aic`,
and `/arm-io/aic-timebase`, with the compatible strings and register-size
summaries shown above. It does **not** expose enough properties to prove
that the XNU 8796 mapping helper's required `interrupt-controller`,
`device_type`, and `reg` values are all present and correctly encoded in
this exact tree.

Likewise, the summary shows `/cpus/cpu0` and `/cpus/cpu1`, but it does
not expose the CPU `reg`, `state`, cache/topology, or clock-frequency
values used by XNU's CPU and clock discovery. The summary's `/pram` and
`/chosen` entries also do not provide the panic-region values required
to populate the project's property inventory.

## What is now supported, and what is not

### Supported by the public survey and metadata

- A public survey file labels the tree as iPhone9,1 / D10AP / 19H422.
- That survey reports 226 nodes and shows the two Hurricane-Zephyr CPU
  nodes, T8010 `arm-io`, AIC child, and AIC-timebase child.
- Orchard publishes a matching 19H422 D10AP DeviceTree component path and
  SHA-256, plus BuildManifest and IPSW SHA-256 values.
- The survey-generation script is available for inspection and explains
  how the summary was obtained from a BuildManifest-selected DeviceTree.

### Verified by Project Sweet-10

- The full IPSW archive hash was not recalculated because the full archive was
  not supplied. The extracted BuildManifest and DeviceTree component hashes
  were independently verified.
- The raw 19H422 DeviceTree component has been decompressed and parsed:
  227 nodes including root, with no trailing bytes.
- `/arm-io/ranges`, the AIC master node, the AIC register pairs, and the
  AIC-timebase register pair have been extracted and compared with the pinned
  XNU 8796 generic mapper. See the parsed DeviceTree audit.
- CPU0/CPU1 `reg` and `state` values are known in the static tree.
- The tree identifies display, LCD, SPI touchscreen, and backlight nodes.

### Still open

- CPU0 frequency fields are present but zero; runtime clock values remain unknown.
- `/memory`, `/pram`, and `/vram` `reg` values are zero in this static tree,
  and `/chosen/embedded-panic-log-size` is absent. Final runtime memory and
  panic-region values remain unverified.
- Full interrupt specifier semantics, trigger modes, routing, EOI requirements,
  and live CPU topology remain unverified.
- The XNU 8796 T8010/H9 machine configuration blocker described in earlier
  audits is unchanged. A DeviceTree inventory does not restore missing
  T8010 source support in XNU 8796.
- No exact 20H392 iPhone9,1 kernelcache, BuildIdentity, or boot compatibility
  is established by this audit.

## Decision

Promote the independently parsed 19H422 D10AP properties and the XNU-correlated
ARM-IO/AIC/timer mapping inputs recorded in `device-tree/PROPERTY_INVENTORY.md`.
Keep zero-filled and runtime-dependent fields unresolved. The parsed tree is a
static IPSW component, not proof of the final iBoot/PongoOS handoff DeviceTree.

Do not infer target values from the unversioned YAML, iPhone X/A11 data,
Qualcomm SWEET data, or generic XNU fallbacks. This document is a static
source audit only; it does not claim a bootable iPhone 7 kernel or a
successful device boot.

See the [independent parsed DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md) for raw values, XNU source comparisons, zero-valued runtime fields, and the display/input node inventory.
