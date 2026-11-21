# Linux IPSW filesystem-DMG mount fallback diagnostic

## Purpose

This note records a source-level explanation of the Linux filesystem-image extraction error encountered while inspecting the iPhone9,1 / D10AP / iOS 15.8.8 (19H422) IPSW. It narrows what the reported HFS+ error means without guessing why the earlier APFS-FUSE attempt failed.

This is host-side analysis only. The physical iPhone remains on iOS 12.1.4. No device, firmware, partition, activation, or boot state is accessed or changed.

## User-side environment and observed result

The user reported:

- IPSW: `$HOME/Downloads/iPhone_4.7_P3_15.8.8_19H422_Restore.ipsw` (shown as 5.1 GiB by `ls -lh`).
- `ipsw`: 3.1.749, build commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`.
- APFS-FUSE executable is discoverable at `/usr/local/bin/apfs-fuse`.
- `ipsw extract --files --device iPhone9,1` selected filesystem DMG `098-68844-067.dmg` and reached the mount stage.
- The final error was `no HFS+ partition found in DMG`, followed by EOF errors while probing MBR, Primary GPT Header, and Backup GPT Header.

The user supplied verbose output from the Snap-packaged command. The host path `/usr/local/bin/apfs-fuse` existed and was executable, but Snap's `ipsw` reported that the configured path did not exist from within its execution environment. The Snap connection listing showed `home` connected and `fuse-support` disconnected. The exact confinement mechanism was not independently diagnosed.

## Pinned ipsw 3.1.749 source path

The following behavior was verified at commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`:

1. `internal/commands/extract/extract.go` selects and extracts the filesystem DMG, then calls `utils.MountDMG`. If mounting fails, the caller wraps the returned error as `failed to IPSW FS dmg`.
2. `internal/utils/macos.go` implements Linux filesystem detection in `mountLinux`.
3. `internal/magic/magic.go` checks for the APFS `NXSB` signature at offset `0x20` and HFS+/HFSX signatures at offset `1024`.
4. If both filesystem probes return false, `mountLinux` takes an explicit fallback path: try APFS-FUSE first; if that fails, log the APFS-FUSE error at debug level and try the HFS+ handler.
5. `mountWithAPFSFuse` calls the discovered APFS-FUSE executable with the image path and mount point. The APFS-FUSE error is included in the debug log from the fallback branch; the outer command can otherwise expose only the later HFS+ fallback failure.

Relevant pinned source files:

- [ipsw 3.1.749: filesystem extraction caller](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/internal/commands/extract/extract.go)
- [ipsw 3.1.749: Linux mount selection and APFS-FUSE invocation](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/internal/utils/macos.go)
- [ipsw 3.1.749: filesystem magic probes](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/internal/magic/magic.go)
- [ipsw 3.1.749: HFS+ fallback parser](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/internal/utils/hfsplus.go)

## Correct interpretation of the reported HFS+ message

The HFS+ message is **not evidence that the iPhone 7 filesystem DMG is HFS+**, nor does it independently prove that the IPSW is corrupt.

Given the pinned code path, the MBR/GPT EOF diagnostics are consistent with the ambiguous-filesystem fallback: APFS-FUSE was attempted first and failed, after which the HFS+ parser attempted to find an HFS+ partition and returned its own error. The user-visible final error can therefore hide the first failure.

This narrows the problem to the APFS-FUSE attempt or the image/type detection path, but does not identify the cause. Possible causes must not be asserted until the debug output and extracted image metadata are available.

## Successful standalone extraction

The user downloaded and extracted the standalone Linux archive for ipsw
`3.1.749`, then retried the same 19H422 filesystem extraction using that
binary and the explicit APFS-FUSE path. The verbose output reported:

- The same IPSW and filesystem DMG `098-68844-067.dmg` were selected.
- The DMG mounted after the filesystem-type detection selected the APFS-FUSE
  attempt.
- The nested
  `AppleMultitouchSPI.kext/PlugIns/MultitouchHID.plugin/Info.plist` was
  extracted successfully.
- A broader driver-name query also extracted the plugin's
  `_CodeSignature/CodeResources`.

The later inspection of the extracted `Info.plist` confirmed bundle ID
`com.apple.iokit.plugin.MultitouchHID`, version `5100.27`, supported platform
`iPhoneOS`, minimum OS `15.8`, and the plugin type/factory UUID mappings.
The extracted parent KEXT plist files were not returned by the broad search;
the parent-driver metadata in the project report is sourced from the separate
KernelCache JSON output.

The standalone result proves the filesystem DMG can be mounted and selected
metadata extracted in this host environment. It does not establish exactly
which Snap sandbox restriction caused the earlier non-existent-file result.

## APFS-FUSE capability boundary

The APFS-FUSE project describes itself as a read-only APFS FUSE driver and documents direct DMG support. Its README also lists compression limitations, including lack of transparent LZFSE decompression. That is a capability caveat, not proof that this specific 19H422 image uses an unsupported format or that compression caused the failure.

The executable's path is known, but its installed build/version and the exact APFS-FUSE error are not yet known.

Reference: [APFS-FUSE README at the reviewed source revision](https://github.com/sgan81/apfs-fuse/blob/66b86bd525e8cb90f9012543be89b1f092b75cf3/README.md).

## Status

**Resolved for this inspection:** the standalone ipsw 3.1.749 binary mounted
the 19H422 filesystem DMG and extracted the nested multitouch plugin metadata.

**Still unknown:** the exact reason the Snap-packaged binary could not see the
host APFS-FUSE executable, the installed APFS-FUSE build/version, and the
plugin executable's contents or runtime loading. The repository contains no
filesystem image or proprietary executable. This remains host-side static
research only; the physical iPhone remains on iOS 12.1.4. M6 continues, and
M7 has not started.
