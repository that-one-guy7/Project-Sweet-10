# Public iPhone9,1 stock DeviceTree artifact evidence

## Scope and conclusion

This audit checks public firmware metadata for the actual iPhone 7 Global target
(`iPhone9,1`, D10AP, A10/T8010). It establishes that public records exist for
D10AP DeviceTree components in multiple iPhone9,1 firmware builds.

**This is artifact-identity evidence, not a parsed DeviceTree.** No node values,
register addresses, interrupt IDs, frequencies, memory ranges, or property
types are claimed from these metadata records. The actual binary has not been
downloaded, parsed, or compared with XNU's property consumers in this audit.

## Source A: firmware metadata database

The public `tihmstar/fwkeydb` repository contains firmware records under
`keys/firmware/iPhone9,1/0x8010/<build>`. The reviewed files identify
`ProductType=iPhone9,1`, `cpid=0x8010`, and `bdid=0x8`. In each checked
record, the component key
`Firmware/all_flash/DeviceTree.d10ap.im4p` is present.

The records list component names `DeviceTree` and `RestoreDeviceTree`,
and variants `Customer Erase Install (IPSW)` and
`Customer Upgrade Install (IPSW)`. The database contains two digest strings
for this component in each reviewed build. They are reproduced below as
metadata values only; Project Sweet-10 has not recomputed them against a
downloaded component.

| Product version | Build | Product type | CPID | BDID | Component path | Metadata digest 0 | Metadata digest 1 |
|---|---|---|---|---|---|---|---|
| 11.0 | `15A372` | `iPhone9,1` | `0x8010` | `0x08` | `DeviceTree.d10ap.im4p` | `75e7f96729b01796d668154fd66604543409774a93fe232dae97d7218208d2143fa4367d8959671efa562315d52d24df` | `d554b35c7f35eed14c302d0ce88a5abb24ac2c6e20cc8d3ae754a6204429d2052711aba089bbaa711e6a74d85108a2e4` |
| 11.0.1 | `15A402` | `iPhone9,1` | `0x8010` | `0x08` | `DeviceTree.d10ap.im4p` | `b2f742b653ca5b34e71c77ea7fdd57c675a40ad80610d0c92a1770ff1a2d8619abb23732cc75b6a94f1cfe6d73a323b2` | `954df7f031e93494855092a8f9fcb26d2a8e74cc2ffa909a326240ed72ee78e2179be477ca9e1ac3c78d98a42e699495` |
| 15.0 | `19A346` | `iPhone9,1` | `0x8010` | `0x08` | `DeviceTree.d10ap.im4p` | `836e706b43cfe760a54377ba41b0225197ab017adc9c237343ebe3fe1d80f3501354479a80eef68746f5568adfffd766` | `3d437b9b5d2c55328b00c764f9e3876c43986a13eeb53920b87c52ffb9ae1693e9ff3ab4d8338d78108870ad09ee978c` |

The three records use different digest pairs. Do not reuse one build's digest
as the expected digest for another build. The database's `kbag` field is
empty for these entries; this audit does not treat that fact alone as proof
that an extracted payload is plaintext or authentic.

### Source records

