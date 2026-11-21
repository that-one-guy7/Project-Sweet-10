# 19H422 target vs 20H392 donor AIC/T8010 KEXT metadata comparison

## Purpose

Compare a small, explicit set of top-level KEXT bundle IDs between the
iPhone 7 target-reference KernelCache JSON (iPhone9,1 / D10AP / 19H422)
and the iPhone X donor KernelCache JSON (iPhone10,3 / D22AP / 20H392).

The target-side inventory already confirms
\`com.apple.driver.AppleInterruptController\` version \`1.0.0d1\`, with
\`IONameMatch = aic,1\` and \`IOProviderClass = AppleARMIODevice\`.
The target-side T8010 personality crosswalk is recorded in
[the 19H422 AIC/T8010 inventory](iphone91-19h422-aic-kext-inventory.md).

## Exact bundles in scope

The tool uses exact top-level bundle identifiers, not substring matches:

- \`com.apple.driver.AppleInterruptController\`
- \`com.apple.driver.AppleARMPlatform\`
- \`com.apple.driver.AppleT8010\`
- \`com.apple.driver.AppleT8010CLPC\`
- \`com.apple.driver.AppleT8010PCIe\`
- \`com.apple.driver.AppleT8010PMPFirmware\`
- \`com.apple.driver.AppleT8010PMGR\`
- \`com.apple.driver.AppleT8010SmartIO\`
- \`com.apple.driver.AppleT8010SOCTuner\`

A reference to \`AppleARMPlatform\` inside another KEXT's
\`os_bundle_libraries\` does not count as a top-level AppleARMPlatform KEXT.
This avoids the broad-substring issue in the earlier 129-location output.

## Run the comparison on Ubuntu

From the repository root, run:

\`\`\`bash
python3 -m unittest discover -s tests -p 'test_compare_kext_metadata.py' -v

python3 tools/compare_kext_metadata.py \\
  --target "$HOME/19H422-kernel-inspect/analysis/kexts.json" \\
  --donor "$HOME/20H392-kernel-inspect/analysis/kexts.json" \\
  | tee "$HOME/20H392-19H422-aic-t8010-kext-comparison.txt"
\`\`\`

The program uses only the Python standard library and opens both JSON inputs
for reading. It reports selected bundle metadata, personality names and
match/provider fields, and \`os_bundle_libraries\` name/version differences.
It rejects duplicate selected bundle IDs and malformed inventory roots.

## Interpretation limits

- A bundle not found means it was not present as a selected top-level record
  in that JSON inventory; it does not prove absence from every filesystem or
  runtime source.
- A matching personality is static metadata, not proof of runtime IOKit
  attachment or controller operation.
- Matching dependency names or versions do not prove private KPI/ABI
  compatibility between XNU 8020 and the XNU 8796 donor.
- Version differences are descriptive. They are not by themselves evidence
  of incompatibility.
- This comparison does not recover proprietary KEXT implementations,
  register semantics, IRQ routing, acknowledge/EOI behavior, timer callbacks,
  or runtime values.
- No target constants are inferred from the donor. No device, firmware,
  partition, or boot state is accessed or modified.

## One-sided bundle records

When a selected bundle exists in only one parsed inventory, the comparator
prints the available side's selected IOKit personality names/fields and
`os_bundle_libraries` names/values. This preserves useful target-native
metadata for T8010-specific KEXTs even when the iPhone X donor has no matching
top-level bundle record. The missing side is still described only as absent
from that JSON inventory.

An empty dependency-version value or omitted bundle field is an export value
or omission, not a demonstrated ABI mismatch. The comparator does not infer
compatibility from presence, names, or version strings. All results remain
static metadata only.

The one-sided report is covered by synthetic tests for both target-only and
donor-only records. Re-run the same command above after updating the local
repository to capture the fuller output.


## Supporting dependency inventory extension

The comparator now also selects the following exact top-level bundle IDs,
which were named by the target T8010-family KEXTs' direct
`os_bundle_libraries` declarations:

- `com.apple.driver.ApplePMGR`
- `com.apple.driver.AppleA7IOP`
- `com.apple.driver.IOSlaveProcessor`
- `com.apple.driver.RTBuddy`
- `com.apple.driver.AppleEmbeddedPCIE`
- `com.apple.driver.AppleHurricaneErrorHandler`
- `com.apple.iokit.IOPCIFamily`
- `com.apple.iokit.IOSurface`
- `com.apple.kec.Libm`
- `com.apple.iokit.IOCryptoAcceleratorFamily`
- `com.apple.iokit.IOReportFamily`

These are selected as exact top-level IDs; a name appearing only as a
dependency reference does not count as a top-level bundle record. The
comparator labels the original nine IDs as core AIC/T8010 bundles and the
eleven additional IDs as supporting dependencies.

Run the same command above after updating the local repository. Save the
new report as
`$HOME/20H392-19H422-t8010-supporting-kext-comparison.txt`.

The extension is one dependency hop only. It does not recursively discover
all transitive dependencies, and no selected record's presence proves that
its binary is ABI-compatible or attaches at runtime. An absent record means
only that the exact top-level ID was not found in the parsed inventory.
