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
`iPhone_4.7_P3_15.8.8_19H422_Restore.ipsw`. The cited listing gives archive
SHA-256:

`4d480918c4a3e6fa69177db706086d3bf00d6f83f311e55974fe54e90c170aab`

This is currently the most relevant stock target firmware reference found
during this audit. However, the checked fwkeydb snapshot's
`keys/firmware/iPhone9,1/0x8010` directory does not contain a `19H422`
record. Therefore this audit does **not** claim a 19H422 DeviceTree component
digest, BuildIdentity details, or parsed tree values.

- [IPSW.me iPhone9,1 iOS 15.8.8 (19H422) record](https://ipsw.me/download/iPhone9%2C1/19H422/)
- [Signet iPhone 7 / iPhone9,1 device page](https://cpeoples.github.io/signet/iphone/iphone9-1/)
- [The Apple Wiki iOS 15.8.8 OTA listing](https://theapplewiki.com/wiki/OTA_Updates/iPhone/15.8.8)

## Relationship to the 20H392 project reference

The project's `20H392` reference remains an iPhone X userland/donor reference.
The supplied BuildManifest audit records only `iPhone10,3` and
`iPhone10,6` product types and A11/T8015 chip ID `0x8015`. It is not an
iPhone9,1 manifest and does not provide the D10AP DeviceTree.

The stock iPhone9,1 records in this document establish that the target has
its own D10AP DeviceTree artifact in published firmware metadata. They do not
make the iPhone X 20H392 kernelcache or DeviceTree interchangeable with it.

## How this changes the evidence status

The previous statement “no verified iPhone9,1 DeviceTree source has yet been
established” needs a narrower wording:

- **Now established:** public firmware metadata ties several
  `DeviceTree.d10ap.im4p` component records to `iPhone9,1`, CPID `0x8010`,
  BDID `0x08`, including an iOS 15.0 build.
- **Still unknown:** any actual parsed `/cpus`, `arm-io`,
  `interrupt-controller`, timer, memory, or panic-region properties for the
  target.
- **Still missing:** the matching 19H422 DeviceTree digest and parsed values,
  exact BuildManifest identity details from that same build, and validation
  of property encodings against XNU 8796 consumers.

Accordingly, the existing per-property rows in
`device-tree/PROPERTY_INVENTORY.md` remain marked **Unknown**. A component
path and digest cannot fill a property-value cell.

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
