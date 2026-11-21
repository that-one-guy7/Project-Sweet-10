# 20H392 donor / 19H422 target MultitouchSupport loader comparison

## Scope and identity

This report compares the user-supplied output of the read-only command
`ipsw dyld image <cache> <image>` for:

```text
/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport
```

- Target: iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8
  build `19H422`.
- Donor: iPhone X `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16
  build `20H392`.
- The physical iPhone 7 remains on iOS 12.1.4.

This is static shared-cache loader metadata from host-side IPSW inspection.
It does not establish runtime dependency resolution, library loading,
touch event delivery, or compatibility between the donor and target boards.

The separate JSON cache inventories identify the corresponding images:

| Field | Target 19H422 | Donor 20H392 |
|---|---|---|
| Image-list index | 1249 | 1648 |
| Version | `5100.27.0.0.0` | `6140.3.0.0.0` |
| Mach-O UUID | `0EAF98B3-8D31-3A90-A578-1787797B9467` | `1B6ABB86-B8A9-3941-A66A-EC9715F6B034` |

The loader reference indexes printed by `ipsw dyld image` are separate
fields from the image-list indexes above. Target loader reference is 1248;
donor loader reference is 1647. Do not conflate the two index types.

## Loader field comparison

| Field | Target 19H422 | Donor 20H392 |
|---|---|---|
| VM Size | `0x3d3f0000` | `0x354c8000` |
| Loader flags | `prebuilt|in-cache-dylib|objc|never-unload` | `prebuilt|in-cache-dylib|objc|never-unload|ro-objc|pre-2022` |
| Loader reference | `index: 1248` | `index: 1647` |
| Info flags | `regions=5` | `overridable|regions=5` |
| Exports trie | offset `0x01c64b98`, size `0x1ca8` | offset `0x0aaa68b0`, size `0x1d78` |
| Region count | 5 | 5 |

The records use the same five-region count and broad permission pattern,
but their VM sizes, exports-trie locations/sizes, flags, and region
mappings differ.

## Region metadata

Target 19H422:

| Region | File offset | File size | VM offset | Permissions | Zero Fill | RO Data |
|---:|---:|---:|---:|---|---|---|
| 1 | `0x0d1c3000` | `0x00025000` | `0x00000000` | `r-x` | false | false |
| 2 | `0x0635bfa0` | `0x00002370` | `0x24dc8fa0` | `rw-` | false | false |
| 3 | `0x0af4cf40` | `0x00000498` | `0x2b9b9f40` | `rw-` | false | false |
| 4 | `0x07fefb98` | `0x00000048` | `0x28a5cb98` | `rw-` | false | false |
| 5 | `0x002ec000` | `0x0b9e0f19` | `0x31a0d000` | `r--` | false | false |

Donor 20H392:

| Region | File offset | File size | VM offset | Permissions | Zero Fill | RO Data |
|---:|---:|---:|---:|---|---|---|
| 1 | `0x02968000` | `0x00026000` | `0x00000000` | `r-x` | false | false |
| 2 | `0x01487ed8` | `0x000027e0` | `0x189b7ed8` | `rw-` | false | false |
| 3 | `0x03719aa0` | `0x000002b8` | `0x1cc49aa0` | `rw-` | false | false |
| 4 | `0x05da3f68` | `0x000000a1` | `0x1f2d3f68` | `rw-` | false | false |
| 5 | `0x0005c000` | `0x13da4000` | `0x21724000` | `r--` | false | false |

Both records use the permission sequence `r-x`, `rw-`, `rw-`,
`rw-`, `r--`. The offsets and sizes are from separate shared-cache
layouts; they are not directly comparable as offsets into standalone
Mach-O files.

## Listed dependent-loader records

The command prints a `Dependents` block. The pinned ipsw parser
`pkg/dyld/prebuilt.go` reads the PrebuiltLoaderSet
`DependentLoaderRefsArrayOffset` and associated dependent-kind array to
populate these records. The exact parser source used for this project is
[prebuilt.go at the pinned ipsw commit](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/pkg/dyld/prebuilt.go).

Target 19H422 reports six regular rows:

1. `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit`
2. `/usr/lib/libIOReport.dylib`
3. `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation`
4. `/System/Library/Frameworks/Foundation.framework/Foundation`
5. `/usr/lib/libobjc.A.dylib`
6. `/usr/lib/libSystem.B.dylib`

Donor 20H392 reports the same six regular rows, plus one additional
regular row:

7. `/usr/lib/libc++.1.dylib`

Therefore, the target record reports six dependent-loader rows, while the
donor reports seven. The only printed row difference is donor-side
`libc++.1.dylib`. The absence of that row from the target record does not
prove that libc++ is absent from the target filesystem or dyld cache image
inventory. That presence question remains open until the target and donor
image inventories are searched for the exact `/usr/lib/libc++.1.dylib`
image record.

The six shared rows are listed as `regular` in both outputs. No other
weak-link or re-export rows were printed for these two records.

## Parser caveat

Both outputs contain a `Sections` block with implausibly large offsets
and sizes, including values that resemble decoded ASCII fragments. Those
section fields are excluded from interpretation, consistent with the
earlier MultitouchHID cache audits. This is not evidence that either cache
image is corrupt.

The region and dependency rows above are recorded as printed by successful
commands. No code-signature validation is claimed.

## Interpretation

The target and donor MultitouchSupport records share the same install path,
the same five-region permission sequence, and six matching regular
dependent-loader rows. They differ in VM size, loader flags, Info flags,
exports-trie metadata, region mappings, cache image version, and UUID.
The donor additionally reports a regular `libc++.1.dylib` row.

These are static metadata differences. They do not show that the additional
donor row causes a runtime failure, that target libc++ is missing, or that
the donor image can be substituted for the target image. The separate
dependency image inventory records already establish different
MultitouchSupport image versions and UUIDs:
`5100.27.0.0.0` / `0EAF98B3-8D31-3A90-A578-1787797B9467` on target,
versus `6140.3.0.0.0` / `1B6ABB86-B8A9-3941-A66A-EC9715F6B034`
on donor.

## Next bounded host-side check

Search both existing read-only dyld image inventories for the exact
`/usr/lib/libc++.1.dylib` path. Record its image-list index, version,
and UUID where present. This will distinguish a donor-only loader edge
from actual target cache-image-list absence. It will not prove filesystem
presence outside the cache, runtime resolution, or library loading.

No binary, shared-cache file, filesystem image, firmware file, or device
state is changed or committed by this documentation.
