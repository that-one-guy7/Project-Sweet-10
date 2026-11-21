# iPhone9,1 19H422 / iPhone10,3 20H392 graphics PrebuiltLoader results

## Scope and provenance

This report records the user's uploaded `graphics-loader-texts.tar.gz` archive. It contains:

- 11 target 19H422 image-query output files.
- 11 donor 20H392 image-query output files.
- 22 stderr files.
- One `query-status.tsv` with 22 query-status rows.

The queries were run with the standalone (non-Snap) `ipsw` 3.1.749 binary, build commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`, against the already-mounted host-side caches. All 22 commands exited status 0. Each stderr file contains only the `Parsing Cache` progress line; no error message was reported.

Every inspected image output identifies the loader as `prebuilt` and prints a `Dependents` block. The paired results cover the following install paths:

| Target 19H422 image | Donor 20H392 image |
|---|---|
| `/System/Library/Frameworks/Metal.framework/Metal` | Same install path |
| `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics` | Same install path |
| `/System/Library/Frameworks/IOSurface.framework/IOSurface` | Same install path |
| `/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer` | Same install path |
| `/System/Library/PrivateFrameworks/IOGPU.framework/IOGPU` | Same install path |
| `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit` | Same install path |
| `/System/Library/PrivateFrameworks/IOAccelerator.framework/IOAccelerator` | Same install path |
| `/System/Library/PrivateFrameworks/AGXCompilerCore.framework/AGXCompilerCore` | Same install path |
| `/System/Library/Frameworks/MetalKit.framework/MetalKit` | Same install path |
| `/System/Library/Extensions/AGXMetalA10.bundle/AGXMetalA10` | `/System/Library/Extensions/AGXMetalA11.bundle/AGXMetalA11` |
| `/System/Library/Extensions/AppleMetalGLRenderer.bundle/AppleMetalGLRenderer` | Same install path |

The physical iPhone 7 remains on iOS 12.1.4. All operations in this report are host-side static cache inspection.

## Dependency summary

Counts below are parsed from the printed `Dependents` block. Dependency kinds are preserved; a weak-link is not counted as an ordinary regular dependency.

| Pair | Target 19H422 | Donor 20H392 | Exact typed-edge comparison |
|---|---:|---:|---|
| Metal | 10 regular + 1 weak-link | 12 regular + 2 weak-link | 11 shared; donor adds 3 |
| CoreGraphics | 12 regular | 12 regular + 1 weak-link | 12 shared; donor adds 1 |
| IOSurface | 5 regular | 5 regular | Identical |
| IOMobileFramebuffer | 4 regular | 4 regular | Identical |
| IOGPU | 9 regular | 9 regular | Identical |
| IOKit | 6 regular | 6 regular | Identical |
| IOAccelerator | 7 regular + 1 weak-link | 7 regular + 1 weak-link | Identical |
| AGXCompilerCore | 10 regular | 10 regular | Identical |
| MetalKit | 12 regular | 12 regular | Identical |
| AGX plugin pair (A10 vs A11) | 14 regular | 14 regular | Identical |
| AppleMetalGLRenderer | 11 regular | 11 regular | Identical |

Across these ten pairs there are 102 target typed edges and 106 donor typed edges. The target edge sets are fully represented in the donor outputs; there are zero target-only typed edges. The donor has four additional typed edges total: three under Metal and one under CoreGraphics. Eight of the ten pairs have identical typed dependency sets.

### Donor-only dependency edges

The donor Metal record prints these additional dependencies:

| Kind | Install path |
|---|---|
| regular | `/System/Library/Frameworks/Security.framework/Security` |
| regular | `/usr/lib/libcompression.dylib` |
| weak-link | `/usr/lib/libllvm-flatbuffers.dylib` |

The donor CoreGraphics record prints this additional weak-link dependency:

| Kind | Install path |
|---|---|
| weak-link | `/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics` |

The target Metal record also has `GPUCompilerUtils.dylib` as a weak-link dependency; that same weak-link is present in the donor Metal record. The Metal output otherwise has the same 10 regular and one weak-link typed rows as target, with the donor adding the three rows above.

### Key common dependency paths

The target and donor IOGPU records print the same nine regular dependencies:

- `/System/Library/PrivateFrameworks/IOAccelerator.framework/IOAccelerator`
- `/System/Library/Frameworks/Metal.framework/Metal`
- `/System/Library/Frameworks/Foundation.framework/Foundation`
- `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
- `/System/Library/Frameworks/IOSurface.framework/IOSurface`
- `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
- `/usr/lib/libc++.1.dylib`
- `/usr/lib/libSystem.B.dylib`
- `/usr/lib/libobjc.A.dylib`

The target and donor IOAccelerator records have the same eight typed rows: CoreAnalytics is weak-link; Foundation, Security, CoreFoundation, IOSurface, IOKit, libSystem, and libobjc are regular.

The target and donor IOKit records each print six regular dependencies: libenergytrace, CoreFoundation, libz, libbsm, libSystem, and libobjc. Their IOMobileFramebuffer records each print four regular dependencies: IOSurface, IOKit, CoreFoundation, and libSystem.

### AGX plugin pair

The target `AGXMetalA10` and donor `AGXMetalA11` loader records each print the same 14 regular dependency install names:

- `/System/Library/PrivateFrameworks/AggregateDictionary.framework/AggregateDictionary`
- `/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics`
- `/System/Library/Frameworks/Foundation.framework/Foundation`
- `/System/Library/PrivateFrameworks/GPURawCounter.framework/GPURawCounter`
- `/System/Library/PrivateFrameworks/IOGPU.framework/IOGPU`
- `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
- `/System/Library/Frameworks/IOSurface.framework/IOSurface`
- `/usr/lib/libcompression.dylib`
- `/usr/lib/libMobileGestalt.dylib`
- `/System/Library/Frameworks/Metal.framework/Metal`
- `/usr/lib/libc++.1.dylib`
- `/usr/lib/libSystem.B.dylib`
- `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
- `/usr/lib/libobjc.A.dylib`

This is a loader-metadata similarity between two different generation-specific plugin images. It does not make `AGXMetalA11` a substitute for `AGXMetalA10`, nor does it establish that either plugin loads or works on the target hardware.

## Cache-local loader metadata

The `Loader` line reports `prebuilt` for all 22 selected image records. It also prints a loader reference index. Those indexes belong to their respective cache data and are not cross-cache identities; they are distinct from the `ipsw dyld info -l` image-list indexes.

Selected printed loader reference indexes:

| Pair | Target loader ref index | Donor loader ref index |
|---|---:|---:|
| Metal | 192 | 6 |
| CoreGraphics | 14 | 14 |
| IOSurface | 368 | 224 |
| IOMobileFramebuffer | 308 | 378 |
| IOGPU | 1174 | 1237 |
| IOKit | 70 | 29 |
| IOAccelerator | 603 | 440 |
| AGXCompilerCore | 518 | 539 |
| MetalKit | 757 | 1070 |
| AGX plugin (A10 vs A11) | 2013 | 2553 |
| AppleMetalGLRenderer | 1946 | 2555 |

Some donor records also print loader flags such as `ro-objc`, `pre-2022`, and `overridable`, while the target records do not show the same flag strings. These are recorded parser metadata only; no behavior is inferred from them here.

## Parser-output exclusions and evidence limits

The `Sections` tables contain visibly implausible decoded offsets and sizes, including values that resemble ASCII fragments of install paths rendered as enormous integers. Those fields are excluded from this comparison and must not be used to infer Mach-O section locations or sizes.

The captured `ipsw dyld image -V` outputs do not print a Mach-O UUID. The report therefore does not claim image-binary identity. The dependency rows establish what the cache's prebuilt loader metadata prints for these image records; they do not establish that an image is loaded at runtime, that dependencies resolve successfully on a specific board, or that an IOKit provider attaches.

Matching dependency names and kinds are not proof of matching exports, private ABI/KPI compatibility, symbol binding, code-signing acceptance, GPU initialization, Metal rendering, kernel boot, or SpringBoard. The donor's extra Metal/CoreGraphics dependency edges are not automatically target blockers: their target-cache image presence has to be checked separately from their being a direct dependency in the donor record.

## Next bounded static work

Check the full image inventories for the donor-only direct Metal dependencies and the shared weak-link / CoreAnalytics records. Only query an image in a cache if its exact install path is present in that cache's full image list. This distinguishes a direct-loader-edge difference from simple cache-image absence.

The next diagnostic checks these exact paths:

- `/System/Library/Frameworks/Security.framework/Security`
- `/usr/lib/libcompression.dylib`
- `/usr/lib/libllvm-flatbuffers.dylib`
- `/System/Library/PrivateFrameworks/GPUCompiler.framework/Libraries/libGPUCompilerUtils.dylib`
- `/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics`

Run each query against target and donor only when the path is present in that cache's full image list. Preserve the status and stderr for each query. No binary extraction or device action is needed.

M6 remains in progress; M7/SpringBoard has not started.
