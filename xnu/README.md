# XNU work area

## Current source baseline

See [BASELINE.lock.json](BASELINE.lock.json) and
[the baseline selection note](../docs/xnu-baseline-selection.md).

Candidate source: Apple `xnu-8796.141.3`, commit
`1b191cb58250d0705d8a51287127505aa4bc0789`.

This is a source-review pin only. It is not a built kernel and is not a statement that
the iPhone9,1 platform is supported.

## Rules

1. Keep upstream source external; do not vendor a full XNU checkout into this repository.
2. Record the exact commit, license, toolchain, and build configuration.
3. Reproduce an unmodified baseline before any local patch.
4. Classify every proposed patch by hardware dependency.
5. Never copy the Qualcomm SWEET machine configuration, interrupt path, device-tree
   expert, or CPU driver as an A10 implementation.
6. Keep boot and device experiments out of the source-baseline phase.

See [PORTING_PLAN.md](PORTING_PLAN.md) and
[the ios-sweet patch triage](../docs/ios-sweet-patch-triage.md).
