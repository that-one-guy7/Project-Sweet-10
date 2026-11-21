# iPhone9,1 19H422 GUI-chain dependency cache cross-reference

## Scope and source

This report cross-references the direct Mach-O dependencies captured for
`backboardd`, `runningboardd`, and SpringBoard against the `dylibs`
image array from the target iPhone 7 / `iPhone9,1` / D10AP dyld cache
inventory.

The original host path recorded in the terminal capture was
`$HOME/19H422-dyld-images.json`; `wc -c` reported **132,175,259 bytes**.
The archived Library capture `log.txt` (799,576 bytes, SHA-256
`d2cb1fb9e75f1d2c477c1cb7c0561cd4ec2b220b19ba96d6828ee267a9a83f3b`)
contains the full minified `dylibs` array. The array was parsed and checked:
**2,407 records**, unique indexes 1–2,407, and 2,407 unique install names.

The extraction is limited to the exact `dylibs` array. It does not assert
anything about loader closures, filesystem presence, or runtime resolution.

## Result summary

| Executable | Regular direct dependencies | Exact image-list matches | Weak rows |
|---|---:|---:|---:|
| `backboardd` | 42 | 42 | 1 named |
| `runningboardd` | 6 | 6 | 0 |
| SpringBoard | 4 | 4 | 0 |

Across the three executables, there are **44 unique regular direct
dependency paths** and **all 44 appear in the target cache image list**.
There is one additional unique weak dependency path,
`/usr/appleinternal/lib/liblinkguard.dylib`, which does **not** appear
in the `dylibs` image array. That means only that it is not represented
there as a cached image record; it does not prove the file is absent from
the mounted filesystem or full iOS installation.

The key conclusion is that the three donor-only regular
`backboardd` direct-dependency edges identified in the Mach-O comparison
are all still represented as target cache images. A donor-only direct edge
is not the same thing as a target-cache-absent framework.

## Donor-only direct edges that are present in the target cache

| Donor-only direct edge | Target image-list index | Target cache version | Target UUID |
|---|---:|---:|---|
| `/System/Library/PrivateFrameworks/CarKit.framework/CarKit` | 130 | `462.4.0.0.0` | `2838C0E5-4D69-31A5-BD4A-E05C208D4A15` |
| `/System/Library/PrivateFrameworks/SystemWake.framework/SystemWake` | 2344 | `567.5.0.0.0` | `647E0318-0C3F-36A9-9225-8F297E54E27A` |
| `/System/Library/PrivateFrameworks/SoftLinking.framework/SoftLinking` | 1430 | `42.0.0.0.0` | `4CF5E13F-3FDB-3CA6-98D4-88AFD1E35B64` |

These paths are present in the target cache image inventory despite not
appearing in the target `backboardd` direct load-command list. This is a
distinction between a dependency edge from one executable and an image's
presence in the broader shared cache.

## Key GUI-chain image records

| Image | Target index | Target version | Target UUID |
|---|---:|---|---|
| BackBoardHIDEventFoundation | 588 | `478.19.0.0.0` | `A99AD801-5B39-347B-AAED-590362F01048` |
| BackBoardHIDEventProcessors | 934 | `478.19.0.0.0` | `8E09BC84-3783-33FF-9674-57ECB993FF76` |
| BackBoardServices | 19 | `478.19.0.0.0` | `35EE3FFB-EB35-38F4-ABFF-D695B8E3FB9F` |
| IOMobileFramebuffer | 309 | `255.6.1.1.0` | `F5FD666B-B216-3084-897D-BF00103F5F9D` |
| RunningBoard | 553 | `618.100.42.0.0` | `68246786-1E83-3892-907F-123EE1F09C68` |
| RunningBoardServices | 62 | `618.100.42.0.0` | `616B8ECB-90ED-38C5-9988-24AD07AE0CE9` |
| SpringBoard.framework | 454 | `4251.53.0.0.0` | `245B5F25-7DE1-329C-9107-87B37883CFB9` |
| Foundation | 12 | `1866.100.1.0.0` | `F9235FC7-EC4E-31C9-B56E-95CF10B07239` |
| CoreFoundation | 4 | `1866.100.1.0.0` | `EEC1287D-059B-38C8-9BC1-58A0C8B1E6C2` |

## Complete unique dependency-path cross-reference

The index, version, and UUID columns are taken directly from the target
`dylibs` image array. Repeated use of the same path by multiple executables
is collapsed into one row; the `Used by` column preserves all selected
consumers.

