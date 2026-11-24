# Repository artifact hygiene: extracted AppleT8010PMGR segments

## Finding

The current `main` tree at commit `9a0b9db95ce1266eb988acd6d0aa899821412a26` contained two extracted code artifacts from the iPhone9,1 / D10AP / iOS 15.8.8 (19H422) target-reference KernelCache. They were tracked despite the repository's existing `.gitignore` rule `*.bin`.

The repository-wide Git tree was not truncated (228 blobs). Among files with binary-artifact extensions, the two `.bin` files below were the only extracted binary candidates. The tracked `BuildManifest.plist` was inspected separately and begins with an XML declaration; it is text metadata, not a firmware image or executable.

## Exact tracked artifacts

| Path on prior `main` | Size | Git blob SHA-1 | Content SHA-256 |
|---|---:|---|---|
| `AppleT8010PMGR.prelink-text.bin` | 4,603 bytes | `c98814f224c08fdbaa5a7424ca1d5b942f587233` | `c903d96cb70e04cd7f8d48a096800af2853504e480e23e9bd87a1faef3303221` |
| `AppleT8010PMGR.text-exec.bin` | 14,984 bytes | `da503e8243697bd8623381a86a442a3cfc7f5de6` | `cfeb027ea005be174cac8c8c233b93b504fa2683fdfc9fb9706358e680940764` |

Both artifacts originate from the target-reference KernelCache whose recorded SHA-256 is:

`7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`

The prelink-text artifact is the extracted 4,603-byte ARM64 `MH_KEXT_BUNDLE` header. The executable segment corresponds to the mapped `__TEXT_EXEC` range `0xfffffff0068ac000–0xfffffff0068afa87`, outer KernelCache offsets `0x1f38000–0x1f3ba87`, size 14,984 bytes. The address mapping and segment boundaries are documented in [the target PMGR audit](iphone91-19h422-applet8010pmgr-binary-audit.md).

## Preserve the provenance distinction

PR #169 records a separate host-side 14,984-byte dump with SHA-256:

`95cb5769c9425c0a6755de602f1e0872959b7fa910da642aa791c5e5f3fc5e52`

That digest differs from the tracked executable segment's `cfeb...` digest even though the sizes match. [PR #170's provenance note](https://github.com/that-one-guy7/Project-Sweet-10/pull/170) records this discrepancy. This cleanup does not choose which dump is correct, overwrite one with the other, or erase either identity. It removes the extracted code from the public working tree while preserving hashes, sizes, source identity, and mapping metadata in text documentation.

## Current-tree cleanup and history limitation

This change removes both tracked `.bin` paths from the current repository tree. The existing `.gitignore` rule already prevents newly untracked `.bin` files from being added by ordinary Git workflows, but ignore rules do not automatically untrack files that were already committed.

**This is not a history rewrite.** The original blobs remain reachable through earlier commits and may remain in existing clones, forks, caches, or downloaded archives. No claim is made that historical copies have been purged. The purpose is to stop carrying the extracted Apple code in the current branch and retain only the minimum text evidence needed for the static audit.

Future host-side extraction artifacts should remain outside the repository. Commit only hashes, source identities, offsets, parser outputs that contain no extracted code, and concise review notes. Do not add raw KernelCache segments, KEXT executables, firmware images, device dumps, or signing material.

## Scope

This is repository hygiene only. No binary was executed, no device or firmware state was accessed, and no build or runtime behavior is claimed. The physical iPhone 7 remains on iOS 12.1.4.
