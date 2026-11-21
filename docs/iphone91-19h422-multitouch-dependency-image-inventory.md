# iPhone9,1 19H422 MultitouchHID dependency image inventory

## Scope and evidence

This note records the user's read-only search of the existing
`$HOME/19H422-dyld-images.json` inventory for selected dependency names
from the target 19H422 `MultitouchHID` PrebuiltLoaderSet record.

Target: iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8 build
`19H422`. The physical iPhone remains on iOS 12.1.4. The lookup read
static dyld cache image-list metadata only. It did not execute an image,
validate its signature, establish runtime dependency resolution, or test
IOKit/plugin loading.

## Results

| Searched image | Image-list index | Full target cache image path | Version | UUID |
|---|---:|---|---|---|
| SymptomDiagnosticReporter | 1455 | `/System/Library/PrivateFrameworks/SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter` | `174.140.2.0.0` | `ED77A600-C0BE-3240-9693-BF5238095816` |
| WirelessDiagnostics | 6 | `/System/Library/PrivateFrameworks/WirelessDiagnostics.framework/WirelessDiagnostics` | `954.1.0.0.0` | `0811A81D-68D5-3FFF-AC31-635D0FE0D732` |
| CoreAccessories | 343 | `/System/Library/PrivateFrameworks/CoreAccessories.framework/CoreAccessories` | `672.140.4.0.0` | `7C035F3B-B050-3B16-99B8-1E75BBEFA7DF` |
| CoreAnalytics | 262 | `/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics` | `155.140.4.0.0` | `742D05D9-7082-307B-A1AE-8D72120856CA` |
| MultitouchSupport | 1249 | `/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport` | `5100.27.0.0.0` | `0EAF98B3-8D31-3A90-A578-1787797B9467` |
| IOKit | 71 | `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit` | `1955.140.2.0.0` | `4AA27953-BAC7-3BCC-A036-2E0CA754907F` |
| ProtocolBuffer | 186 | `/System/Library/PrivateFrameworks/ProtocolBuffer.framework/ProtocolBuffer` | `288.32.9.15.1` | `A1947EB8-542F-3676-B3CC-EDD3B628B96F` |

Each of the seven selected dependency names returned one relevant image
record. The `IOKit.framework` substring search also returned
`CoreAudioKit.framework/CoreAudioKit` at index 732; that is a separate
framework and is not an additional IOKit result. The IOKit record relevant
to the loader dependency is the exact `IOKit.framework/Versions/A/IOKit`
path at index 71.

## Interpretation

The most important result is that
`SymptomDiagnosticReporter.framework/SymptomDiagnosticReporter` is
represented in the target 19H422 dyld cache image inventory at index 1455,
version `174.140.2.0.0`, UUID
`ED77A600-C0BE-3240-9693-BF5238095816`.

This resolves the narrow question raised by the donor/target loader
comparison:

- The donor 20H392 `MultitouchHID` loader record lists
  `SymptomDiagnosticReporter` as a regular dependency.
- The target 19H422 `MultitouchHID` loader record does not list it as a
  dependency.
- The target 19H422 cache image inventory nevertheless contains a
  `SymptomDiagnosticReporter` image record.

Therefore, it is accurate to call this a **donor-only direct dependency
edge in the compared loader records**. It is not accurate to call the
framework absent from the target dyld cache. The image-list record does not
prove it is present as a standalone file in the mounted root filesystem,
resolved by the target loader for this plugin, or loaded at runtime.

The other six searched dependency names are also represented in the target
image inventory, with the paths, versions, and UUIDs listed above. This
establishes image-list presence only. It does not establish that the loader
resolves each dependency to that exact record, that all transitive
dependencies are satisfied, or that the plugin executes successfully.

## Next bounded check

Run the same read-only name lookup against the already-generated donor
inventory `$HOME/20H392-dyld-images.json` for these seven selected
dependencies. Comparing the donor and target version/UUID records will
clarify which framework builds differ between the two caches. This remains
static cache metadata research; it does not establish binary compatibility,
runtime loading, or cross-board support.

No binary, shared-cache file, filesystem image, or firmware file is added
to the repository. No device, partition, activation, security, boot, or
restore state was accessed or changed.
