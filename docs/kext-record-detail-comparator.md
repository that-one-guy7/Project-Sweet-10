# Complete KEXT record metadata comparator

## Purpose

`tools/compare_kext_record_details.py` compares complete selected top-level
records from the parsed 19H422 target and 20H392 donor KEXT JSON inventories.
Unlike the earlier selected-field comparator, it recursively visits all JSON
keys and values in each requested record.

It is intended for the next bounded cross-generation review of
`AppleA7IOP`, `AppleEmbeddedTempSensor`, the `AppleT8010` /
`AppleT8015` parent records, and the corresponding Hurricane/Monsoon
error-handler records. It also includes the H9P/H10P, AGXG9P/AGXG10P, and
H9/H10 camera pairs as default inventory checks.

## Run on Ubuntu

From the repository root after updating `main`:

```bash
python3 -m unittest discover -s tests -v

python3 tools/compare_kext_record_details.py \\
  --target "$HOME/19H422-kernel-inspect/analysis/kexts.json" \\
  --donor "$HOME/20H392-kernel-inspect/analysis/kexts.json" \\
  | tee "$HOME/20H392-19H422-kext-record-detail-comparison.txt"
```

Without any `--pair` arguments, the tool compares these seven exact-ID pairs:

| Target 19H422 | Donor 20H392 |
|---|---|
| `com.apple.driver.AppleA7IOP` | `com.apple.driver.AppleA7IOP` |
| `com.apple.driver.AppleEmbeddedTempSensor` | `com.apple.driver.AppleEmbeddedTempSensor` |
| `com.apple.driver.AppleT8010` | `com.apple.driver.AppleT8015` |
| `com.apple.driver.AppleHurricaneErrorHandler` | `com.apple.driver.AppleMonsoonErrorHandler` |
| `com.apple.driver.AppleMobileDispH9P` | `com.apple.driver.AppleMobileDispH10P` |
| `com.apple.AGXG9P` | `com.apple.AGXG10P` |
| `com.apple.driver.AppleH9CameraInterface` | `com.apple.driver.AppleH10CameraInterface` |

To compare only a custom pair, pass `--pair TARGET_ID DONOR_ID`. Repeat
`--pair` for multiple pairs; supplying any custom pair set replaces the
default set.

## Output rules

- Only exact top-level `id` values are selected; a dependency-map mention
  does not create a top-level record.
- Nested dictionaries are compared recursively and reported with stable
  JSON-pointer-style paths.
- An omitted key is reported as `<missing>`; an explicit JSON `null`
  remains `null`; an empty string remains `""`.
- JSON types are preserved, so boolean `true` is not treated as integer `1`.
- Lists are compared by index and report a synthetic `#length` path when
  their lengths differ. List order is not normalized.
- A missing record means only that the exact top-level ID was not found in
  that parsed JSON inventory.

The tool reads JSON only. It does not extract or inspect executable bytes,
open a KernelCache binary, load a KEXT, interact with a device, or modify
input files. A metadata difference does not establish ABI incompatibility,
runtime attachment, hardware behavior, or bootability.

The local focused unit-test run for the new helper completed with 16 tests
passing during development. The full repository suite should be run after
merging this change. The physical iPhone 7 remains on iOS 12.1.4.
