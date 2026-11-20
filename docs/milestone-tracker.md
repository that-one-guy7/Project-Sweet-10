# Milestone tracker

| ID | Milestone | Exit criterion | Status |
|---|---|---|---|
| M0 | Repository scaffold | Initial docs and target metadata | Prepared |
| M1 | Hardware/source audit | Evidence-backed iPhone9,1 inventory | In progress: XNU source consumers mapped; target hardware evidence incomplete |
| M2 | XNU baseline | Exact revision and reproducible host build | Candidate XNU source pinned; exact 20H392 kernel revision and reproducible build not yet established |
| M3 | Boot contract | Reviewed A10 handoff specification | Not started |
| M4 | Early-kernel test | Deterministic diagnostics in safe test environment | Not started |
| M5 | Display/input research | Independent subsystem plans | Research inventory started; A10 implementation not started |
| M6 | Root/userland research | launchd dependencies documented | 20H392 reference selected; dependency analysis not started |
| M7 | SpringBoard | GUI starts and remains stable in controlled test | Long-term goal; not started |

## Reference-project progress

- Reviewed `ios-sweet` as the initial Qualcomm SM7150/XNU 8796 reference.
- Reviewed `ios-sunstone` revision
  `e0471191ddbfb17fde6674db41320bffa832a85b` as a later-stage XNU 8796 plus
  iPhone X 20H392 reference. It reports SpringBoard on Qualcomm SM4375 hardware.
- Reviewed `ios-qemu` as a virtualized iPhone X 20H392 userland reference. It reports
  SpringBoard on QEMU virtual hardware using a rebuilt XNU 8796-generation kernel.
- These projects are useful for source organization, patch discipline, build
  reproducibility, and userland dependency research. Their Qualcomm or QEMU-specific
  hardware implementations are not portable A10/T8010 code.

## Change log

- 2026-11-19: Initial documentation scaffold prepared for iPhone 7 `iPhone9,1`.
  No device changes performed.
- 2026-11-20: Pinned a candidate XNU source revision, selected the 20H392 userland
  reference, and mapped ARM64 source/configuration consumers. Exact kernel matching,
  target hardware evidence, and a reproducible baseline build remain open.
- 2026-11-20: Added the ios-sunstone cross-project comparison. Its SpringBoard result
  is an upstream report on SM4375 hardware, not evidence of A10 support.
- 2026-11-20: Added the ios-qemu reference study. Its reported 20H392 SpringBoard
  result is on a QEMU virtual board and does not establish iPhone9,1 support.
