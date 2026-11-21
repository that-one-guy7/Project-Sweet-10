# H9/T8010 full-tree source consumer audit

## Purpose and status

This document extends the earlier hand-reviewed
[H9 feature-macro consumer audit](h9-feature-macro-consumer-audit.md).
The historical T8010 profile is not a self-contained header that can be copied
into XNU 8796: its macros select or alter code in other parts of the kernel.

The historical header defines **12 feature macros**, excluding its include
guard:

- \`APPLEHURRICANE\`
- \`NO_MONITOR\`
- \`HAS_MIGSTS\`
- \`HAS_KTRR\`
- \`HAS_CPMU_L2C_EVENTS\`
- \`CORE_NCTRS\`
- \`CPMU_AIC_PMI\`
- \`__ARM_16K_PG__\`
- \`__ARM_KERNEL_PROTECT__\`
- \`__ARM_GLOBAL_SLEEP_BIT__\`
- \`__ARM_PAN_AVAILABLE__\`
- \`SINGLE_STEP_RETIRE_ERRATA\`

The H9 header directly includes \`pexpert/arm64/apple_arm64_common.h\`.
The historical \`board_config.h\` includes H9 under
\`#ifdef ARM64_BOARD_CONFIG_T8010\`, then sets \`MAX_CPUS=3\`,
\`MAX_CPU_CLUSTERS=1\`, and \`MAX_L2_CLINE=7\` for that board block.
These values are historical configuration facts, not approved Sweet-10
constants. The static 19H422 DeviceTree has two CPU nodes (one marked
\`running\`, one \`waiting\`); that alone does not establish the final online
CPU count or reconcile the historical board maximum.

Sources:
- [XNU 7195.121.3 H9.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)
- [XNU 7195.121.3 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/board_config.h)
- [XNU 8796.141.3 H13.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/H13.h)
- [Pinned public XNU 12377.1.9 commit](https://github.com/apple-oss-distributions/xnu/commit/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea)

## What the existing reviewed-file comparison establishes

The earlier audit examined selected matching ARM64, exception, VM, PMU,
and platform-expert files. Its bounded findings remain:

| H9 macro | Existing reviewed-file result | Porting interpretation |
|---|---|---|
| \`APPLEHURRICANE\` | CPU-name, register/cache-line, and PMU paths remain in parts of newer source; the old startup HID5 workaround is absent from the corresponding reviewed \`start.s\` | A retained CPU-family conditional does not recreate the T8010 board profile |
| \`NO_MONITOR\` | Generic EL3-related checks remain; H13 also defines this macro | Do not confuse this with the separate \`XNU_MONITOR\` secure-pmap build option |
| \`HAS_MIGSTS\` | The old exception/status-reporting branch is absent from the corresponding reviewed 8796 \`sleh.c\` | Replacement or removal rationale remains unknown |
| \`HAS_KTRR\` | Generic common-header support remains, while H13 defines \`HAS_CTRR\` | KTRR and CTRR are distinct hardware integrity mechanisms |
| \`HAS_CPMU_L2C_EVENTS\` | No direct consumer was found in the earlier selected-file review | Unresolved; absence from selected files is not proof of global non-use |
| \`CORE_NCTRS\` | Used by common KPC/PMU code; H13 also sets 10 | Same count does not prove matching T8010 PMU semantics or interrupt wiring |
| \`CPMU_AIC_PMI\` | Conditional logic remains in generic PMU/interrupt code; H13 does not declare it | The required A10 value and wiring are unverified |
| \`__ARM_16K_PG__\` | Generic page-size paths remain; H13 also defines it | Shared VM support is not a complete board or memory layout |
| \`__ARM_KERNEL_PROTECT__\` | Many guarded paths remain in newer source; H13 does not declare it | Build selection and A10 applicability remain unresolved |
| \`__ARM_GLOBAL_SLEEP_BIT__\` | Generic sleep coordination remains; H13 also defines it | No A10 power-state behavior is established by this alone |
| \`__ARM_PAN_AVAILABLE__\` | Generic PAN-related paths remain; H13 also defines it | Architectural feature use still needs target evidence |
| \`SINGLE_STEP_RETIRE_ERRATA\` | The corresponding reviewed 8796 \`pcb.c\` path is absent; H13 does not define it | The old workaround's disposition is unknown |

## Newer public-source indexed cross-check

The default branch of Apple's public XNU repository is currently pinned at
commit \`f6217f891ac0bb64f3d375211650a4c1ff8ca1ea\`
(\`xnu-12377.1.9\`). A GitHub code-search cross-check at that exact public
snapshot returned the following indexed paths:

| H9 macro | Indexed result count | Returned consumer paths / note |
|---|---:|---|
| \`APPLEHURRICANE\` | 3 | \`osfmk/arm64/sleh.c\`, \`proc_reg.h\`, \`monotonic_arm64.c\` |
| \`NO_MONITOR\` | 10 | H13/H14/H15/H16, VMAPPLE, \`cpu.c\`, \`kpc.c\`, pmap paths |
| \`HAS_MIGSTS\` | 0 | No indexed result |
| \`HAS_KTRR\` | 1 | \`pexpert/pexpert/arm64/apple_arm64_common.h\` |
| \`HAS_CPMU_L2C_EVENTS\` | 0 | No indexed result |
| \`CORE_NCTRS\` | 7 | H13/H14/H15/H16, \`machine_kpc.h\`, \`monotonic_arm64.c\`, \`board_config.h\` |
| \`CPMU_AIC_PMI\` | 3 | \`monotonic.h\`, \`monotonic_arm64.c\`, \`machine_routines.c\` |
| \`__ARM_16K_PG__\` | 12 | Generic TLB, VM, pmap, and ARM64 profile files |
| \`__ARM_KERNEL_PROTECT__\` | 19 | Generic TLB, CPU, VM, task, pmap, and assembly files |
| \`__ARM_GLOBAL_SLEEP_BIT__\` | 8 | H13/H14/H15/H16 and CPU/sleep implementation files |
| \`__ARM_PAN_AVAILABLE__\` | 13 | Generic copyio, ARM init, PCB, register, and test files |
| \`SINGLE_STEP_RETIRE_ERRATA\` | 0 | No indexed result |

These are search-index observations, **not** a full-tree proof of absence:
the returned results reflect GitHub's indexed code search, not compiler
preprocessing. The new pinned full-tree workflow below performs a separate
textual scan of all selected source/build files in both XNU checkouts and
uploads a machine-readable report.

The important pattern is already clear: several generic CPU/VM/PMU consumers
survive long after the historical H9 board profile disappears. Their presence
cannot be used as evidence that T8010 is a supported machine configuration.
Likewise, a zero-result search does not prove a feature is unused, unsupported,
or removed from every private/generated build input.

## Reproducible full-tree scan

The new read-only scanner is \`tools/audit_h9_source_closure.py\`. It:

1. Reads the 12 object-like feature definitions from historical \`H9.h\`.
2. Searches candidate source/build files in the complete 7195 and 8796
   checkouts for identifier-token occurrences, recording file, line, and
   coarse context classification.
3. Compares the matching names with definitions in the candidate \`H13.h\`;
   it never substitutes H13 values for H9 values.
4. Walks locally resolvable includes reachable from historical \`H9.h\`,
   retaining unresolved include names.
5. Emits a JSON report with per-macro references, path sets, include edges,
   and explicit limitations.

Synthetic tests are in \`tests/test_audit_h9_source_closure.py\`. The workflow
\`.github/workflows/h9-source-closure.yml\` checks out the two exact commits
from the repository lock files, runs the host-side test suite, runs the
scanner, and uploads \`h9-source-closure.json\` as a workflow artifact.

The scanner is deliberately a textual inventory, not a C preprocessor or
linker dependency graph. It does not evaluate conditional branches, macro
expansion, SDK search paths, generated headers, or private build inputs.
A missing match remains an unresolved source question rather than a hardware
capability conclusion.

## Implementation decision

This audit does **not** authorize copying H9 into XNU 8796, enabling the old
machine selector, changing feature flags, or writing a target CPU driver.
Before a target-specific platform patch can be reviewed, the project still
needs exact source/build provenance, a complete conditional/dependency review,
a reproducible baseline build environment, and verified runtime platform and
handoff contracts.

The next hardware-interface investigation is the target AIC/timer path. The
19H422 static DeviceTree already identifies an AIC master node and an
AIC-timebase node with register windows consumed by the generic XNU mapper.
What remains unverified is the final runtime DeviceTree, complete interrupt
specifier/routing and per-CPU delivery, EOI behavior, timer counter semantics
and frequency, and compatibility of the relevant implementation with XNU
8796. See the [interrupt/timer interface audit](interrupt-timer-interface-audit.md)
and [parsed target DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md).

M6 remains in progress and M7/SpringBoard has not started. The physical
iPhone 7 remains on iOS 12.1.4.


## Full-tree scan result (2026-11-20)

The pinned GitHub Actions full-source run completed successfully:
[H9 source-closure workflow run 44864823137](https://github.com/that-one-guy7/Project-Sweet-10/actions/runs/44864823137).
The synthetic test suite, both complete source checkouts, scanner, and JSON
artifact upload all passed. The artifact is named
`h9-source-closure-a379060efdcb2fbc62b600c025d39f4ca7b22ec8`; its ZIP
SHA-256 is
`67f292f3c983a1ee2133d39ee879a862b1f4f39484fbd3edd5778017ee78a69e`.

The scanner read **3,508** candidate source/build files in XNU 7195 and
**3,961** in XNU 8796. It extracted **12** H9 feature macros and scanned
their identifier-token occurrences. Counts below are textual occurrences
and unique containing paths; a source line can be a preprocessor condition,
definition, comment, closing directive, or other plain text. They are not
counts of compiled/active code paths.

| H9 macro | XNU 7195 occurrences / files | XNU 8796 occurrences / files | Defined by XNU 8796 H13? |
|---|---:|---:|---:|
| `APPLEHURRICANE` | 4 / 4 | 3 / 3 | No |
| `NO_MONITOR` | 9 / 6 | 5 / 5 | Yes |
| `HAS_MIGSTS` | 2 / 1 | 0 / 0 | No |
| `HAS_KTRR` | 1 / 1 | 1 / 1 | No |
| `HAS_CPMU_L2C_EVENTS` | 2 / 2 | 0 / 0 | No |
| `CORE_NCTRS` | 12 / 7 | 9 / 4 | Yes |
| `CPMU_AIC_PMI` | 16 / 5 | 17 / 4 | No |
| `__ARM_16K_PG__` | 39 / 8 | 44 / 9 | Yes |
| `__ARM_KERNEL_PROTECT__` | 116 / 17 | 130 / 18 | No |
| `__ARM_GLOBAL_SLEEP_BIT__` | 8 / 5 | 7 / 4 | Yes |
| `__ARM_PAN_AVAILABLE__` | 27 / 12 | 24 / 10 | Yes |
| `SINGLE_STEP_RETIRE_ERRATA` | 2 / 1 | 0 / 0 | No |

### Interpretation of the full-tree results

- **Hurricane conditionals persist, but not the T8010 profile.** The three
  XNU 8796 occurrences of `APPLEHURRICANE` are conditionals in
  `monotonic_arm64.c:174`, `proc_reg.h:168`, and `sleh.c:232`.
  The historical `start.s` occurrence is not present in the candidate
  scan, consistent with the earlier observation that the old startup
  HID5 workaround is absent at the corresponding path.
- **Some shared architecture features persist.** `__ARM_16K_PG__`,
  `__ARM_GLOBAL_SLEEP_BIT__`, and `__ARM_PAN_AVAILABLE__` are defined by
  H13 and still have generic source consumers. That is evidence that
  generic 16K-page, global-sleep-bit, and PAN code paths remain in the
  newer tree. It does not establish that the T8010 board uses them with
  the H9 settings or that the corresponding A10 hardware behavior matches.
- **The KTRR source hook remains, but H13 is a different profile.**
  XNU 8796 still has one `HAS_KTRR` conditional in
  `apple_arm64_common.h:51`, but H13 declares `HAS_CTRR`, not
  `HAS_KTRR`. KTRR and CTRR must not be treated as equivalent hardware
  features.
- **PMU code remains conditional and has evolved.**
  `CPMU_AIC_PMI` occurs 17 times in four XNU 8796 files, including the
  additional `perfmon_arm64.c` path. H13 does not define this macro.
  The textual inventory does not determine whether a product build sets
  it or whether the A10 PMU interrupt wiring matches the newer path.
- **The counter-count interface remains, but values are profile-specific.**
  The H13 header defines `CORE_NCTRS=10`, while other definitions in the
  candidate `board_config.h` include placeholder values for other
  machine profiles. Shared code uses the macro, but the H13 value cannot
  be adopted as an H9/T8010 configuration value by analogy.
- **The legacy kernel-protection flag has many remaining consumers.**
  `__ARM_KERNEL_PROTECT__` occurs 130 times in 18 candidate files,
  including startup, CPU, VM, pmap, TLB, task, and machine-dependent code.
  H13 does not define it. The presence of generic guarded code is not
  permission to enable the old H9 flag: the newer tree also has separate
  `XNU_MONITOR`, CTRR, and parameterized-pmap mechanisms, and source
  comments describe combinations that are constrained or mutually
  exclusive.
- **Three H9 feature names have no textual matches in the candidate tree:**
  `HAS_MIGSTS`, `HAS_CPMU_L2C_EVENTS`, and
  `SINGLE_STEP_RETIRE_ERRATA`. This establishes only that the scanner
  found no matching tokens in the selected source/build file types. It
  does not establish that the hardware capability is absent, that Apple
  removed support from its shipped kernels, or that no private/generated
  replacement exists.
- **`NO_MONITOR` is a generic selector, not a unique A10 marker.**
  Candidate occurrences include H13, BCM2837 and VMAPPLE profile
  definitions, a generic CPU condition, and an LLDB macro string. It
  cannot identify a T8010 machine configuration.

### Include closure and limitations

The local include resolver followed **23** source/header files reachable
from historical `H9.h`. The direct include is
`apple_arm64_common.h`; the locally resolved chain also includes
`apple_arm64_regs.h`, `AIC.h`, `S3cUART.h`, and
`dockchannel.h`, plus architecture/type headers. Two includes from
`bsd/sys/cdefs.h` remained unresolved by this limited local resolver:
`sys/_symbol_aliasing.h` and `sys/_posix_availability.h`. They are
reported as resolver gaps, not claimed absent from every SDK or build
environment.

The scanner does not evaluate conditional compilation, resolve macro
expansion, reproduce compiler include flags, inspect private/generated
build inputs, or establish a complete link dependency graph. A zero
textual-reference result is not proof of unsupported hardware. The report
is a repeatable source inventory that tells us where to focus manual
review; it does not authorize copying H9 into XNU 8796 or enabling any
feature macro.

## Updated recommendation

The full H9 macro search is now complete for the pinned public 7195 and
8796 trees. The next code-level preparation remains a **manual, per-feature
migration assessment** for the high-impact areas: Apple CPU startup/errata,
KTRR-versus-CTRR integrity setup, PMU/AIC interrupt coupling, 16K-page and
pmap protections, and CPU power/sleep handling. Each needs a specific
source-level replacement or an explicit unresolved blocker; no feature
macro should be carried forward just because its name still appears.

Separately, the AIC/timebase DeviceTree nodes and first register windows
are already known from the 19H422 static tree. The next hardware research
must focus on interrupt specifier decoding, routing/per-core delivery,
EOI, timer counter semantics and runtime frequency, and whether public
XNU 8796 contains the needed AIC controller implementation or only
generic mapping/header support. No driver implementation is justified
until those contracts are understood.
