# iPhone9,1 / D10AP / 19H422 artifact verification

## Scope

Project Sweet-10 received two extracted members from the iPhone 7 Global iOS 15.8.8 (19H422) IPSW:

- `BuildManifest-19H422.plist`
- `DeviceTree.d10ap.im4p`

The complete IPSW archive was not supplied. No firmware was installed, and the iPhone 7 was not connected or modified for this verification.

## Independently measured results

| Artifact / field | Measured result |
|---|---|
| BuildManifest size | 337,447 bytes |
| BuildManifest SHA-256 | `1eb426fd4da23fc8d133a06c15f697924537d09b9dc192e49e23accf8dd9d015` |
| DeviceTree IM4P size | 29,568 bytes |
| DeviceTree IM4P SHA-256 | `906a2708d3d15828c447ee1d7211f628dfeec7653a343384f3845153178c5906` |
| DeviceTree IM4P SHA-384 | `d7cb7c692e20013c28602c6c3e05eb045294b6dee12daadff8822fd17fc1b79f8d7098a95d90fcf2636e7ff7d3db6096` |

Both SHA-256 values match the values published in the pinned [Orchard D10 boot metadata](https://github.com/OrchardLinux/orchard/blob/7d33160c1ab73d365a7911f90ecdf5592749dcae/devices/d10/boot.json). The component SHA-384 also exactly matches the 48-byte `Digest` field in the D10AP BuildManifest identity. The three-way agreement verifies the supplied files against the available public metadata.

The full IPSW SHA-256 was not recalculated because the full IPSW archive was not supplied.

## BuildManifest findings

The actual plist reports:

- `ProductVersion`: `15.8.8`
- `ProductBuildVersion`: `19H422`
- Root `SupportedProductTypes`: `iPhone9,1`, `iPhone9,3`
- Four total `BuildIdentities`
- Two `d10ap` identities:
  - Index 1: `Erase`, `Customer Erase Install (IPSW)`
  - Index 3: `Update`, `Customer Upgrade Install (IPSW)`

Both D10AP identities reference:

- DeviceTree path: `Firmware/all_flash/DeviceTree.d10ap.im4p`
- DeviceTree `Digest`: the same 48-byte value, matching SHA-384 of the complete supplied IM4P file
- KernelCache path: `kernelcache.release.iphone9`

The manifest's root supported-product list is shared by the identities; it is not a separate product list embedded in each D10AP identity. The D10AP entries' `Info` dictionaries do not contain `ApBoardID` or `ApChipID`; this audit does not invent those values.

The BuildManifest marks the DeviceTree component `Personalize=true` and `IsFirmwarePayload=true`. These are recorded metadata fields, not a claim about compatibility with a custom loader.

## IM4P inspection

The supplied component parses as a complete DER sequence with:

- IM4P marker: `IM4P`
- Component type: `dtre`
- Description: `EmbeddedDeviceTrees-6331.140.11.700.2`
- Payload length: 29,499 bytes
- Payload prefix: `bvx2`
- Trailing OCTET STRING count after the payload: zero

The `bvx2` marker identifies an LZFSE-family compressed payload. Apple's open-source [LZFSE reference implementation](https://github.com/lzfse/lzfse) provides a Linux Makefile and command-line decoder. This project has extracted and hashed the compressed payload and has now independently decompressed and parsed the flattened DeviceTree. See the [parsed DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md).

## Reproducible local verification

The repository tool validates the exact BuildManifest and DeviceTree hashes, verifies the D10AP Erase/Update identities, checks that SHA-384 of the component matches the manifest's 48-byte Digest, and validates the IM4P wrapper. It does not need the full IPSW and does not alter either input file.

From the repository root, with the two files in the current directory:

```bash
python3 tools/verify_d10ap_19h422_artifacts.py \
  --manifest BuildManifest-19H422.plist \
  --device-tree DeviceTree.d10ap.im4p \
  --extract-payload DeviceTree.d10ap.lzfse
```

The optional extracted file is the compressed LZFSE payload. Decompress it with the command above to produce `DeviceTree.d10ap.raw`; that raw file was subsequently parsed with `tools/inspect_apple_dt.py`.

### Decompress on Ubuntu

The upstream LZFSE project documents a Linux build with `make`. Its command-line source documents the `-decode -i INPUT -o OUTPUT` syntax.

```bash
sudo apt-get update
sudo apt-get install -y git build-essential

git clone https://github.com/lzfse/lzfse.git
cd lzfse
make

./build/bin/lzfse -decode \
  -i ../DeviceTree.d10ap.lzfse \
  -o ../DeviceTree.d10ap.raw
```

References: [LZFSE README and Linux build](https://github.com/lzfse/lzfse/blob/master/README.md), [LZFSE command-line argument parser](https://github.com/lzfse/lzfse/blob/master/src/lzfse_main.c).

The decoder is run on the extracted data file on the computer. It is not run on the iPhone and does not install or restore firmware.

## What this establishes — and what it does not

**Established:**

- The uploaded BuildManifest is the published 19H422 manifest by SHA-256.
- The uploaded component is the published D10AP DeviceTree IM4P by SHA-256.
- Its SHA-384 matches the D10AP BuildManifest Digest field.
- The manifest contains D10AP Erase and Update identities referencing the same target DeviceTree component.
- The component is an IM4P `dtre` wrapper with an LZFSE-family `bvx2` payload.

**Now verified from the static target DeviceTree:**

- Complete parse: 227 nodes including root, 160,572 bytes, zero trailing bytes.
- Root identity `D10AP / iPhone9,1 / AppleARM` and `/arm-io` compatibility `arm-io,t8010`.
- CPU0/CPU1 state and `reg`/`cpu-id` values.
- `/arm-io/ranges` value used by the pinned XNU SoC-base helper.
- AIC master-controller metadata, register windows, and AIC-timebase register window used by the generic XNU mapper.
- Presence of display, LCD, SPI touchscreen, and backlight nodes.

**Still unverified:**

- Final runtime clock values: CPU0 frequency properties are zero in the static component.
- Final memory and panic regions: `/memory`, `/pram`, and `/vram` are zero-filled, and `/chosen/embedded-panic-log-size` is absent.
- The final DeviceTree and `boot_args` that a PongoOS custom loader would hand to XNU.
- Full interrupt routing and actual AIC/timer operation.
- Whether the iOS 15.8.8 DeviceTree is directly reusable with an iOS 16-era XNU build.

This artifact is a target-hardware reference from iOS 15.8.8. It is not the iOS 16 donor KernelCache, not a 20H392 iPhone 7 manifest, and not proof that XNU 8796 supports T8010.

Selected property-value rows are now populated in `device-tree/PROPERTY_INVENTORY.md` where the static tree bytes and pinned XNU consumer agree. Runtime-dependent or zero-filled fields remain unresolved.
