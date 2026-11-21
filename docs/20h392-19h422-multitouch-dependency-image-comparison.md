# 20H392 donor / 19H422 target MultitouchHID dependency image comparison

## Scope

This report compares seven selected dependency image records from two
read-only dyld shared-cache JSON inventories:

- Donor: iPhone X `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16,
  build `20H392`, inventory `$HOME/20H392-dyld-images.json`.
- Target: iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8,
  build `19H422`, inventory `$HOME/19H422-dyld-images.json`.

The physical iPhone 7 remains on iOS 12.1.4. The records below were
supplied from read-only host-side inventory lookups. This is metadata
comparison only: it does not compare Mach-O bytes, verify code signatures,
establish loader resolution or runtime loading, or demonstrate compatibility
on the A10/T8010 target.

## Image-list record comparison

| Image | Target index | Target version | Target UUID | Donor index | Donor version | Donor UUID |
|---|---:|---|---|---:|---|---|
| SymptomDiagnosticReporter | 1455 | `174.140.2.0.0` | `ED77A600-C0BE-3240-9693-BF5238095816` | 928 | `229.120.4.0.0` | `AD5E6BA8-ED20-3AF7-BD79-274FEBAC7ABD` |
| WirelessDiagnostics | 6 | `954.1.0.0.0` | `0811A81D-68D5-3FFF-AC31-635D0FE0D732` | 600 | `980.0.0.0.0` | `B6D6A466-6317-3243-A8E7-D0C25575F981` |
| CoreAccessories | 343 | `672.140.4.0.0` | `7C035F3B-B050-3B16-99B8-1E75BBEFA7DF` | 312 | `793.140.4.0.0` | `82233556-8941-3465-A570-F8529F3BCD1E` |
| CoreAnalytics | 262 | `155.140.4.0.0` | `742D05D9-7082-307B-A1AE-8D72120856CA` | 226 | `264.140.2.0.0` | `A973AEA3-3A5D-3AAF-985D-29E7B13AE91C` |
| MultitouchSupport | 1249 | `5100.27.0.0.0` | `0EAF98B3-8D31-3A90-A578-1787797B9467` | 1648 | `6140.3.0.0.0` | `1B6ABB86-B8A9-3941-A66A-EC9715F6B034` |
| IOKit | 71 | `1955.140.2.0.0` | `4AA27953-BAC7-3BCC-A036-2E0CA754907F` | 30 | `2022.140.2.701.1` | `BCAE5DD8-45F9-3877-92CB-44190C3BAD70` |
| ProtocolBuffer | 186 | `288.32.9.15.1` | `A1947EB8-542F-3676-B3CC-EDD3B628B96F` | 239 | `294.30.6.7.2` | `54255241-0540-398C-BD54-B2F185C6D23C` |

All seven selected image families are represented in both cache image
inventories. Every corresponding pair has a different recorded version
string and a different Mach-O UUID. Image-list indexes are local to their
respective cache inventories; they must not be compared as stable IDs or
used to infer a dependency relationship.

The exact image paths are the matching framework executable paths under
`/System/Library`. The IOKit record in both inventories is
`/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`.

## Relationship to the MultitouchHID loader records

The separate `MultitouchHID` PrebuiltLoaderSet comparison reports:

- Target 19H422: 13 dependency rows (10 regular, 3 weak-link).
- Donor 20H392: 14 dependency rows (11 regular, 3 weak-link).
- The donor record lists `SymptomDiagnosticReporter` as an additional
  regular direct dependency; the target record does not.
- The target image inventory nevertheless contains
  `SymptomDiagnosticReporter` at index 1455. The donor inventory contains
  it at index 928.

Thus, `SymptomDiagnosticReporter` is a donor-only direct dependency edge
in the two compared loader records, not a framework missing from the target
cache image list. Image-list presence does not prove that the target
MultitouchHID loader resolves or loads that framework.

The same distinction applies to the other six image-list records: their
presence in each cache does not by itself establish that the loader resolves
each dependency to the listed record, or that all transitive dependencies
are satisfied. The loader edge types remain those recorded in the dedicated
[loader comparison](20h392-19h422-multitouch-loader-comparison.md).

## Interpretation and limits

This comparison establishes that the selected framework image records
differ between iOS 15.8.8 (19H422) and iOS 16.7.16 (20H392). It does not
establish that any one version difference causes a touch failure, that an
image is API-compatible or incompatible, or that a donor framework can be
substituted for the target build.

A different UUID identifies a different Mach-O build identity; it is not a
cryptographic trust verdict. No byte-level executable comparison,
code-signature verification, dependency-closure analysis, runtime loader
trace, IOKit provider attachment, plugin factory execution, HID event
delivery, or SpringBoard behavior is claimed.

No binary, shared-cache file, filesystem image, or firmware file is added
to the repository. No device, partition, activation, security, boot, or
restore state was accessed or changed.

## Follow-up: MultitouchSupport loader records

The target and donor `MultitouchSupport` loader records have now been
inspected. Their five-region permission patterns match, and both list six
shared regular dependent-loader rows. The donor additionally lists
`/usr/lib/libc++.1.dylib`; the target record does not. Full loader fields,
region tables, and dependency rows are recorded in the
[MultitouchSupport loader comparison](20h392-19h422-multitouchsupport-loader-comparison.md).

The exact `/usr/lib/libc++.1.dylib` path has now been found in both
cache inventories: target index 150, version `1300.36.0.0.0`, UUID
`16BE14F2-A677-3DF1-984D-BBAB893EE3B9`; donor index 93, version
`1500.65.0.0.0`, UUID
`07F1FD58-7392-34FF-8D56-AE101EBC175A`. This confirms the donor-only
MultitouchSupport dependent-loader row is not evidence that libc++ is
missing from the target cache. The full record comparison is in
[the libc++ cache-image audit](20h392-19h422-libcxx-cache-image-comparison.md).

The next bounded host-side check is a static comparison of target and donor
`MultitouchSupport` export metadata, while keeping cache image-list
membership, loader dependency edges, KEXT metadata, and runtime behavior
as separate evidence categories.