- [fwkeydb 15A372 record](https://github.com/tihmstar/fwkeydb/blob/aed8a659526ee0d4101f81981ca94b469e5b5de6/keys/firmware/iPhone9,1/0x8010/15A372)
- [fwkeydb 15A402 record](https://github.com/tihmstar/fwkeydb/blob/aed8a659526ee0d4101f81981ca94b469e5b5de6/keys/firmware/iPhone9,1/0x8010/15A402)
- [fwkeydb 19A346 record](https://github.com/tihmstar/fwkeydb/blob/aed8a659526ee0d4101f81981ca94b469e5b5de6/keys/firmware/iPhone9,1/0x8010/19A346)
- [fwkeydb repository](https://github.com/tihmstar/fwkeydb)

No key, IV, or other decryption material is reproduced in this project document.

## Source B: component catalog cross-check

The iPhone Wiki's `Tigris 15A402 (iPhone9,1)` firmware component page lists
`DeviceTree.d10ap.im4p` as “Not Encrypted”. That independently corroborates
the component filename and published catalog classification for build 15A402.
It is a community-maintained firmware catalog, not a binary verification by
Project Sweet-10.

- [Tigris 15A402 (iPhone9,1) component listing](https://www.theiphonewiki.com/wiki/Tigris_15A402_%28iPhone9%2C1%29)

## Newer stock target reference: iOS 15.8.8 (19H422)

Public firmware indexes list the iPhone 7 Global restore image for
`iPhone9,1` as iOS 15.8.8, build `19H422`, filename
`iPhone_4.7_P3_15.8.8_19H422_Restore.ipsw`. The published full-archive
SHA-256 is:

`4d480918c4a3e6fa69177db706086d3bf00d6f83f311e55974fe54e90c170aab`

The checked fwkeydb snapshot still does not contain a `19H422` record.
However, the pinned public Orchard D10 firmware recipe publishes the
following metadata for the exact target build:

- `BuildManifest.plist` SHA-256:
  `1eb426fd4da23fc8d133a06c15f697924537d09b9dc192e49e23accf8dd9d015`
- `Firmware/all_flash/DeviceTree.d10ap.im4p` SHA-256:
  `906a2708d3d15828c447ee1d7211f628dfeec7653a343384f3845153178c5906`

The Orchard-published full-archive SHA-256 agrees with the IPSW.me listing.
Project Sweet-10 has now independently recalculated the SHA-256 of the supplied
standalone BuildManifest and D10AP DeviceTree component. Both match Orchard's
published component metadata, and the component's SHA-384 matches the
48-byte BuildManifest Digest field. The full IPSW archive itself was not supplied.

A separate public inventory file in the Ios-emul repository is explicitly
labeled `iPhone9,1 d10ap iOS 15.8.8 (19H422)`. Its accompanying
`dt-survey.py` script describes reading the IPSW BuildManifest and
DeviceTree component using HTTP range requests, selecting a matching erase
identity, unwrapping/parsing the DeviceTree, and writing node paths,
compatible strings, and register-pair count/size summaries. The script
does not independently compare the archive or component hashes before
writing the output. Its survey is secondary structural evidence, not a
hash-verified parse performed by Project Sweet-10.

See the detailed
[19H422 DeviceTree structure audit](iphone91-19h422-device-tree-structure-audit.md)
for node findings, script provenance, checksum metadata, and remaining
unknowns.

- [IPSW.me iPhone9,1 iOS 15.8.8 (19H422) record](https://ipsw.me/download/iPhone9%2C1/19H422/)
- [Orchard D10 boot metadata](https://github.com/OrchardLinux/orchard/blob/7d33160c1ab73d365a7911f90ecdf5592749dcae/devices/d10/boot.json)
- [Ios-emul 19H422 DeviceTree survey](https://github.com/vytska69/Ios-emul/blob/ade83f8fe550385c60a244b47982966e0da768e8/research/devicetrees/iPhone9,1-d10ap-19H422.txt)
- [Ios-emul survey script](https://github.com/vytska69/Ios-emul/blob/4e2afb56f076473c54c720a607bb44cffc0ab04e/scripts/dt-survey.py)

## Relationship to the 20H392 project reference

The project's `20H392` reference remains an iPhone X userland/donor reference.
The supplied BuildManifest audit records only `iPhone10,3` and
`iPhone10,6` product types and A11/T8015 chip ID `0x8015`. It is not an
iPhone9,1 manifest and does not provide the D10AP DeviceTree.

The stock iPhone9,1 records in this document establish that the target has
its own D10AP DeviceTree artifact in published firmware metadata. They do not
make the iPhone X 20H392 kernelcache or DeviceTree interchangeable with it.

## How this changes the evidence status

The earlier audit stated that 19H422 DeviceTree metadata and parsed values
were missing. The supplied extracted members now allow a more precise status:

- **Now established at artifact-metadata level:** Orchard publishes the
  19H422 IPSW, BuildManifest, and D10AP DeviceTree component hashes; the
  published archive hash agrees with IPSW.me.
- **Now reported at structural-summary level:** the Ios-emul survey labels
  a tree iPhone9,1 / D10AP / 19H422 and lists 226 nodes, two
  Hurricane-Zephyr CPU nodes, `arm-io,t8010`, an AIC node, and an
  AIC-timebase node.
- **Independently verified by this project:** the supplied standalone
  BuildManifest SHA-256 and D10AP DeviceTree component SHA-256 match the
  pinned Orchard metadata; the component SHA-384 also matches the
  BuildManifest Digest field. The full IPSW archive hash was not recalculated
  because the archive was not supplied.
- **Parsed by this project:** the decompressed tree contains 227 nodes
  including root; selected CPU, ARM-IO, AIC, timer, display, and touch
  properties were recorded in a privacy-filtered report.
- **Verified at selected property-value level:** CPU0/CPU1 state and IDs,
  ARM-IO ranges used by XNU's SoC-base helper, AIC and AIC-timebase register
  pairs used by the generic XNU mapper, and their source-derived mapping inputs.
- **Still unresolved at runtime level:** CPU0 clock properties are zero in
  the static tree; `/memory`, `/pram`, and `/vram` regions are zero; and
  `/chosen/embedded-panic-log-size` is absent. Live memory, clocks, and
  panic-region values need the final runtime DeviceTree.

Accordingly, `device-tree/PROPERTY_INVENTORY.md` now distinguishes verified
static-component values from runtime-dependent fields that remain unknown.
A parsed static property does not prove that the final boot-time tree or
hardware service is operational. See the [parsed DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md).

## Evidence-handling rules

1. Keep each DeviceTree component associated with its exact product, build,
   board ID, and component path.
2. Keep the normal `DeviceTree` and `RestoreDeviceTree` component names
   distinguishable.
3. Do not compare digests across different build versions as if they were
   interchangeable.
4. Do not infer DeviceTree contents from the filename, board name, SoC, or
   generic XNU parser.
5. Do not substitute iPhone X D22/D221 or Qualcomm SWEET data.
6. Only promote an individual property from Unknown after the component has
   been independently authenticated and parsed, and its location, width,
   endianness, units, and source build have been recorded.

No device operations, firmware installation, kernel changes, or boot procedure
are part of this audit.
