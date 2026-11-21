# iPhone9,1 19H422 / iPhone10,3 20H392 AGX and Metal Dyld Exports results

## Scope and provenance

This report records the uploaded `agx-metal-export-logs.tar.gz` archive. It
contains 22 target/donor parser logs for 11 graphics-related image pairs,
22 stderr files, 11 empty comparison-output files, 11 comparison stderr
files, and `query-status.tsv`.

The logs were produced with standalone `ipsw dyld macho <DSC> <DYLIB>
--symbols -V` against the host-side shared caches already identified by
the project:

- Target: iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8
  `19H422`.
- Donor: iPhone X `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16
  `20H392`.

All 22 cache-parser queries exited with status 0. Their stderr files
contain only the `Parsing Cache` progress message; they do not contain
parser error messages.

The comparison subprocesses did **not** run on the Ubuntu host: each
comparison stderr reports that Python could not find the relative
`tools/compare_dyld_exports.py` path from the current working directory.
The saved source logs are intact. The comparisons below were independently
re-run against those saved text logs using the repository's export-row
format and corrected resolver classification. The zero-byte comparison
files in the uploaded archive are not treated as empty results.

The physical iPhone 7 remains on iOS 12.1.4. No phone, firmware, partition,
security state, or boot state was accessed or changed.

## Per-image results

Counts are from the parser's `Dyld Exports` section only. A row is one
printed export entry; unique names are compared as exact strings. The
target-only and donor-only columns are per image pair, not a count of
unique names across the whole operating system.

| Image pair | Target rows | Donor rows | Common names | Target-only names | Donor-only names | Kind-category differences |
|---|---:|---:|---:|---:|---:|---:|
| Metal | 960 | 1,063 | 959 | 1 | 104 | 0 |
| CoreGraphics | 2,161 | 2,383 | 2,156 | 5 | 227 | 0 |
| IOSurface | 546 | 596 | 545 | 1 | 51 | 0 |
| IOMobileFramebuffer | 133 | 161 | 133 | 0 | 28 | 0 |
| IOGPU | 248 | 281 | 247 | 1 | 34 | 0 |
| IOKit | 2,095 | 2,119 | 2,091 | 4 | 28 | 0 |
| IOAccelerator | 156 | 156 | 156 | 0 | 0 | 0 |
| AGXCompilerCore | 11 | 33 | 11 | 0 | 22 | 0 |
| MetalKit | 41 | 42 | 41 | 0 | 1 | 0 |
| AppleMetalGLRenderer | 131 | 131 | 131 | 0 | 0 | 0 |

Across these ten usable pairs, the per-pair totals are 6,482 target rows
and 6,965 donor rows, with 6,470 common name instances, 12 target-only
name instances, and 495 donor-only name instances. No duplicate export
names appeared in any of the ten parsed sections.

The aggregate figures are sums of separate image-pair comparisons. They
must not be read as 6,470 unique symbols across the system: the same
symbol name may appear in more than one image.

## Target-only names

The exact target-only names were:

- Metal: `_MTLAddDeviceClass`.
- CoreGraphics:
  - `_CGGStateGetInfoDictionary`
  - `_CGGStateSetInfoDictionary`
  - `_CGPDFStreamGetAssociation`
  - `__ZN12CGBlitBufferC1Emmm`
  - `__ZN12CGBlitBufferC2Emmm`
- IOSurface: `__sniffBulkKeys`.
- IOGPU: `_IOGPUDeviceSetResourcesPurgeable`.
- IOKit:
  - `__IOHIDEventSystemConnectionGetProperty`
  - `__IOHIDEventSystemGetPropertyForConnection`
  - `__IOHIDSessionGetPropertyForClient`
  - `___IOHIDEventSystemClientRefresh`

The remaining five usable pairs had no target-only names.

## Representative donor-only names

The donor-only sets are largest in CoreGraphics (227 names) and Metal
(104 names). Examples from the exact parsed names include:

| Image | Donor-only examples |
|---|---|
| Metal | `_MTLIOCreateCompressionContext`, `_MTLIOCreateDecompressionContext`, `_MTLGetOptimalCompilerProcessesCount`, `_OBJC_CLASS_$_MTLMeshRenderPipelineDescriptor` |
| CoreGraphics | `_CGDisplayListEnumerateEntriesWithOptions`, `_CGImageCreateCopyByApplyingToneMapping`, `_CGContextGetToneMappingInfo` |
| IOSurface | `_IOSurfaceGetBaseAddressOfCompressedTileDataRegionOfSliceAndPlane`, `_IOSurfaceGetSliceCount`, `_OBJC_CLASS_$_IOSurfaceMemoryPool` |
| IOMobileFramebuffer | `_IOMFBGainEncoderCreate`, `_IOMobileFramebufferSwapSetGainMap` |
| IOGPU | `_IOGPUIOCommandQueueCreate`, `_IOGPUMetalDeviceShmemUpdateTrimLevel` |
| IOKit | `_IOHIDEventCreateProximtyLevelEvent`, `_IOAVHDMIFRLRateString` |
| AGXCompilerCore | `_AIRNTGetSupportedArchs`, `_AIRNTEmitPipelineImage` |
| MetalKit | `_MTKTextureLoaderOptionLoadAsArray` |

IOAccelerator and AppleMetalGLRenderer had identical exported-name sets
in the captured output.

These are export-name observations only. A donor-only name does not prove
that the target userland needs it, that the target lacks equivalent
functionality elsewhere, or that it blocks startup. A target-only name
does not establish that the donor lacks an equivalent.

## Export-kind and resolver details

After normalizing resolver records to the `resolver` category, no common
export name has a different printed export-kind category in these ten
comparisons.

Two common CoreGraphics names have resolver-address values that differ:

| Name | Target 19H422 resolver value | Donor 20H392 resolver value |
|---|---:|---:|
| `_CGApplyGainMapHeadRoom` | `0x1824828cc` | `0x188b7bce8` |
| `_CGBufIsConstantValue` | `0x1824828d8` | `0x188b7bcf4` |

The previous raw-string comparison classified these as kind differences
because the parser embeds the resolver address in the displayed
`resolver=0x...` text. The comparator has now been corrected to report
the resolver category separately from its address. Resolver values and
export addresses belong to their respective cache layouts; their numeric
difference is not a compatibility measurement.

The printed first export address differed for every common name in these
separate target/donor cache comparisons. This is expected cache-local
metadata and is not interpreted as a symbol implementation difference.

## AGX plugin pair: unresolved parser evidence

The generation-specific plugin pair could not be compared:

- Target `AGXMetalA10`: no `Dyld Exports` heading was printed.
- Donor `AGXMetalA11`: the heading and separator were printed, but no
  export rows followed.

Both underlying `ipsw` commands nevertheless exited status 0. These
outputs do not establish that either plugin has no externally visible
symbols. The result is recorded as `NO_HEADING` for the target and
`EMPTY_SECTION` for the donor; the comparator correctly refuses to
silently turn either condition into an empty symbol set.

The next bounded check is to inspect the two cached Mach-O load-command
tables (without extraction) and record whether each contains
`LC_DYLD_EXPORTS_TRIE`, along with its reported data offset and size.
This may clarify the parser-output difference, but still would not prove
ABI or runtime compatibility.

## Tooling correction

PR #105 is merged and adds the log-only comparator. The archive's
comparison stage was invoked from a directory where the relative
`tools/compare_dyld_exports.py` path did not exist. Run the helper from
the repository root, or pass its absolute path, for example:

```bash
python3 "$HOME/Project-Sweet-10/tools/compare_dyld_exports.py" \
  --target "$HOME/agx-metal-static-audit/export-symbols/19H422-Metal.txt" \
  --donor "$HOME/agx-metal-static-audit/export-symbols/20H392-Metal.txt"
```

Replace `$HOME/Project-Sweet-10` with the actual local clone directory
if it is named differently. The cache-query logs themselves succeeded;
only the separate comparison invocation failed due to the script path.

## Interpretation limits and next step

Export-name overlap is not implementation identity, calling-convention
compatibility, structure-layout compatibility, private API/KPI
compatibility, code-signing validity, dependency resolution, IOKit
attachment, GPU initialization, Metal rendering, kernel boot, or
SpringBoard stability. The target and donor are different operating
system releases and different SoCs, so the observed export differences
cannot be attributed to hardware alone.

Next, inspect load-command metadata for the A10 and A11 AGX plugin pair
to clarify the missing/empty export sections. Keep the check host-side
and read-only; do not extract or substitute binaries. M5 graphics research
remains static, M6 userland research remains in progress, and M7/SpringBoard
has not started.
