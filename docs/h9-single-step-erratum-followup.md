# H9 single-step retirement erratum: 7195-to-8796 source comparison

## Scope and result

This follow-up narrows one item in the H9/T8010 migration audit:
`SINGLE_STEP_RETIRE_ERRATA`. The historical H9 header names Radar
20619637 and enables a conditional instruction-synchronization barrier in
two ARM64 debug-state routines. The reviewed XNU 8796 source removes that
macro guard, but it does **not** remove the barrier from those routines:
it places an unconditional ISB after each routine's MDSCR update branch.

This corrects the shorthand that the old workaround is simply absent from
the newer file. The source establishes a changed barrier placement and
broader control-flow coverage. It does **not** establish that XNU 8796's
barrier was intentionally introduced as the fix for Radar 20619637, that
the erratum applies to every T8010 stepping, or that the exact 20H392
product build selects these source paths.

No build, binary execution, device access, firmware change, or boot
operation is involved.

## Pinned source identity

The comparison uses immutable public Apple XNU commits and Git blob IDs:

| Source | Commit | File | Git blob SHA-1 |
|---|---|---|---|
| Historical H9 | `2a647cb3489890a0948eb7ee3a118307d39bb574` | `pexpert/pexpert/arm64/H9.h` | `53143c7b6d8efbea630bf2afc32e96fd5ed161fb` |
| Historical H9 | `2a647cb3489890a0948eb7ee3a118307d39bb574` | `osfmk/arm64/pcb.c` | `ee7417e20df5c7ac89c95178ad7ea3b047ae1240` |
| iOS 16-era public candidate | `1b191cb58250d0705d8a51287127505aa4bc0789` | `osfmk/arm64/pcb.c` | `7b98a3323d3ac29e76022899d3dfa00c156ea00f` |
| iOS 16-era public candidate | `1b191cb58250d0705d8a51287127505aa4bc0789` | `pexpert/pexpert/arm64/H13.h` | `22e8c4068d815da283e2bbd59c23bb5ee29b1066` |

The public tag names are `xnu-7195.121.3` and `xnu-8796.141.3`.
The commit and blob IDs above pin the actual inspected source contents;
the donor KernelCache's embedded `8796.142.1.703.8~1` string is not
being treated as either public tag.

## Historical H9 declaration and use

The H9 header contains:

```c
// Hurricane and Zephyr require workaround for radar 20619637
#define SINGLE_STEP_RETIRE_ERRATA 1
```

In XNU 7195 `osfmk/arm64/pcb.c`, both `arm_debug_set32()` and
`arm_debug_set64()` have the same relevant structure:

1. Update the MDSCR breakpoint/watchpoint controls.
2. Test bit 0 of the supplied `mdscr_el1` state.
3. If single-step is enabled, update MDSCR and mask the saved-state SS bit.
4. Otherwise, clear the MDSCR SS bit and execute
   `__builtin_arm_isb(ISB_SY)` under
   `#if SINGLE_STEP_RETIRE_ERRATA`.
5. Restore the prior interrupt-enable state.

The two guarded sites are at:
- `arm_debug_set32()`: [XNU 7195 pcb.c lines 684–697](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/pcb.c#L684-L697)
- `arm_debug_set64()`: [XNU 7195 pcb.c lines 876–889](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/pcb.c#L876-L889)

The H9 declaration is at [H9.h lines 45–50](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h#L45-L50).

## XNU 8796 placement

The corresponding XNU 8796 routines no longer reference
`SINGLE_STEP_RETIRE_ERRATA`. However, after the same MDSCR update
if/else branch, each routine executes an unconditional
`__builtin_arm_isb(ISB_SY)` before restoring interrupts:

- `arm_debug_set32()`: [XNU 8796 pcb.c lines 766–779](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/pcb.c#L766-L779)
- `arm_debug_set64()`: [XNU 8796 pcb.c lines 968–981](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/pcb.c#L968-L981)

The difference is therefore not “ISB present” versus “ISB absent”:

| Aspect | XNU 7195 / H9 | XNU 8796 |
|---|---|---|
| Macro guard | `SINGLE_STEP_RETIRE_ERRATA` | No corresponding guard |
| 32-bit debug-state routine | ISB only in the `else` branch | ISB after the full if/else |
| 64-bit debug-state routine | ISB only in the `else` branch | ISB after the full if/else |
| Branch coverage | Conditional on SS bit being clear and macro enabled | Unconditional for either SS-bit branch |
| Interrupt restoration | After the guarded ISB / branch | After the unconditional ISB |

This is a source-level control-flow comparison. It does not prove that the
newer unconditional ISB was intended to replace the named erratum
workaround, nor that its architectural effect is sufficient for every
Hurricane/Zephyr implementation or revision. The source comments in the
newer routines do not attribute the barrier to Radar 20619637.

## Updated migration classification

Classify this item as **barrier retained, implementation changed, erratum
relationship unresolved**:

- Do not mark the barrier itself as missing from XNU 8796.
- Do not claim the old macro or its CPU-specific erratum annotation remains.
- Do not infer that the erratum was fixed in silicon or that a target
  T8010 product build uses the newer source path.
- Keep the H9-specific `HAS_MIGSTS` exception-reporting question separate;
  the 8796 `sleh.c` comparison remains a distinct unresolved source change.

This finding reduces one false-positive migration concern but does not
reduce the overall CPU/errata risk to low. CPU startup, the historical
HID5 startup workaround, PMU/AIC coupling, protection mode, sleep/wake,
and exact product build inputs remain independent questions.

## Relationship to the 20H392 donor

The donor KernelCache reports XNU
`8796.142.1.703.8~1/RELEASE_ARM64_T8015`. The inspected public
`xnu-8796.141.3` tree is a nearby source candidate, not an Apple
source-to-binary attestation for 20H392. This comparison therefore
describes public source only. It does not show that the 20H392 donor
contains the exact same `pcb.c`, nor does it show that the public
candidate was built with an H9/T8010 configuration.

The physical iPhone 7 remains on iOS 12.1.4. No runtime behavior,
hardware erratum status, build success, ABI compatibility, or SpringBoard
milestone is claimed.

## References

- [XNU 7195.121.3 H9.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)
- [XNU 7195.121.3 pcb.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/osfmk/arm64/pcb.c)
- [XNU 8796.141.3 pcb.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/pcb.c)
- [Existing H9 feature-macro consumer audit](h9-feature-macro-consumer-audit.md)
- [H9/T8010 migration-risk classification](h9-t8010-migration-risk-classification.md)
