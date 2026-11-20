# iOS 16.7.16 (20H392) split dyld shared-cache inventory

## Scope and source

This is a read-only inventory of the iPhone X 20H392 donor SystemOS Cryptex
mounted locally with `apfs-fuse`. The physical Project Sweet-10 target remains
iPhone 7 `iPhone9,1` / D10AP / A10-T8010. This cache belongs to the iPhone X
donor userland; it is not an iPhone 7 system image.

The donor images were identified from the pinned `ios-sweet` notes:

| Image | Role | Expected size |
|---|---|---:|
| `087-86698-044.dmg` | OS root filesystem | 4,730,814,044 bytes |
| `087-86593-047.dmg` | Cryptex1 / SystemOS | 2,743,074,816 bytes |

Both local file sizes were checked by the user and match those expected values.
The OS root filesystem and SystemOS Cryptex are mounted separately. Earlier
checks against the root filesystem alone returned many apparent missing
framework paths; those results were incomplete and must not be described as
missing from the complete donor system.

## Cache selected

The selected cache is:

```text
System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64
```

Do not confuse it with the separate DriverKit cache at
`System/DriverKit/System/Library/dyld/dyld_shared_cache_arm64`.

The user inspected the cache with ipsw 3.1.749
(commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`). The image-list
inspection used `ipsw dyld info -l`; a second header/mapping inspection used
`ipsw dyld info "$CACHE"`. Both completed successfully. The latter reported
the following main-cache header:

| Field | Observed value |
|---|---|
| Magic | `dyld_v1   arm64` |
| Platform | iOS |
| OS version | 16.7 |
| Images | 2,710 |
| Subcaches | 42 |
| Cache UUID | `8F970452-C9E3-3E88-B114-FEB1864BC9E0` |

The selected main cache file is 393,216 bytes (384 KiB). The user also listed
the on-disk companions: numbered subcache files `.01` through `.42`, the
`.dylddata` and `.dyldlinkedit` companions, and the `.symbols` file.
The `ipsw dyld info "$CACHE"` output enumerated subcache UUIDs and mappings.
This confirms the split-cache set is readable; do not concatenate, rename, or
treat companion files as independent caches.

### APFS-FUSE mount layout observed

Both donor DMGs were mounted at separate host mountpoints. In this installed
`apfs-fuse` layout, each mountpoint contains a child directory named
`root`; the iOS filesystem hierarchy is below that child. In particular,
the working SystemOS cache path is:

```text
$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64
```

The outer `root` is the host mountpoint; the inner `root` is the directory
exposed by the APFS-FUSE mount. This distinction matters when reproducing the
inspection from the Ubuntu shell. The main cache was identified by
`ipsw` as `dyld_v1   arm64` even though the generic `file` utility
described it only as `data`.

## GUI-relevant images listed in the cache

The `ipsw dyld info -l` output lists the following paths and versions. These
are donor-side cache image-list records, not a complete dependency graph.

| Cached image path | Reported version |
|---|---|
| `/System/Library/Frameworks/Foundation.framework/Foundation` | 1979.1.102 |
| `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation` | 1979.1.102 |
| `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics` | 1690.8.1 |
| `/System/Library/Frameworks/Metal.framework/Metal` | 306.6.6 |
| `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit` | 2022.140.2.701.1 |
| `/System/Library/Frameworks/IOSurface.framework/IOSurface` | 336.60.1 |
| `/System/Library/Frameworks/AVFoundation.framework/AVFoundation` | 2165.7.1 |
| `/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices` | 540.114.1 |
| `/System/Library/PrivateFrameworks/BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation` | 540.114.1 |
| `/System/Library/PrivateFrameworks/BackBoardHIDEventProcessors.framework/BackBoardHIDEventProcessors` | 540.114.1 |
| `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices` | 803.120.4 |
| `/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard` | 803.120.4 |
| `/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard` | 4344.149.1.2 |
| `/System/Library/PrivateFrameworks/SpringBoardServices.framework/SpringBoardServices` | 4344.149.1.2 |
| `/System/Library/PrivateFrameworks/SpringBoardHome.framework/SpringBoardHome` | 4344.149.1.2 |

The listed entries overlap with the direct load commands previously reported
for donor `backboardd`, `runningboardd`, and the SpringBoard executable.
This confirms that the selected iPhone X shared cache advertises corresponding
framework images. It does not yet prove each image's complete transitive
dependencies, successful runtime loading, or compatibility with iPhone9,1.

## Reproduction

With the SystemOS APFS volume mounted read-only and readable by the current
Ubuntu user:

```sh
SYSTEM_MNT="$HOME/20H392/systemos-mnt/root"
CACHE="$SYSTEM_MNT/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
ipsw version
file "$CACHE"
ipsw dyld info "$CACHE" > "$HOME/20H392/dyld-cache-header-and-mappings.txt"
ipsw dyld info -l "$CACHE" > "$HOME/20H392/dyld-cache-info.txt"
```

For the user-observed run, `ipsw version` reported 3.1.749 and both cache
inspection commands exited successfully. The header/mapping output showed
`dyld_v1   arm64`, iOS 16.7, 2,710 images, 42 subcaches, and the UUID above.

## Interpretation and limits

- The root filesystem and SystemOS Cryptex are separate donor volumes. A
  root-only file lookup is insufficient to classify an absolute install name
  as missing from the complete donor system.
- The cache image list reports image paths and source versions. It does not
  show which executable depends on which cached image, all re-exported
  dependencies, dlopen behavior, closure validity, code-signing state, or
  hardware service requirements.
- A framework's presence in the iPhone X cache does not establish that an
  equivalent iPhone9,1 provider exists or that the framework will work on
  T8010 hardware.
- No donor executable was run. No target firmware, device, partition, or
  activation/security state was changed.

## Next M6 evidence

The next host-side research should resolve the recursive load graph and
separate ordinary dylibs from cache-resident images, app-bundle frameworks,
embedded XPC services, and IOKit personality/provider requirements. Each
requirement must then be classified against iPhone9,1 evidence as
target-confirmed, donor-reference-only, missing, or unverified.

M6 remains in progress; M7 (SpringBoard on the target) has not started.
