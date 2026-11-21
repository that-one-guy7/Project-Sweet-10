# 20H392 donor / 19H422 target libc++ cache image record comparison

## Scope

This note records the user's read-only lookup for the exact dyld image
path `/usr/lib/libc++.1.dylib` in two existing cache image inventories:

- Target: iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8
  build `19H422`, inventory `$HOME/19H422-dyld-images.json`.
- Donor: iPhone X `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16
  build `20H392`, inventory `$HOME/20H392-dyld-images.json`.

The physical iPhone 7 remains on iOS 12.1.4. This is read-only host-side
cache metadata. It does not establish filesystem presence outside the cache,
runtime loader resolution, library loading, or binary compatibility.

## Exact image-list records

| Field | Target 19H422 | Donor 20H392 |
|---|---|---|
| Match count | 1 | 1 |
| Image-list index | 150 | 93 |
| Full path | `/usr/lib/libc++.1.dylib` | `/usr/lib/libc++.1.dylib` |
| Version | `1300.36.0.0.0` | `1500.65.0.0.0` |
| Mach-O UUID | `16BE14F2-A677-3DF1-984D-BBAB893EE3B9` | `07F1FD58-7392-34FF-8D56-AE101EBC175A` |

Both inventories contain exactly one matching image record. Their image-list
indexes are cache-local and are not stable identifiers across the two caches.
The version strings and UUIDs differ.

## Relationship to MultitouchSupport loader records

The target 19H422 MultitouchSupport PrebuiltLoaderSet record lists six
regular dependent-loader rows. The donor 20H392 record lists those same
six rows plus one additional regular row:

`/usr/lib/libc++.1.dylib`.

The new image-list lookup shows that libc++ is nevertheless represented
in the target cache at index 150, version `1300.36.0.0.0`, UUID
`16BE14F2-A677-3DF1-984D-BBAB893EE3B9`. The donor cache contains it at
index 93, version `1500.65.0.0.0`, UUID
`07F1FD58-7392-34FF-8D56-AE101EBC175A`.

Therefore, the donor-only row is a difference in the compared
MultitouchSupport dependent-loader records. It is **not** evidence that
libc++ is missing from the target dyld cache. The cache image-list entries
do not establish whether the target loader resolves libc++ for this image
through another mechanism, whether it is loaded at runtime, or whether
the target and donor library builds are ABI-compatible.

## Interpretation limits

The different UUIDs identify distinct Mach-O build identities; they are
not a code-signature validation result. No raw byte comparison, export
surface comparison, ABI analysis, loader trace, or runtime library-load
test is claimed. The donor's newer version is not a reason to substitute
donor files into the target filesystem.

This closes the narrow cache-image-presence question raised by the
MultitouchSupport loader comparison. It does not prove that any difference
causes or explains a touch failure.

## Next bounded host-side research

The next useful static comparison is the target and donor
`MultitouchSupport` exported-symbol metadata, followed by checking which
of those symbols or libraries are directly referenced by the corresponding
`MultitouchHID` images if the cache parser exposes reliable records. Keep
export metadata, image-list identity, dependent-loader edges, and runtime
behavior as separate evidence categories.

No binary, shared-cache file, filesystem image, firmware file, or device
state is changed or committed by this documentation.
