# T8010 supporting KEXT inventory plan

## Objective

Expand the exact-ID 19H422 target versus 20H392 donor comparison from the
nine core AIC/T8010 bundle IDs to the eleven non-KPI bundle IDs directly
named by those target KEXTs' `os_bundle_libraries` metadata.

The target is iPhone9,1 / D10AP / iOS 15.8.8 / 19H422. The comparison donor
is iPhone10,3 / D22AP / iOS 16.7.16 / 20H392. The physical iPhone 7 remains
on iOS 12.1.4; neither comparison inventory is installed on it.

## Selected support bundle IDs

| Bundle ID | Why selected from the supplied target metadata |
|---|---|
| `com.apple.driver.ApplePMGR` | Direct dependency of AppleT8010CLPC, AppleT8010PMGR, and AppleT8010SOCTuner |
| `com.apple.driver.AppleA7IOP` | Direct dependency of AppleT8010PMPFirmware and AppleT8010SmartIO |
| `com.apple.driver.IOSlaveProcessor` | Direct dependency of AppleT8010PMPFirmware and AppleT8010SmartIO |
| `com.apple.driver.RTBuddy` | Direct dependency of AppleT8010PMPFirmware |
| `com.apple.driver.AppleEmbeddedPCIE` | Direct dependency of AppleT8010PCIe |
| `com.apple.driver.AppleHurricaneErrorHandler` | Direct dependency of AppleT8010 |
| `com.apple.iokit.IOPCIFamily` | Direct dependency of AppleT8010PCIe |
| `com.apple.iokit.IOSurface` | Direct dependency of AppleT8010CLPC |
| `com.apple.kec.Libm` | Direct dependency of AppleT8010CLPC and AppleT8010PMGR |
| `com.apple.iokit.IOCryptoAcceleratorFamily` | Direct dependency of AppleT8010SmartIO |
| `com.apple.iokit.IOReportFamily` | Direct dependency of AppleT8010, AppleT8010CLPC, AppleT8010PCIe, and AppleT8010SOCTuner |

KPI pseudo-library IDs (`com.apple.kpi.*`) remain visible in each driver's
dependency output but are not included in this support-bundle allowlist.

## Run

From the local Project-Sweet-10 repository root after updating `main`:

```bash
python3 -m unittest discover -s tests -p 'test_compare_kext_metadata.py' -v

python3 tools/compare_kext_metadata.py \
  --target "/home/hey/19H422-kernel-inspect/analysis/kexts.json" \
  --donor "/home/hey/20H392-kernel-inspect/analysis/kexts.json" \
  | tee "/home/hey/20H392-19H422-t8010-supporting-kext-comparison.txt"
```

The program reads both JSON files only. It does not alter the input files,
inspect a live device, extract or execute KEXT binaries, or load drivers.

## What the next report should establish

For each of the eleven selected IDs, the next report will state whether a
matching top-level record is present in each parsed JSON inventory. Where a
record exists on one or both sides, it will print the selected bundle
metadata, selected IOKit personality fields, and serialized
`os_bundle_libraries` declarations.

This will answer a bounded static question: which of these direct support
bundle IDs and metadata records are represented in each inventory?

## Evidence limits

- A dependency name in another bundle's `os_bundle_libraries` map is not
  itself proof that a corresponding top-level KEXT record exists.
- A selected record absent from one parsed JSON inventory is not proof of
  absence from every filesystem, cache, or runtime source.
- Version strings and personality keys do not establish binary identity,
  KPI/ABI compatibility, load order, runtime service attachment, or
  hardware behavior.
- This is one dependency hop only. Transitive dependencies beyond these
  eleven exact IDs are not automatically inferred.
- No interrupt-controller constants, register behavior, device operation,
  kernel loading, or boot state are inferred or changed.
- The M7/SpringBoard milestone remains unstarted.

