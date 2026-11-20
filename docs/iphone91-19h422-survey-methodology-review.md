# iPhone9,1 19H422 DeviceTree survey methodology review

## Scope

This review examines the public survey generator and its published iPhone 7 result:

- Target label: `iPhone9,1` / D10AP
- Stock reference build: iOS 15.8.8 / `19H422`
- Survey file and generator commit: [`4e2afb56f076473c54c720a607bb44cffc0ab04e`](https://github.com/vytska69/Ios-emul/commit/4e2afb56f076473c54c720a607bb44cffc0ab04e)
- Generator: [`scripts/dt-survey.py`](https://github.com/vytska69/Ios-emul/blob/4e2afb56f076473c54c720a607bb44cffc0ab04e/scripts/dt-survey.py)
- Published target survey: [`iPhone9,1-d10ap-19H422.txt`](https://github.com/vytska69/Ios-emul/blob/4e2afb56f076473c54c720a607bb44cffc0ab04e/research/devicetrees/iPhone9,1-d10ap-19H422.txt)

This is a source-method review. Project Sweet-10 has not independently downloaded the IPSW, recalculated its archive/component digests, or parsed the original DeviceTree payload. No target property value is promoted by this document.

## What the generator does

The pinned script:

1. Gets the latest IPSW metadata for the requested product from the public IPSW.me API.
2. Uses `RemoteZip` range reads for the archive directory, root `BuildManifest.plist`, and selected DeviceTree component.
3. Filters BuildIdentities by the device classes reported for the product and prefers an identity whose restore behavior is `Erase`.
4. Reads that identity's DeviceTree component path, unwraps IMG4/IM4P, rejects an encrypted payload, and decompresses recognized LZFSE payloads when the optional decoder is installed.
5. Parses the flattened tree and writes node paths, compatible strings, and a compact `reg` summary.

This is a useful way to discover candidate node paths without fetching every IPSW member. The script does not calculate and compare the published full-IPSW SHA-256 or DeviceTree-component SHA-256 before emitting the report. Its output remains secondary evidence until the exact archive and component have been independently verified.

## Important limitation: `reg` is not decoded from its parent cell contract

The generator's `walk()` implementation calculates the number of `reg` pairs by dividing the property byte length by 16. For each pair it reads the second eight-byte field as a little-endian unsigned 64-bit size. That hard-codes a 16-byte `(u64 address, u64 size)` record.

The script does not inspect the parent node's `#address-cells` and `#size-cells` properties, does not establish an Apple-specific alternative encoding, and does not reject a `reg` property whose length is not an exact multiple of 16. It therefore does not demonstrate that every reported pair count or total size represents the actual address/length tuples in the source tree.

The generic Devicetree specification describes `reg` as address/length pairs whose field widths are determined by the parent node's `#address-cells` and `#size-cells` properties. Those properties determine the number of 32-bit cells used for each field; a consumer cannot safely infer a universal 64-bit-address plus 64-bit-size layout from the property name alone. See the [Devicetree specification's `reg` and cell-count definition](https://devicetree-specification.readthedocs.io/en/latest/chapter2-devicetree-basics.html).

That generic specification is a reference for the encoding question, not proof that Apple's flattened DeviceTree serialization is identical in every detail. Project Sweet-10 must establish the exact encoding used by the 19H422 Apple payload and consumed by the pinned XNU code before treating any parsed field as a target value.

**Interpretation:** the published values such as `4 reg pairs; total size 0x16000` for `/arm-io` are script-reported summaries, not verified register addresses, resource-window lengths, or mapped extents. They must not be copied into a board configuration or used to initialize hardware. The CPU, AIC, timer, `pram`, and other `reg` fields remain Unknown in the project inventory.

A related counting detail: the generator's `walk()` function adds a line only for non-root nodes. Its printed line count therefore excludes the root `/` node; the survey's node count should be understood according to that implementation's counting convention.

## Evidence classification

| Item | Current classification | What would promote it |
|---|---|---|
| Product/build label `iPhone9,1 / D10AP / 19H422` | Externally reported; corroborated by public firmware indexes and Apple security-release information | Exact local BuildManifest identity plus archive provenance |
| CPU, `arm-io`, AIC, and timer node presence | Provisional third-party structural evidence | Independent parse of the hash-verified target component |
| Compatible strings | Provisional third-party structural evidence | Independent parse of the exact component |
| `reg` pair counts and total sizes | Unvalidated generator heuristic | Raw property bytes plus validated encoding/cell widths |
| `ranges`, interrupt specifiers, timer metadata, CPU state/topology, and clock values | Unknown | Independent extraction and comparison with the relevant XNU consumers |
| IPSW and DeviceTree SHA-256 values | Published third-party metadata, not yet recalculated by this project | Local digest matches against the exact downloaded archive and component |

## Next verification work

1. Obtain the exact `iPhone9,1` / `19H422` IPSW and record its source, size, and SHA-256. Compare the result with the published digest; do not treat a filename as identity proof.
2. Read the root BuildManifest and record the selected D10AP BuildIdentity, supported product type, board/chip identity, and DeviceTree component path. Keep every identity in the report until the target identity is unambiguous.
3. Extract only the selected DeviceTree component to a temporary local path and independently calculate its SHA-256. Compare it with the published component digest before parsing.
4. Parse the verified payload with bounds checks and retain raw property bytes. Determine the encoding used by the Apple payload; decode `reg` and `ranges` only after validating the relevant cell counts, byte order, and XNU consumer expectations.
5. Add synthetic host-side tests for more than one address/size cell-width combination, truncated properties, invalid lengths, and absent cell-count properties.
6. Update `device-tree/PROPERTY_INVENTORY.md` one property at a time, with the exact build, component digest, raw encoding, units, source, and confidence. Keep unknowns unknown.

## Project decision

The survey remains useful for selecting where to investigate next, but it is not a hardware specification. Its node/compatible summary is provisional; its `reg` totals are specifically heuristic. No target-specific address, length, interrupt, clock, CPU, or memory constant is approved by this review.

This review does not add kernel code, a machine configuration, a boot payload, firmware, or device-operation instructions. The project remains in source research and host-side validation.
