# 19H422 / 20H392 AGXMetal plugin Mach-O load-command and import results

## Scope and provenance

This report records the uploaded agx-metal-plugin-load-commands.tar.gz
archive and a second static pass over the original AGX plugin --symbols -V
logs from agx-metal-export-logs.tar.gz.

- Target: iPhone 7, iPhone9,1 / D10AP / A10-T8010, iOS 15.8.8
  19H422, image /System/Library/Extensions/AGXMetalA10.bundle/AGXMetalA10.
- Donor: iPhone X, iPhone10,3 / D22AP / A11-T8015, iOS 16.7.16
  20H392, image /System/Library/Extensions/AGXMetalA11.bundle/AGXMetalA11.

The uploaded load-command archive contains two ipsw dyld macho --loads
--json outputs, two status files, and two empty stderr files. Both query
statuses are 0; both stderr files are empty. The preceding symbol-log
archive's AGXPlugin pair also had successful parser command statuses.

All results are host-side metadata from existing shared caches and saved
parser output. No Mach-O image was extracted, no iOS binary was executed,
and no device, firmware, partition, security, or boot state was changed.
The physical iPhone 7 remains on iOS 12.1.4.

## Main finding: export-trie load command is present on both images

Both images contain LC_DYLD_EXPORTS_TRIE, but the reported payload sizes
differ:

| Field | Target 19H422 AGXMetalA10 | Donor 20H392 AGXMetalA11 |
|---|---:|---:|
| Load command | LC_DYLD_EXPORTS_TRIE present | LC_DYLD_EXPORTS_TRIE present |
| Load-command data size | 16 bytes | 16 bytes |
| Trie payload size | **0 bytes** | **8 bytes** |
| Parser Dyld Exports heading | Not printed | Printed |
| Parsed export rows | No section emitted | Section emitted, zero rows |

This explains the earlier difference in the saved text logs. At the pinned
ipsw source revision, the Dyld Exports heading and row loop are emitted
only when the export-trie load command exists, its size is greater than
zero, and verbose mode is active. The pinned go-macho v1.1.296
DyldExports() method returns an empty export slice immediately when the
trie size is zero; for non-zero size it parses the trie payload. In the
donor case, the eight-byte payload was accepted by the parser but produced
no export rows in the saved output.

