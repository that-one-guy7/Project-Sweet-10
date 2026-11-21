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
This remains an exact-ID inventory finding only.

The follow-up keyword search (PR #92) found a plausible donor-side,
differently named counterpart: `com.apple.driver.AppleMonsoonErrorHandler`.
Its `AppleARM64ErrorHandler` personality has the same `IOClass` as the
target Hurricane record, but uses `IONameMatch=cpu-error-handler,monsoon`
instead of the target's `cpu-error-handler,hurricane`. The donor parent
`AppleT8015` also has an `AppleT8015PlatformErrorHandler` personality
matched to `error-handler,t8015` and a direct dependency reference to
`AppleMonsoonErrorHandler`; the target `AppleT8010` parent uses the
corresponding T8010 personality and Hurricane dependency.

This is a strong structural metadata parallel, not a proof of identical
implementation, binary compatibility, private KPI/ABI compatibility,
provider attachment, or interchangeable behavior. The different match
strings must be treated as hardware-specific.

See [the full T8010/T8015 KEXT crosswalk](20h392-19h422-t8010-t8015-platform-crosswalk.md)
for the exact rows and other shared/split platform records.

## Historical context (not donor evidence)

Jonathan Levin's public BridgeOS 2.0 inspection article documents a 2017
KernelCache whose kernel string identifies XNU
`4570.20.58~3/RELEASE_ARM64_T8010`; its printed KEXT list includes
`AppleHurricaneErrorHandler (com.apple.driver.AppleHurricaneErrorHandler)`.
This is an older BridgeOS image, not the iPhone X 20H392 donor. It establishes
a historical T8010-family occurrence only and must not be used to infer
that the same bundle or implementation exists in 20H392.

Source: https://newosxbook.com/articles/BridgeOS.html

## Search result summary

The read-only search scanned 230 target records and 239 donor records.
It reported 15 target records and 19 donor records with one or more keyword
matches. Category counts overlap and must not be added together. The broad
`h9` term also produced incidental hits in encoded trackpad
`HIDScrollAccelerationTable` strings; those are not hardware evidence.

Other notable metadata leads:

- `AppleA7IOP` appears in both inventories and includes
  `iop-gfx,t8010` as well as T8015-specific personality matches.
- `AppleEmbeddedTempSensor` appears in both and includes T8010 and T8015
  match strings in shared personality records.
- Target display/GPU records are `AppleMobileDispH9P` and `AGXG9P`,
  with T8010 match strings; donor records are `AppleMobileDispH10P` and
  `AGXG10P`, with T8015 match strings.
- The target inventory includes `AppleH9CameraInterface`; the donor
  inventory includes `AppleH10CameraInterface`.

These findings are recorded in the crosswalk linked above. A keyword match
is only a lead for manual review.

## Evidence limits and next step

- The helper searches parsed JSON string keys and values only. It does not
  inspect executable bytes, enumerate a mounted filesystem, disassemble code,
  execute KEXTs, or interact with a device.
- A no-hit result means only that none of the chosen terms appeared in the
  parsed JSON fields searched by this helper.
- A similar name, shared IOClass, personality, or dependency relationship
  does not prove binary identity, private KPI/ABI compatibility, service
  attachment, or equivalent behavior.
- Empty or omitted serialized fields are not treated as zero values or as
  evidence of incompatibility.
- The next bounded host-side step is a detailed metadata crosswalk for the
  shared `AppleA7IOP` and `AppleEmbeddedTempSensor` bundles, followed by
  the target H9P/G9P and donor H10P/G10P dependency/personality records.
- M1 remains in progress; M7/SpringBoard has not started.
- The physical iPhone 7 remains on iOS 12.1.4. No device, firmware, partition,
  binary, or boot state is accessed or modified.
