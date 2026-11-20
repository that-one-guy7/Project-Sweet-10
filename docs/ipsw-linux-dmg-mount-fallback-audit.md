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

The user has not yet supplied the verbose/debug output from a retry with the global `-V` flag. The precise APFS-FUSE failure is therefore unknown.

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

## APFS-FUSE capability boundary

The APFS-FUSE project describes itself as a read-only APFS FUSE driver and documents direct DMG support. Its README also lists compression limitations, including lack of transparent LZFSE decompression. That is a capability caveat, not proof that this specific 19H422 image uses an unsupported format or that compression caused the failure.

The executable's path is known, but its installed build/version and the exact APFS-FUSE error are not yet known.

Reference: [APFS-FUSE README at the reviewed source revision](https://github.com/sgan81/apfs-fuse/blob/66b86bd525e8cb90f9012543be89b1f092b75cf3/README.md).

## Next bounded evidence

The next useful item is the full output from the already prepared host-side retry:

- Run the same IPSW extraction command with the global verbose flag `-V`.
- Preserve the complete output, especially the debug line containing `apfs-fuse failed` and the command's own output.
- Do not publish the complete filesystem image, raw DeviceTree, or private machine-specific files.

Only after that log is available should a specific APFS-FUSE, image-format, or extraction issue be proposed. No phone-side action is required.

## Status

**Source audit complete:** the pinned `ipsw` fallback behavior and the meaning of the outer HFS+ error are documented.

**Root cause pending:** the APFS-FUSE error from the user's actual image has not been captured. The nested `MultitouchHID.plugin/Info.plist` check remains pending until the matching 19H422 filesystem can be inspected. M6 remains in progress; M7 has not started.
