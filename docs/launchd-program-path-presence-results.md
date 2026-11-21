# Actual LaunchDaemon Program path presence results

**Reviewed:** 2026-11-21  
**Source report:** `project-sweet-10.launchd-program-path-presence.v1`  
**Source report SHA-256:** `33dbb1e62ded690e0660c4fd76fd7b343e3155afa3ae3053475a17c105a202d9`

This note records the user-supplied read-only report for the nine selected
LaunchDaemons in the target reference inventory (19H422) and the iPhone X
donor reference inventory (20H392). The report does not record the exact scan
timestamp; the date above is the review date.

## Result

All nine selected `Program` paths were found as regular filesystem objects
in both datasets.

| Dataset | Supplied roots | Found | Matching root | Wrapper depth |
|---|---:|---:|---|---:|
| Target 19H422 | 1 | 9/9 | `target_root_0` | 1 (`root/`) |
| Donor 20H392 | 2 | 9/9 | `donor_root_0` | 2 (`root/root/`) |

All 9 target matches were at depth 1. All 9 donor matches were at depth 2 in
`donor_root_0`. None of the nine paths matched any checked prefix in
`donor_root_1`. This describes only the supplied roots and the tested
prefixes; it does not imply that other files or services are absent from that
second volume.

## Selected jobs

| LaunchDaemon label | `Program` |
|---|---|
| `com.apple.SpringBoard` | `/System/Library/CoreServices/SpringBoard.app/SpringBoard` |
| `com.apple.backboardd` | `/usr/libexec/backboardd` |
| `com.apple.bluetoothd` | `/usr/sbin/bluetoothd` |
| `com.apple.configd` | `/usr/libexec/configd` |
| `com.apple.mediaserverd` | `/usr/sbin/mediaserverd` |
| `com.apple.mobileactivationd` | `/usr/libexec/mobileactivationd` |
| `com.apple.notifyd` | `/usr/sbin/notifyd` |
| `com.apple.runningboardd` | `/usr/libexec/runningboardd` |
| `com.apple.wifid` | `/usr/sbin/wifid` |

The scan performed 81 bounded path checks: 27 for the single target root and
54 across the two donor roots. It checked wrapper depths 0, 1, and 2.

## Input provenance

| Dataset | Launchd inventory SHA-256 | Source plist SHA-256 |
|---|---|---|
| Target 19H422 | `539ae9992e6fb8395bf0354a2c3feb98cdae85933b40bb1a19a9a3e10c8270e3` | `34b6a174d2b948035afd71ad0a4fc2d3e4e85ea807a794ee69722054b09d6bbe` |
| Donor 20H392 | `86c9f900b2e3a02e78631a1bdc10929d493d13beb401183f4b289b93732f1d92` | `810070302b5c4d7c5f00bdc8df20aaea2dd33cd8342d2402fcdf7ff6397d374c` |

The compact machine-readable transcription is
[`research/launchd-program-path-presence-results.json`](../research/launchd-program-path-presence-results.json).
It retains the per-job paths, matched roots/depths, source hashes, and result
limits. Its `source_report_sha256` identifies the full supplied JSON report.

## Interpretation boundary

This establishes **path presence only**. The checker uses `lstat` component
by component, stops at symlinks, and does not follow symlink targets. It does
not open, hash, execute, or inspect any program file.

A regular-file result does **not** validate Mach-O format or architecture,
code signature, entitlements, ABI, linked dependencies, or loadability. It
also does not show that launchd registers the job, that a process starts, or
that it runs correctly. In particular, finding the SpringBoard executable
does not establish SpringBoard readiness or a successful iPhone 7 boot.

This is static host-side reference evidence only. No physical device, firmware,
partition, launch configuration, or boot state was accessed or changed.
