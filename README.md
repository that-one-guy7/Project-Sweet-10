# Project Sweet-10

**Target:** iPhone 7, `iPhone9,1` (A10 Fusion / T8010)  
**OS research target:** iOS 16-generation XNU and userland  
**First major milestone:** SpringBoard

> Research scaffold only. It contains no iOS firmware, proprietary binaries, boot payload,
> or working kernel. It is not ready to boot or flash.

## Current status
- [x] Target and project scope recorded
- [x] Initial feasibility and architecture notes
- [ ] Verify hardware and software baseline
- [ ] Establish reproducible XNU source/toolchain baseline
- [ ] Document A10 boot handoff requirements
- [ ] Host-side tests and diagnostics
- [ ] Display and input research
- [ ] Userland compatibility
- [ ] SpringBoard

## Reference projects
- [ios-sweet](https://github.com/dipa-studio/ios-sweet): useful iOS 16-era XNU,
  diagnostics, device-tree workflow, and userland research. Its target is Qualcomm
  SM7150; its platform-specific drivers and hardware values are not A10 code.
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
