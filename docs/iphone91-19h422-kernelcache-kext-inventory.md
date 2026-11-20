# iPhone9,1 19H422 KernelCache KEXT inventory

## Purpose and evidence boundary

This is the next bounded, read-only M6 task: identify the kernel build and enumerate the KEXT bundle identifiers in the already extracted iPhone 7 target KernelCache. The KernelCache is a target-native iPhone9,1 artifact; it is not the iPhone X 20H392 donor kernel.

The physical iPhone remains on iOS 12.1.4. The file described here was extracted from a separately downloaded iPhone9,1 iOS 15.8.8 (19H422) IPSW for host-side analysis only. Do not treat this IPSW as installed on the phone or as proof that 20H392 can run on iPhone9,1.

## Artifact reported by the user

| Field | Observation |
|---|---|
| IPSW | iPhone 7 iOS 15.8.8, build 19H422 |
| Target product | iPhone9,1 |
| Extracted file | `kernelcache.release.iPhone9,1_3` |
| Relative host path | `19H422-kernel-inspect/19H422__iPhone9,1_3/kernelcache.release.iPhone9,1_3` |
| Reported size | 44,924,928 bytes |
| SHA-256 | Not yet recorded |
| Kernel/Darwin version | Not yet inspected |
| KEXT count and bundle IDs | Not yet inspected |
| IOKit personality metadata | Not yet inspected |

The absolute home-directory path is intentionally omitted from this public repository note. The filename and size are user-reported; they do not replace an independently recorded hash and parser output.

## Host-side read-only inventory

The following commands inspect the extracted file on the analysis computer. They do not communicate with the iPhone.

```sh
KC="$HOME/19H422-kernel-inspect/19H422__iPhone9,1_3/kernelcache.release.iPhone9,1_3"
REPORT="$HOME/19H422-kernel-inspect/report"

mkdir -p "$REPORT"

test -f "$KC" || {
  printf 'KernelCache not found: %s\n' "$KC" >&2
  exit 1
}

stat -c 'bytes=%s path=%n' "$KC" | tee "$REPORT/artifact.txt"
sha256sum "$KC" | tee "$REPORT/kernelcache.sha256"
ipsw version | tee "$REPORT/ipsw-version.txt"
ipsw kernel version "$KC" 2>&1 | tee "$REPORT/kernel-version.txt"
ipsw kernel kexts "$KC" 2>&1 | tee "$REPORT/kext-list.txt"
```

The `ipsw kernel version` and `ipsw kernel kexts` subcommands are documented by the ipsw project. Check the installed command's `--help` output if the local 3.1.749 build uses different flags. Keep the complete KEXT list; do not rely only on a keyword-filtered excerpt.

## Follow-up review

After the metadata output is recorded:

1. Confirm the reported file size and record the SHA-256.
2. Record the Darwin/XNU version exactly as printed by ipsw.
3. Record the total KEXT count and the complete ordered bundle-ID/version list.
4. Identify candidate bundles for display/framebuffer, touch/HID, SPI, and backlight by their metadata—not by guessing from DeviceTree node names.
5. Inspect only candidate KEXT metadata needed to establish whether an IOKit personality advertises matching properties relevant to the already documented 19H422 DeviceTree nodes.
6. Keep bundle presence, personality presence, match-property overlap, and a proven provider relationship as separate evidence levels.

Do not commit the KernelCache, extracted KEXT binaries, raw DeviceTree, device identifiers, or personal host paths. Commit only sanitized bundle IDs, version strings, hashes, relevant personality key/value names, and carefully qualified conclusions.

## Current status

**Artifact staged on host; metadata inventory pending.** The user has reported the extracted file path and byte size, but no SHA-256, kernel-version output, KEXT list, or personality results have yet been supplied.

M6 remains in progress. Target KEXT/provider matching and 20H392 userland service compatibility are not established. M7 (SpringBoard on iPhone9,1) has not started.

## References

- [ipsw kernelcache and KEXT analysis guide](https://github.com/blacktop/ipsw-skill/blob/main/ipsw/references/kernel.md)
- [ipsw kernel parsing guide](https://blacktop.github.io/ipsw/docs/guides/kernel/)
- [ipsw kernel extract command reference](https://blacktop.github.io/ipsw/docs/cli/ipsw/kernel/extract/)