| Install name | Index | Cache version | UUID | Used by | Image-list status |
|---|---:|---|---|---|---|
| `/System/Library/Frameworks/AVFoundation.framework/AVFoundation` | 708 | `2091.1.1.0.0` | `C9045B58-4EAC-3C7B-A09C-18D6578E9815` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation` | 4 | `1866.100.1.0.0` | `EEC1287D-059B-38C8-9BC1-58A0C8B1E6C2` | backboardd (regular), runningboardd (regular) | image-list present |
| `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics` | 15 | `1557.7.1.0.0` | `C99C6784-000C-3D9A-B7EF-AF28A0F1A28A` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/CoreMotion.framework/CoreMotion` | 75 | `2667.4.3.1.0` | `341A23BD-CCAD-3C1F-9008-42164FE124ED` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/CoreServices.framework/CoreServices` | 5 | `1165.83.0.0.0` | `F0ACFB7C-6C39-36D7-BB9B-D0ADF76C845E` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/CoreText.framework/CoreText` | 28 | `710.5.0.2.0` | `33AA63BC-E745-3CF9-8CBB-195E696233E1` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/Foundation.framework/Foundation` | 12 | `1866.100.1.0.0` | `F9235FC7-EC4E-31C9-B56E-95CF10B07239` | backboardd (regular), runningboardd (regular), SpringBoard (regular) | image-list present |
| `/System/Library/Frameworks/ImageIO.framework/ImageIO` | 13 | `2222.15.2.0.0` | `786D7A4C-4D39-38C5-BCD7-2E7AC08B623E` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit` | 71 | `1955.140.2.0.0` | `4AA27953-BAC7-3BCC-A036-2E0CA754907F` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/IOSurface.framework/IOSurface` | 369 | `302.15.0.0.0` | `12A86B9F-A356-3C17-831A-37F2B4B533AC` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/Metal.framework/Metal` | 193 | `261.13.4.0.0` | `E33EAE79-59DE-37E8-BA20-03A5BF3CC7AC` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/QuartzCore.framework/QuartzCore` | 18 | `964.34.0.0.0` | `BFB37348-30C8-3723-84E1-7B04ACACC5BE` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/Security.framework/Security` | 45 | `60158.141.1.700.8` | `A2299834-68B3-3E3F-99F9-FEC44C972386` | backboardd (regular) | image-list present |
| `/System/Library/Frameworks/SystemConfiguration.framework/SystemConfiguration` | 7 | `1163.140.3.0.0` | `324E7521-8781-343C-8A43-DEAB68EEACF1` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/AggregateDictionary.framework/AggregateDictionary` | 879 | `427.1.0.0.0` | `CCA0340F-83B0-3D3F-A76C-6E15290E4B7C` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation` | 588 | `478.19.0.0.0` | `A99AD801-5B39-347B-AAED-590362F01048` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/BackBoardHIDEventProcessors.framework/BackBoardHIDEventProcessors` | 934 | `478.19.0.0.0` | `8E09BC84-3783-33FF-9674-57ECB993FF76` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices` | 19 | `478.19.0.0.0` | `35EE3FFB-EB35-38F4-ABFF-D695B8E3FB9F` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard` | 31 | `567.5.0.0.0` | `54602700-3B41-3EAA-9EE2-88F025D09D5F` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/BiometricKit.framework/BiometricKit` | 357 | `300.120.3.0.0` | `E1F2B63C-379E-343A-ABCD-C258E82089F5` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/BoardServices.framework/BoardServices` | 222 | `567.5.0.0.0` | `15893FEF-16F8-30CD-A674-CFB3CB055D11` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/ButtonResolver.framework/ButtonResolver` | 957 | `36.0.0.0.0` | `A5F64E5C-F383-32B6-86D5-38EB2B225426` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/CoreAccessories.framework/CoreAccessories` | 343 | `672.140.4.0.0` | `7C035F3B-B050-3B16-99B8-1E75BBEFA7DF` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics` | 262 | `155.140.4.0.0` | `742D05D9-7082-307B-A1AE-8D72120856CA` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/CoreBrightness.framework/CoreBrightness` | 1013 | `1212.120.4.0.0` | `9ED042E4-63A7-3CBC-8FEE-42E207BE2B35` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/CrashReporterSupport.framework/CrashReporterSupport` | 171 | `14264.0.0.0.0` | `0F3972AA-D6CD-300A-91F7-C86489294ACC` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/DataMigration.framework/DataMigration` | 72 | `2141.0.0.0.0` | `971E8C97-07E1-3D64-A269-6E53395C4CEF` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/GraphicsServices.framework/GraphicsServices` | 208 | `5006.0.0.0.0` | `BB434D86-0991-365F-BED3-C3923CF3073C` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/HangTracer.framework/HangTracer` | 644 | `184.3.0.0.0` | `9D8745ED-498F-3BDB-B94E-EABE422F6F80` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/Haptics.framework/Haptics` | 525 | `29.0.0.0.0` | `84EF8A51-856C-32BD-B9C2-67B5C0F08763` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer` | 309 | `255.6.1.1.0` | `F5FD666B-B216-3084-897D-BF00103F5F9D` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/ProgressUI.framework/ProgressUI` | 1326 | `2141.0.0.0.0` | `2C60BFFD-98FD-30BA-BAB0-D65B9AF55E62` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard` | 553 | `618.100.42.0.0` | `68246786-1E83-3892-907F-123EE1F09C68` | runningboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices` | 62 | `618.100.42.0.0` | `616B8ECB-90ED-38C5-9988-24AD07AE0CE9` | backboardd (regular), runningboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard` | 454 | `4251.53.0.0.0` | `245B5F25-7DE1-329C-9107-87B37883CFB9` | SpringBoard (regular) | image-list present |
| `/System/Library/PrivateFrameworks/StudyLog.framework/StudyLog` | 532 | `35.0.0.0.0` | `55042E6B-DD94-35D8-89AA-BF33D4080D3A` | backboardd (regular) | image-list present |
| `/System/Library/PrivateFrameworks/WatchdogClient.framework/WatchdogClient` | 1522 | `127.140.2.0.0` | `3B22A5D3-6AF7-3D07-9562-6305FF7D0FBB` | backboardd (regular) | image-list present |
| `/usr/appleinternal/lib/liblinkguard.dylib` | — | — | — | backboardd (weak) | not in image list |
| `/usr/lib/libAccessibility.dylib` | 17 | `2933.45.3.0.0` | `4C8AF83E-24C3-3F01-A25A-991110625BC1` | backboardd (regular) | image-list present |
| `/usr/lib/libc++.1.dylib` | 150 | `1300.36.0.0.0` | `16BE14F2-A677-3DF1-984D-BBAB893EE3B9` | backboardd (regular) | image-list present |
| `/usr/lib/liblockdown.dylib` | 1694 | `1188.120.4.0.0` | `87DBB112-22B2-3118-881A-FB477A58FA16` | backboardd (regular) | image-list present |
| `/usr/lib/libMobileGestalt.dylib` | 88 | `1073.100.31.0.1` | `71F82BAC-04CB-35C9-937B-7AC9989A0101` | backboardd (regular) | image-list present |
| `/usr/lib/libobjc.A.dylib` | 148 | `841.13.0.0.0` | `F1B36686-ED48-35EF-8896-0CEA8E9DA1C0` | backboardd (regular), runningboardd (regular), SpringBoard (regular) | image-list present |
| `/usr/lib/libsp.dylib` | 1717 | `61.0.0.0.0` | `E4E34F5F-4290-33B2-AE53-94EB26E6C25D` | backboardd (regular) | image-list present |
| `/usr/lib/libSystem.B.dylib` | 658 | `1311.120.1.0.0` | `EFE3ECA7-89AB-3B10-ADE7-C8527E93ED56` | backboardd (regular), runningboardd (regular), SpringBoard (regular) | image-list present |

The complete machine-readable data is in
[`research/iphone91-19h422-gui-dependency-cache-crossref.json`](../research/iphone91-19h422-gui-dependency-cache-crossref.json).

## Interpretation and next evidence

This closes the bounded image-list cross-reference for the three selected
executables: every regular direct install name is represented in the target
cache inventory. It does **not** prove that dyld resolves each path for a
specific executable, that the corresponding code is valid or compatible,
or that the image loads at runtime.

The next static investigation should expand target PrebuiltLoaderSet records
for the three higher-level frameworks directly named by the GUI-chain
executables:

- `/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard`
- `/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard`
- `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices`

Those loader records can show each framework's own direct dependency rows.
Keep their edges separate from the executable's direct load commands and
from cache image-list membership. The SpringBoard executable's
`@executable_path/Frameworks` rpath also remains a separate app-bundle
path question.

## Evidence boundary

The image-list membership check is host-side static metadata only. It does
not validate file signatures, entitlements, ABI, linked dependencies,
loader resolution, filesystem availability, launchd registration, process
launch, IOKit provider attachment, hardware operation, kernel compatibility,
or SpringBoard readiness. The target reference is stock iOS 15.8.8
(19H422), not the intended iOS 16 userland. The physical iPhone 7 remains
on iOS 12.1.4; no device or boot state was accessed or changed.
