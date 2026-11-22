# AppleT8010PMGR executable-dump provenance reconciliation

## Purpose

This note reconciles two same-sized artifacts that are currently described as
the iPhone9,1 / D10AP / iOS 15.8.8 (19H422) AppleT8010PMGR executable segment.
The comparison is strictly byte-identity and repository-provenance work. It
does not interpret instructions, assign method semantics, or establish any
runtime behavior.

The physical iPhone 7 remains on iOS 12.1.4. No device, firmware, partition,
security, or boot state was accessed or changed.

## Artifacts compared

### Existing repository file on main

At base commit
`9a0b9db95ce1266eb988acd6d0aa899821412a26`, the repository contains:

| Field | Value |
|---|---|
| Path | `AppleT8010PMGR.text-exec.bin` |
| Size | 14,984 bytes |
| Git blob SHA-1 | `da503e8243697bd8623381a86a442a3cfc7f5de6` |
| Independently computed content SHA-256 | `cfeb027ea005be174cac8c8c233b93b504fa2683fdfc9fb9706358e680940764` |

The content was retrieved through the GitHub file API as base64 and decoded
locally in the analysis environment. The decoded bytes reproduce the GitHub
blob identifier when hashing the Git object header
`blob 14984\\0` followed by the file bytes. This cross-check confirms that
the SHA-256 was calculated over the exact repository blob content rather than
a truncated or text-transformed representation.

### Dump described by PR #169

PR #169 records a separate host-side dump with:

| Field | Value |
|---|---|
| Reported size | 14,984 bytes |
| Reported SHA-256 | `95cb5769c9425c0a6755de602f1e0872959b7fa910da642aa791c5e5f3fc5e52` |
| Recorded source VM range | `0xfffffff0068ac000–0xfffffff0068afa87` |
| Recorded outer KernelCache range | `0x1f38000–0x1f3ba87` |

PR #169's patch records the digest and the first 180 lines of user-supplied
AArch64 disassembly, but does not add or replace the binary artifact. The
repository file above therefore remains unchanged on the PR's base branch.

## Verified result

The two reported SHA-256 values differ:

- Repository blob: `cfeb027ea005be174cac8c8c233b93b504fa2683fdfc9fb9706358e680940764`
- PR #169 local dump: `95cb5769c9425c0a6755de602f1e0872959b7fa910da642aa791c5e5f3fc5e52`

Both are reported as 14,984 bytes. Equal length is not byte identity. The
committed repository file must not be treated as a byte-for-byte copy of the
dump whose disassembly is recorded in PR #169.

As a hash-procedure cross-check, the other committed artifact
`AppleT8010PMGR.prelink-text.bin` is 4,603 bytes and hashes to
`c903d96cb70e04cd7f8d48a096800af2853504e480e23e9bd87a1faef3303221`,
matching the digest already recorded in the target PMGR audit. Its Git blob
identifier also matches the repository tree entry.

## Interpretation and limits

The mismatch establishes an artifact-provenance gap; it does **not** establish
which artifact is incorrect. Plausible explanations include an older
repository extraction, a different host-side extraction input, or an
incorrectly transcribed digest. The available evidence does not distinguish
among them.

Until the discrepancy is reconciled:

1. Do not use the committed `AppleT8010PMGR.text-exec.bin` as a substitute
   for the local dump described in PR #169.
2. Do not claim that the PR #169 disassembly is reproducible from the current
   repository binary.
3. Preserve both identities as separate records; do not silently overwrite,
   rename, or delete the existing artifact.
4. Resolve the gap with a read-only host-side comparison against the
   hash-identified 19H422 KernelCache and its already documented
   virtual-address-to-outer-file mapping. Record the resulting input hash,
   extracted byte count, and output hash together.

This does not invalidate the user's local disassembly if its source file and
hash are correct. It only means that the exact bytes used for that disassembly
are not currently represented by the same-named repository file.

## References

- [PR #169 — Record AppleT8010PMGR executable disassembly](https://github.com/that-one-guy7/Project-Sweet-10/pull/169)
- [Target AppleT8010PMGR binary audit](iphone91-19h422-applet8010pmgr-binary-audit.md)
- [EnableCPUCore contract cross-check](iphone91-19h422-enablecpu-core-contract-crosscheck.md)
- [Target KernelCache identity and segment mapping](iphone91-19h422-applet8010pmgr-binary-audit.md)

This is repository artifact-integrity documentation only. It does not establish
an ApplePMGR callback, an `IOPMGR::enableCPUCore` implementation, secondary
CPU release, runtime driver attachment, iOS 16 compatibility, boot, or
SpringBoard.
