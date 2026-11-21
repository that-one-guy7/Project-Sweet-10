# dyld cache and filesystem-path evidence: source-backed interpretation

## Purpose

This note verifies how to interpret the Project Sweet-10 GUI framework path scan. It separates four different evidence types:

1. A standalone filesystem object at an install path.
2. An image advertised in a dyld shared-cache image list.
3. A PrebuiltLoader record and its dependency references.
4. Runtime resolution/loading by dyld.

They are related, but they are not interchangeable. The goal here is to prevent a path lookup or a cache index from being mistaken for a runtime compatibility result.

## Findings from Apple's public dyld sources

### Shared-cache contents are not the same thing as standalone files

Apple's shared-cache layout note explains that the cache builder copies the segments of each source dylib into shared-cache mappings. The cache is therefore a separately laid-out collection of image contents, not simply a directory listing of the source framework files.

Apple's `PrebuiltLoader.cpp` makes the operational distinction especially clear:

- If a PrebuiltLoader is marked `dylibInDyldCache`, the validation path checks that a shared cache is available and, where relevant, checks for a filesystem override that should supersede the cached dylib.
- In the separate `not in dyld cache` branch, validation checks the ordinary file path. If the file is missing, that loader is marked invalid.

This supports a narrow conclusion: **failure to find a standalone file at one install path does not prove that the corresponding image is absent from a shared cache.** It also does not prove that the image is present in the cache; that requires a separate cache-image record for the exact image/path.

Sources:
- [Apple dyld shared-cache layout](https://github.com/apple-oss-distributions/dyld/blob/main/doc/CacheLayout.md), especially the cache-building section.
- [Apple dyld PrebuiltLoader.cpp](https://github.com/apple-oss-distributions/dyld/blob/main/dyld/PrebuiltLoader.cpp), especially `PrebuiltLoader::invalidateInIsolation`, the `dylibInDyldCache` branch and the subsequent `not in dyld cache` branch.

### PrebuiltLoader references and cache image-list indexes are different index spaces

Apple's dyld4 design note describes `LoaderRef` as a reference to another Loader using a 16-bit value that selects a PrebuiltLoaderSet and an index within that set. The same note says the OS shared cache has a PrebuiltLoaderSet containing a PrebuiltLoader for each dylib in the cache.

Separately, Apple's `DyldSharedCache` interface exposes `images()` and `imagesCount()` for the array of `dyld_cache_image_info` entries. These are distinct structures and APIs. A PrebuiltLoader reference index must therefore not be equated with a cache image-list index, and no constant offset should be inferred between them.

Sources:
- [Apple dyld4 design documentation](https://github.com/apple-oss-distributions/dyld/blob/main/doc/dyld4.md), sections “PrebuiltLoader and PrebuiltLoaderSet”.
- [Apple DyldSharedCache.h](https://github.com/apple-oss-distributions/dyld/blob/main/common/DyldSharedCache.h), declarations of `images()` and `imagesCount()`.

## Applying this to Project Sweet-10

### Target 19H422 result

The user-run scan checked 18 exact candidate paths under one supplied target root, at wrapper depths 0, 1, and 2. All 18 reported `not-found-under-scanned-roots`.

That finding is valid only for those exact paths and that supplied root. It is not a recursive basename search, does not cover unlisted volumes, and does not show whether a candidate is represented in the target dyld cache at another install name. The report must continue to use the exact status name `not-found-under-scanned-roots`; it must not be shortened to “absent”.

The target cache image-list record for ExtensionFoundation at image-list index 1093 under the PrivateFrameworks path remains a separate observation. Its presence in the cache inventory and the scan's failure to find a standalone file at the checked path can both be true.

### Donor 20H392 volume layout is not proof of target 19H422 layout

The existing donor inventory documents two separately mounted iPhone X 20H392 images:

- `087-86698-044.dmg`: OS root filesystem.
- `087-86593-047.dmg`: Cryptex1 / SystemOS.

The donor dyld shared cache was inspected under the separately mounted SystemOS tree. The same inventory explicitly warns that root-filesystem-only donor searches produced incomplete apparent framework misses.

This is strong reason to make volume coverage explicit. It is **not** evidence that the iPhone 7 19H422 target has the same two-image layout. The donor and target are different devices and OS builds. The BuildManifest audit currently documented for 20H392 is a standalone donor plist; that audit records device identities, KernelCache and DeviceTree metadata, but it does not establish a complete target 19H422 volume inventory.

Consequently, the 18-path target scan must not be described as a scan of every possible target system volume until the target build's own component inventory has been checked.

Project-local evidence:
- [20H392 split dyld shared-cache inventory](20h392-dyld-cache-inventory.md).
- [Uploaded 20H392 BuildManifest audit](uploaded-20h392-buildmanifest-audit.md).
- [19H422 GUI framework path-presence results](iphone91-19h422-gui-framework-path-presence-results.md).

## Version and source caveats

The Apple dyld source links above point to the public repository's current `main` branch. They are authoritative descriptions of Apple's published dyld implementation, but they are not a pinned source snapshot proven to match the exact dyld binary shipped in iOS 16.7.16 build 20H392 or iOS 15.8.8 build 19H422. Use them to verify the architecture and avoid conflating data structures; do not treat them as a byte-for-byte specification for either build.

A secondary implementation reference, the Rust `object` crate's Mach-O parser, records that the dyld shared-cache subcache-entry v1 format dates from dyld-940 (macOS 12 / iOS 15), while v2 was added in dyld-1042.1 (macOS 13 / iOS 16). This is a useful warning that the target and donor cache generations can differ in cache-header/subcache details. It is not a substitute for inspecting the actual target and donor cache headers.

Source: [object crate Mach-O format definitions](https://docs.rs/object/latest/src/object/macho.rs.html), definitions for `DyldSubCacheEntryV1` and `DyldSubCacheEntryV2`.

## Revised evidence rules

1. Keep standalone filesystem presence, cache image-list membership, PrebuiltLoader records, and runtime behavior in separate columns/sections.
2. Preserve the `not-found-under-scanned-roots` label with the exact roots and wrapper depths.
3. Never treat a PrebuiltLoader reference index as a cache image-list index.
4. Do not infer the 19H422 target's volume layout from the 20H392 iPhone X donor.
5. Before any target-wide missing-framework conclusion, identify the filesystem components actually supplied by the 19H422 target build and record every root that was inspected.
6. A filename match is not a Mach-O validation, code-signature check, ABI test, loader-resolution test, service-start result, or SpringBoard result.

## Next host-side research checkpoint

The next useful read-only checkpoint is to establish the target 19H422 image/component inventory from that build's own BuildManifest and archive metadata, then record which of those filesystems are actually mounted. Only after that should the exact candidate names be inventoried across each confirmed target root and compared against the target dyld cache image list.

No device interaction is part of this research note. The physical iPhone 7 remains on iOS 12.1.4. M6 remains in progress; M7/SpringBoard has not started.
