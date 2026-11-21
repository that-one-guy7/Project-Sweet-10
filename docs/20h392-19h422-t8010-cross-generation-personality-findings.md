# 19H422 / 20H392 T8010 cross-generation KEXT personality findings

## Scope and provenance

This report records the user-supplied output of the read-only
`tools/search_kext_inventory.py` run against the parsed KEXT inventories:

- Target: iPhone 7 `iPhone9,1` / D10AP / iOS 15.8.8 / `19H422`
- Donor: iPhone X `iPhone10,3` / D22AP / iOS 16.7.16 / `20H392`

The search scanned 230 target and 239 donor top-level KEXT records using
normalized terms `hurricane`, `errorhandler`, `platformerror`,
`t8010`, `t8015`, and `h9`. It reported 15 target records and 19
donor records with at least one hit. The category counts (identity,
personality, dependency, and other metadata) overlap; they are not unique
record totals.

The user reports that the local unit-test run completed with 64 tests passing.
That is a local test result, not a statement about a new GitHub Actions run.

## 1. Error-handler naming follows the SoC-specific platform record

### Target 19H422 / T8010

The target inventory contains the top-level bundle
`com.apple.driver.AppleHurricaneErrorHandler`. Its personality is:

- Personality and IOClass: `AppleARM64ErrorHandler`
- `IONameMatch=cpu-error-handler,hurricane`

The target `AppleT8010` KEXT also exposes
`AppleT8010PlatformErrorHandler` with
`IONameMatch=error-handler,t8010` and
`IOProviderClass=AppleARMIODevice`. Its direct dependency map names
`com.apple.driver.AppleHurricaneErrorHandler`.

### Donor 20H392 / T8015

The donor inventory contains
`com.apple.driver.AppleMonsoonErrorHandler`. Its personality uses the
same `AppleARM64ErrorHandler` class and IOClass, but its match string is
`cpu-error-handler,monsoon`.

The donor `AppleT8015` KEXT exposes
`AppleT8015PlatformErrorHandler` with
`IONameMatch=error-handler,t8015`; its dependency map names
`com.apple.driver.AppleMonsoonErrorHandler`.

### Interpretation

This is a strong metadata-level structural correspondence: both platform
families have a platform-error-handler personality, a family-named error
handler bundle, a shared class name, and a dependency edge from the matching
SoC KEXT. It explains why an exact-ID search for the T8010 Hurricane bundle
does not find a same-ID donor record.

It does **not** establish that the Hurricane and Monsoon executables have
the same implementation, private KPI/ABI, register behavior, error handling,
or runtime attachment. The different `IONameMatch` strings are material
hardware-selection differences and must not be rewritten or treated as
interchangeable.

## 2. Shared bundles advertise both T8010 and T8015 personality strings

Two records are notable because the target and donor search outputs both
contain T8010 and T8015 match strings in the same top-level bundle.

### AppleA7IOP

Both inventories contain `com.apple.driver.AppleA7IOP`. Both show
`AppleA7IOPV2-GFX` with an `IONameMatch` entry
`iop-gfx,t8010`.

Both outputs also show the following T8015 personality match strings:

- `AppleA7IOPV4`: `iop,t8015`
- `AppleA7IOPV4-GFX`: `iop-gfx,t8015`
- `AppleA7IOPV4PMP`: `iop-pmp,t8015`
- `AppleASC-ANS2`: `iop-ans2,t8015`

This is evidence that the donor inventory's AppleA7IOP metadata is not
exclusively T8015-labelled: it retains a T8010 graphics-IO match as well.
The keyword output does not show the complete personalities or prove which
one would match a particular device at runtime.

### AppleEmbeddedTempSensor

Both inventories contain `com.apple.driver.AppleEmbeddedTempSensor`.
Both outputs show T8010 matches for:

- `AppleDieTempController`: `dietempctl,t8010`
- `AppleT700XTempSensor`: `tempsensor,t8010`
- `AppleVTempDispatcher`: `vtempctl,t8010`

Both outputs also show T8015 match strings in
`AppleDieTempController`, `AppleT8015TempSensor`, and
`AppleVTempDispatcher`.

This is another useful cross-generation metadata lead. It is not a complete
property-by-property comparison and does not prove that the T8010 hardware
path remains operational in the donor's environment.

## 3. Display, GPU, and camera records are generation-specific in these exports

The target inventory reports:

| Subsystem | Target 19H422 record | Target match evidence |
|---|---|---|
| Display | `AppleMobileDispH9P` | `disp0,t8010`, `disp1,t8010` |
| GPU | `AGXG9P` | `gpu,t8010` |
| Camera interface | `AppleH9CameraInterface` | Personality named `s5l8960x`, IOClass `AppleH9CamIn` |

The donor inventory reports:

| Subsystem | Donor 20H392 record | Donor match evidence |
|---|---|---|
| Display | `AppleMobileDispH10P` | `disp0,t8015` |
| GPU | `AGXG10P` | `gpu,t8015` |
| Camera interface | `AppleH10CameraInterface` | `isp,t8015` |

These records reinforce that display, graphics, and camera are not shown as
same-ID, same-match substitutes across the two inventories. Their executable
interfaces, userland dependencies, and runtime behavior have not been
compared here.

## 4. Keyword-search false-positive caution

The term `h9` also matched the
`AppleTopCaseHIDEventDriver` record in both inventories, but the printed
path points inside an opaque `HIDScrollAccelerationTable` value rather
than a bundle identity or platform personality. This is an incidental
substring hit and is not evidence of H9 hardware support.

This example validates the search helper's evidence boundary: classify a
hit by its JSON path and category before treating it as a research lead.
Identity and personality matches are more informative than incidental
matches in encoded or opaque values, but none alone proves compatibility.

## Next bounded static task

The next useful comparison is to extract and diff the **complete JSON
records**, without loading or executing anything, for these shared bundles:

- `com.apple.driver.AppleA7IOP`
- `com.apple.driver.AppleEmbeddedTempSensor`

For the error-handler and platform records, compare the complete target
`AppleT8010` / Hurricane records against the donor
`AppleT8015` / Monsoon records, preserving their distinct match strings.
Keep H9/H10 display, AGX, and camera records as separate target/donor
hardware implementations rather than assuming they can be substituted.

The comparison should report exact top-level IDs, personality names,
selected property trees, and dependency maps. It should explicitly label
missing or empty fields as export metadata, not as ABI conclusions.

## Evidence limits

- These are parsed JSON metadata results only.
- A same-name class or a T8010 string in a donor personality does not prove
  binary equivalence, ABI compatibility, matching hardware registers, service
  attachment, or functional support.
- A selected top-level inventory omission is not a filesystem-wide absence
  claim.
- The H9/H10 and AGXG9P/AGXG10P names identify separate records in these
  exports; no binary compatibility test was performed.
- M1 remains in progress; M7/SpringBoard has not started.
- The physical iPhone 7 remains on iOS 12.1.4. No device, firmware,
  partition, or boot state was accessed or modified.
