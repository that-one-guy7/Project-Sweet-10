# Project Sweet-10

**Target:** iPhone 7, `iPhone9,1` (A10 Fusion / T8010)  
**OS research target:** iOS 16-generation XNU and userland  
**Selected userland reference:** iPhone X iOS 16.7.16 (`20H392`)  
**First major milestone:** SpringBoard

> Research scaffold only. It contains no iOS firmware, proprietary binaries, boot payload,
> or working kernel. It is not ready to boot or flash.

## Current status
- [x] Target and project scope recorded
- [x] Initial feasibility and architecture notes
- [x] Candidate XNU 8796 source revision pinned for review
- [x] iOS 16.7.16 (20H392) userland reference recorded
- [x] XNU ARM64 source and configuration consumers inventoried
- [ ] Verify exact 20H392 kernel source revision
- [ ] Verify iPhone9,1 hardware/platform evidence
- [ ] Establish reproducible XNU source/toolchain baseline build
- [ ] Document A10 boot handoff requirements
- [ ] Host-side tests and diagnostics
- [ ] Display and input research
- [ ] Userland compatibility
- [ ] SpringBoard

## Reference projects
- [ios-sweet](https://github.com/dipa-studio/ios-sweet): useful iOS 16-era XNU,
  diagnostics, device-tree workflow, and userland research. Its target is Qualcomm
  SM7150; its platform-specific drivers and hardware values are not A10 code.
- [ios-sunstone](https://github.com/14sea/ios-sunstone): later-stage XNU 8796 plus
  iPhone X 20H392 userland reference, reporting SpringBoard on Qualcomm SM4375.
  Its build discipline and subsystem decomposition are useful; its hardware code is
  not portable to A10. See [the comparison](docs/ios-sunstone-comparison.md).
- [Project Sandcastle](https://github.com/corellium/projectsandcastle): useful
  boot-environment research, but its Linux-oriented loader is not automatically an XNU loader.

## Safety and preservation
1. Begin with source review, static analysis, and host-side tests.
2. Do not write partitions or replace boot components during initial milestones.
3. Preserve the stock operating system and a verified recovery path.
4. Keep serials, ECIDs, calibration data, backups, firmware, and proprietary iOS files out of Git.
5. Every later hardware experiment needs a documented rollback plan.

## Repository map
- `docs/` — feasibility, hardware audit, architecture, milestones
- `research/` — public references and experiment notes
- `xnu/`, `boot/`, `device-tree/`, `userland/` — research work areas
- `tools/` — read-only scaffold validation
- `tests/` — host-side checks

Start with `docs/feasibility.md` and `docs/hardware-audit.md`.