References to the exact parser implementation:
- [ipsw 3.1.749 dyld Mach-O command](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/dyld/dyld_macho.go)
- [go-macho v1.1.296 DyldExports implementation](https://github.com/blacktop/go-macho/blob/v1.1.296/file.go)
- [go-macho v1.1.296 export-trie parser](https://github.com/blacktop/go-macho/blob/v1.1.296/pkg/trie/trie.go)

The eight-byte donor trie payload itself was not extracted or independently
hex-inspected. The evidence supports "zero parsed rows" for the donor, not
a claim about the exact raw byte sequence or why it was emitted as eight
bytes.

## Mach-O identity and build metadata

| Field | Target AGXMetalA10 | Donor AGXMetalA11 |
|---|---|---|
| Mach-O type / CPU | DYLIB / AARCH64 ARM64 | DYLIB / AARCH64 ARM64 |
| LC_ID_DYLIB install name | .../AGXMetalA10.bundle/AGXMetalA10 | .../AGXMetalA11.bundle/AGXMetalA11 |
| LC_UUID | FFF046B5-917A-3817-BE5D-F99EFB994E0D | A28FFCAD-5B21-3D66-91E4-C7573948C36A |
| LC_BUILD_VERSION platform | iOS | iOS |
| Minimum OS / SDK | 15.8 / 15.8 | 16.7 / 16.7.3 |
| Linker version | 760 | 857.1 |
| LC_SOURCE_VERSION | 190.23.2.0.0 | 227.6.5.0.0 |
| Mach-O load-command count | 27 | 28 |
| Load-command bytes | 4,176 | 4,568 |
| LC_SEGMENT_64 names | __TEXT, __DATA_CONST, __DATA, __LINKEDIT | Same, plus __DATA_DIRTY |

The target and donor UUIDs differ, and their source versions and build
versions differ. These identify separate generation/build artifacts; UUID
or version differences alone do not decide compatibility.

## Symbol-table counts

| Field | Target AGXMetalA10 | Donor AGXMetalA11 |
|---|---:|---:|
| LC_SYMTAB.nsyms | 418 | 3,248 |
| LC_DYSYMTAB.nlocalsym | 0 | 2,784 |
| LC_DYSYMTAB.nundefsym | 418 | 464 |
| LC_DYSYMTAB.nextdefsym | 0 | 0 |
| Undefined symbol rows in saved Symtab output | 418 | 464 |

The displayed undefined-symbol rows split into normal external imports and
weak external imports:

| Import row kind | Target | Donor |
|---|---:|---:|
| Normal (undefined) external | 414 | 460 |
| Weak (undefined) weak external automatically hidden | 4 | 4 |
| Total undefined rows | 418 | 464 |

The four weak imports are identical in both outputs and are attributed to
libc++.1.dylib:

- __ZdaPv
- __ZdlPv
- __Znam
- __Znwm

## Normal undefined-import name comparison

Comparing exact (symbol name, provider library) pairs in the saved
Symtab rows gives:

| Result | Count |
|---|---:|
| Common normal import pairs | 401 |
| Target-only normal import pairs | 13 |
| Donor-only normal import pairs | 59 |
| Provider-name changes among common symbol names | 0 |

All 401 common normal import symbols retain the same printed provider
library in both images. The 13 target-only normal imports are:

| Symbol | Printed provider |
|---|---|
| _ADClientSetValueForScalarKey | AggregateDictionary |
| _IOGPUResourceCreate | IOGPU |
| _IOGPUResourceGetDataBytes | IOGPU |
| _IOGPUResourceGetGPUVirtualAddress | IOGPU |
| _IOGPUResourceRelease | IOGPU |
| _OBJC_CLASS_$_NSException | CoreFoundation |
| _OBJC_CLASS_$__MTLSWRaytracingAccelerationStructureCommandEncoder | Metal |
| __ZNKSt3__120__vector_base_commonILb1EE20__throw_length_errorEv | libc++.1.dylib |
| ___error | libSystem.B.dylib |
| __os_crash_fmt | libSystem.B.dylib |
| __os_log_pack_fill | libSystem.B.dylib |
| __os_log_pack_size | libSystem.B.dylib |
| _kIOMainPortDefault | IOKit |

The donor-only set has 59 normal import pairs. Representative names include
_MTLProgressBinsMake, _MTLBVHDescriptorForMTLAccelerationStructureDescriptor,
_OBJC_CLASS_$_MTLAccelerationStructureTriangleGeometryDescriptor,
_OBJC_CLASS_$_IOGPUMetalAccelerationStructure, _objc_retain_x19,
_objc_opt_respondsToSelector, _os_parse_boot_arg_int, and
_kIOMasterPortDefault.

The provider distribution also changes notably in the donor-only imports:
25 are from Metal, 22 from libobjc, 6 from libSystem, 3 from IOGPU, and
one each from CoreFoundation, libc++, and IOKit. The target-only imports
include four IOGPU names, four libSystem names, and one each from
AggregateDictionary, CoreFoundation, Metal, libc++, and IOKit.

This is a comparison of the Mach-O symbol table's printed undefined import
records and their provider labels. It is not a record of resolved runtime
bindings. The saved output contains no Dyld Binds section, so no bind
locations, fixup targets, or successful dependency resolutions are claimed.

## Direct dylib load-command dependencies

Both images have 14 LC_LOAD_DYLIB commands, and their exact install-name
sets are identical. Six shared dependencies print different current-version
strings; their compatibility-version strings remain equal:

| Dependency | Target current version | Donor current version | Compatibility version |
|---|---:|---:|---:|
| CoreFoundation | 1866 | 1979.1.102 | 150 |
| Foundation | 1866 | 1979.1.102 | 300 |
| Metal | 261.13 | 306.6.6 | 1 |
| GPURawCounter | 25 | 27.3 | 1 |
| libSystem.B.dylib | 1311.120.1 | 1319.100.3 | 1 |
| libc++.1.dylib | 1300.36 | 1500.65 | 1 |

The other eight dependency paths have the same printed current-version and
compatibility-version values in the two load-command records. This exact
install-name overlap is metadata only; it does not prove that target and
donor symbol implementations or ABIs match.

## Interpretation and limits

1. The initial target/donor export-log difference is explained at the
   parser-output level: target trie size is zero, while donor trie size is
   eight bytes and still yielded no parsed rows.
2. Neither plugin produced a non-empty export list in the saved output.
   The evidence does not justify saying that the A10 plugin exports
   symbols that the A11 plugin lacks, or the reverse.
3. Both images have zero externally-defined symbol-table entries in the
   printed LC_DYSYMTAB fields. Their displayed undefined imports differ:
   13 target-only and 59 donor-only normal imports, plus four common weak
   imports.
4. The shared 14 dependency install names do not prove compatible versions,
   matching symbol implementations, dyld resolution, code-signing validity,
   or hardware support.
5. These are different iOS releases and different SoC generations. The
   metadata differences cannot be attributed to hardware alone.
6. Do not treat the donor AGXMetalA11 plugin as a substitute for the target
   AGXMetalA10 plugin.

## Project status

PR #106, which corrected resolver-address classification and recorded the
preceding export-name results, is merged. This report is the next
host-side static evidence update. M5 graphics research remains static;
M6 userland research remains in progress; M7/SpringBoard has not started.
The physical iPhone 7 remains on iOS 12.1.4.
