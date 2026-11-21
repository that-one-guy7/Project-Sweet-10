# AppleHurricaneErrorHandler donor metadata follow-up

## Current evidence

The 19H422 target-reference inventory selects
`com.apple.driver.AppleHurricaneErrorHandler` as a top-level supporting
dependency of the target `AppleT8010` KEXT. The target's
`AppleT8010PlatformErrorHandler` personality uses
`IONameMatch=error-handler,t8010` and
`IOProviderClass=AppleARMIODevice`.

The exact-ID comparison found no selected top-level record with bundle ID
`com.apple.driver.AppleHurricaneErrorHandler` in the 20H392 donor KEXT JSON.
This is a limitation of that parsed inventory, not a filesystem-wide absence
claim and not proof that the donor has no functionally related implementation.

## Historical context (not donor evidence)

Jonathan Levin's public BridgeOS 2.0 inspection article documents a 2017
KernelCache whose kernel string identifies XNU
`4570.20.58~3/RELEASE_ARM64_T8010`; its printed KEXT list includes
`AppleHurricaneErrorHandler (com.apple.driver.AppleHurricaneErrorHandler)`.
This is an older BridgeOS image, not the iPhone X 20H392 donor. It establishes
a historical T8010-family occurrence only and must not be used to infer
that the same bundle or implementation exists in 20H392.

Source: https://newosxbook.com/articles/BridgeOS.html

## Objective

Run a broad, reproducible string search over every top-level record in both
already-parsed KEXT JSON inventories. Search record identity fields, all
nested personality names and values, dependency-map keys and values, and
other string-valued metadata. This can reveal plausible renamed labels or
cross-references that the exact-ID allowlist does not capture.

The helper searches JSON only. It does not inspect binary contents, enumerate
a mounted filesystem, disassemble code, execute KEXTs, or interact with a
device.

## Run on Ubuntu

From the Project-Sweet-10 repository root after updating `main`:

```bash
python3 -m unittest discover -s tests -v

python3 tools/search_kext_inventory.py \\
  --target "$HOME/19H422-kernel-inspect/analysis/kexts.json" \\
  --donor "$HOME/20H392-kernel-inspect/analysis/kexts.json" \\
  | tee "$HOME/20H392-19H422-hurricane-error-handler-search.txt"
```

The default normalized search terms are:

- `hurricane`
- `errorhandler`
- `platformerror`
- `t8010`
- `t8015`
- `h9`

Matching ignores case and punctuation, so `error-handler`,
`Error_Handler`, and `ErrorHandler` are searched equivalently. Terms can
be overridden with `--terms`.

## How to classify results

1. A match in top-level `id`, `name`, `executable`, or `bundle_path`
   identifies a candidate record name/path. The exact `id` is the strongest
   inventory identity evidence.
2. A personality-name or personality-value match is a metadata association,
   not proof that the record implements the same code.
3. A match only in `os_bundle_libraries` is a dependency reference. It does
   not create a top-level KEXT record.
4. A match in other metadata is a lead to inspect manually, not a compatibility
   result.

Compare donor hits with the target's known
`AppleT8010PlatformErrorHandler` personality and the
`AppleHurricaneErrorHandler` supporting bundle ID. Do not designate a
candidate as an equivalent without additional independent evidence.

## Evidence limits and next step

- A no-hit result means only that none of the chosen terms appeared in the
  parsed JSON string keys/values searched by this helper.
- It does not prove the absence of strings or code from the underlying
  KernelCache binary, another filesystem/cache, or runtime.
- A similar name or personality does not prove binary identity, private
  KPI/ABI compatibility, service attachment, or equivalent behavior.
- The full detailed metadata for eight supporting dependencies remains
  untranscribed; the current 11-row table records their inventory presence.
- M1 remains in progress; M7/SpringBoard has not started.
- The physical iPhone 7 remains on iOS 12.1.4. No device, firmware, partition,
  or boot state is accessed or modified.
