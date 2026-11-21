# 20H392 donor dyld shared-cache multitouch image audit

## Purpose and evidence boundary

This report records the user's read-only inspection of the iPhone X
`iPhone10,3` / D22AP / A11-T8015 iOS 16.7.16 (20H392) SystemOS
dyld shared cache and compares the image-path/version records with the
iPhone 7 `iPhone9,1` / D10AP / A10-T8010 iOS 15.8.8 (19H422) target
reference.

The physical iPhone 7 remains on iOS 12.1.4. Both caches were inspected
from host-side mounted firmware filesystems. This report records dyld
image-list metadata only. It does not establish runtime image loading,
plugin factory execution, IOKit attachment, HID event delivery, or
cross-board compatibility.

## Donor cache and command

The donor cache path used by the user was:

```text
/home/hey/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64
```

The user ran `ipsw dyld info --dylibs` against that cache and saved the
text output as:

```text
/home/hey/20H392-multitouch-cache-list.txt
```

The saved report size was 293,678 bytes. The user supplied the grep output
for the four multitouch/HID image names. The result contained the
`MultitouchHID` image at the exact install path previously found in the
19H422 target cache.

## Direct image-list comparison

The following rows compare the user-supplied donor output with the
previously recorded 19H422 target image inventory.

| Image | 20H392 donor entry | Donor version | 19H422 target entry | Target version |
|---|---:|---|---:|---|
| `MultitouchHID` | 2557 | `6140.3.0.0.0` | 1948 | `5100.27.0.0.0` |
| `AppleHIDTransportSupport` | 1499 | `6140.1.0.0.0` | 2067 | `5100.32.0.0.0` |
| `MultitouchSupport` | 1648 | `6140.3.0.0.0` | 1249 | `5100.27.0.0.0` |
| `MultitouchSessionFilterSupport` | 2140 | `6140.3.0.0.0` | 2221 | `5100.27.0.0.0` |

The full `MultitouchHID` install path reported in the donor cache is:

```text
/System/Library/Extensions/AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/MultitouchHID
```

The target cache inventory reports the same full path. The donor image
indices and target image indices belong to separate cache inventories;
their numerical difference does not imply load order, priority, or
compatibility.

## UUID status and next metadata check

The supplied `ipsw dyld info --dylibs` text excerpt reports each image's
index, version, and path, but it does not include the donor
`MultitouchHID` Mach-O UUID. The donor UUID is therefore **not recorded
or inferred** in this report.

The documented `ipsw dyld image <cache> <image> -V` command prints an
image's ID, full name, flags, UUID, cache segments, and dependency
metadata. The next bounded check is to query the exact donor image path
with that command and record the resulting UUID. Until then, the target
UUID is known
(`304953E6-6B67-3CF1-B7CA-E011978210DE`) but the donor UUID comparison
remains incomplete.

## Interpretation

The supplied cache inventories establish that:

1. Both the 20H392 donor and 19H422 target cache image lists contain the
   `MultitouchHID` image at the same full install path.
2. The donor image-list version is `6140.3.0.0.0`, while the target
   image-list version is `5100.27.0.0.0`.
3. The three related donor multitouch/HID userland images listed above
   also have later version strings than their corresponding target
   records.
4. The donor and target are different hardware generations:
   A11/T8015 on iPhone10,3 versus A10/T8010 on iPhone9,1.

This is stronger than plist-only evidence because both cache inventories
list compiled image records for the plugin path. It remains metadata-level
evidence: no raw Mach-O bytes have been compared, the donor UUID has not
yet been retrieved, and no signature verification or runtime test is
claimed. The shared install path and previously observed matching plugin
type/factory UUID declarations do not establish binary compatibility,
provider attachment, or cross-board support.

The donor's later image-list versions must not be treated as a reason to
substitute donor files into the target filesystem. The target-native
19H422 image records remain the appropriate static reference for the
iPhone9,1 hardware identity.

## Evidence status

| Claim | Status |
|---|---|
| Donor 20H392 cache path | Supplied by user |
| Donor `MultitouchHID` path and image-list version | Confirmed in supplied grep output |
| Donor related multitouch/HID image paths and versions | Confirmed in supplied grep output |
| Target 19H422 corresponding paths and versions | Confirmed in the previously recorded target cache inventory |
| Donor `MultitouchHID` Mach-O UUID | Pending exact `ipsw dyld image` query |
| Raw donor/target Mach-O byte comparison | Not performed |
| Signature validation | Not performed |
| Runtime plugin loading or IOKit attachment | Not tested |
| Touch-event delivery on iPhone9,1 | Not tested |
| A11/T8015 donor binary compatibility with A10/T8010 target | Not established |

No proprietary binary, shared-cache file, filesystem image, KernelCache,
or raw DeviceTree is committed to this repository. No device, firmware,
partition, activation, security, or boot state was accessed or changed.
