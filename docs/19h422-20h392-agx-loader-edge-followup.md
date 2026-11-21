# 19H422 / 20H392 AGX loader-edge follow-up

## Scope and provenance

This report records the user's uploaded `loader-edge-followup.tar.gz` archive. It contains five image-query outputs per cache (10 total), corresponding stderr files, and a status table. The commands used standalone `ipsw` 3.1.749 against the already-mounted host-side dyld shared caches.

All ten queries exited status 0:

| Cache | Image | Query status |
|---|---|---:|
| 19H422 | Security | 0 |
| 19H422 | libcompression | 0 |
| 19H422 | libllvm-flatbuffers | 0 |
| 19H422 | libGPUCompilerUtils | 0 |
| 19H422 | CoreAnalytics | 0 |
| 20H392 | Security | 0 |
| 20H392 | libcompression | 0 |
| 20H392 | libllvm-flatbuffers | 0 |
| 20H392 | libGPUCompilerUtils | 0 |
| 20H392 | CoreAnalytics | 0 |

Each query produced an image record with a `prebuilt` loader. Thus all five exact install paths are represented in both selected cache inventories. This is an important distinction: the prior report's “donor-only” items are donor-only dependency **edges** from the selected parent loader records, not images absent from the 19H422 cache.

## Exact image paths and loader records

| Image | Exact install path | 19H422 record | 20H392 record |
|---|---|---|---|
| Security | `/System/Library/Frameworks/Security.framework/Security` | Present; prebuilt, in-cache dylib | Present; prebuilt, in-cache dylib |
| libcompression | `/usr/lib/libcompression.dylib` | Present; prebuilt, in-cache dylib | Present; prebuilt, in-cache dylib |
| libllvm-flatbuffers | `/usr/lib/libllvm-flatbuffers.dylib` | Present; prebuilt, in-cache dylib | Present; prebuilt, in-cache dylib |
| libGPUCompilerUtils | `/System/Library/PrivateFrameworks/GPUCompiler.framework/Libraries/libGPUCompilerUtils.dylib` | Present; prebuilt, in-cache dylib | Present; prebuilt, in-cache dylib |
| CoreAnalytics | `/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics` | Present; prebuilt, in-cache dylib | Present; prebuilt, in-cache dylib |

## Dependency records

### Security

Both versions print the same 11 regular dependency install paths:

- `/usr/lib/libsqlite3.dylib`
- `/usr/lib/libcoretls.dylib`
- `/usr/lib/libcoretls_cfhelpers.dylib`
- `/usr/lib/libMobileGestalt.dylib`
- `/usr/lib/libbsm.0.dylib`
- `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
- `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
- `/System/Library/PrivateFrameworks/SoftLinking.framework/SoftLinking`
- `/usr/lib/libobjc.A.dylib`
- `/usr/lib/libc++.1.dylib`
- `/usr/lib/libSystem.B.dylib`

### libcompression

Both versions print the same two regular dependencies:

- `/usr/lib/liblzma.5.dylib`
- `/usr/lib/libSystem.B.dylib`

### libllvm-flatbuffers

Both versions print the same two regular dependencies:

- `/usr/lib/libc++.1.dylib`
- `/usr/lib/libSystem.B.dylib`

### libGPUCompilerUtils

Both versions print the same two regular dependencies:

- `/usr/lib/libc++.1.dylib`
- `/usr/lib/libSystem.B.dylib`

This image's install path is present in both caches. Its presence does not change the earlier finding that the selected Metal records have a weak-link edge to GPUCompilerUtils in both versions.

### CoreAnalytics

Both versions print the same six regular dependencies:

- `/System/Library/PrivateFrameworks/AppleSauce.framework/AppleSauce`
- `/System/Library/Frameworks/Foundation.framework/Foundation`
- `/usr/lib/libobjc.A.dylib`
- `/usr/lib/libc++.1.dylib`
- `/usr/lib/libSystem.B.dylib`
- `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`

This confirms that CoreAnalytics itself is present in the target cache and has a prebuilt loader record. The earlier CoreGraphics difference is specifically that the donor CoreGraphics record prints a weak-link dependency edge to CoreAnalytics while the target CoreGraphics record did not print that edge.

## Updated interpretation of the four donor-only edges

The prior PrebuiltLoader report identified four additional typed edges in the donor's selected parent records:

| Parent loader record | Donor-only edge | Is the dependency image present in target cache? |
|---|---|---|
| Metal | regular `Security.framework/Security` | Yes |
| Metal | regular `/usr/lib/libcompression.dylib` | Yes |
| Metal | weak-link `/usr/lib/libllvm-flatbuffers.dylib` | Yes |
| CoreGraphics | weak-link `CoreAnalytics.framework/CoreAnalytics` | Yes |

Therefore, none of these four differences is explained by the dependency image being absent from the target dyld cache. The difference is in the selected parent image's printed PrebuiltLoader dependency metadata, not simple cache inventory availability.

The target and donor dependency images themselves have matching printed dependency install-name sets for these five inspected pairs. This does not establish matching exports, UUIDs, ABI, symbols, versions, runtime load behavior, or that a parent image can safely use a dependency across OS generations.

## Metadata caveats

The output's `Sections` rows again contain visibly implausible decoded offsets and sizes, often resembling ASCII fragments interpreted as large integers. Those fields are excluded from analysis. Loader reference indexes are cache-local and must not be compared as identifiers across caches.

The output does not provide Mach-O UUIDs. Query status 0 confirms successful command completion, not runtime loading or compatibility.

## Project status and safety boundary

This is host-side static dyld cache metadata analysis only. No device, firmware, partition, security, or boot state was changed. The physical iPhone 7 remains on iOS 12.1.4. M6 remains in progress; M7/SpringBoard has not started.
