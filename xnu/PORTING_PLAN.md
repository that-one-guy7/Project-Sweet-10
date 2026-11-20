# XNU porting plan for iPhone9,1

## Baseline

The iOS 16-generation `xnu-8796` series is a candidate source baseline because the
ios-sweet project documents using it. The exact upstream tag/commit and toolchain for
Project Sweet-10 are not pinned yet.

## Order of work

1. Pin the exact XNU commit and record its license.
2. Reproduce an unmodified build and retain logs and hashes.
3. Map the target's platform selection and early initialization code paths.
4. Inventory the boot arguments and device-tree contract expected by that XNU revision.
5. Document A10 CPU, memory, interrupt, and timer requirements from reliable evidence.
6. Create a minimal, separately reviewed platform design before writing drivers.
7. Add host-side tests for parsers and pure logic.
8. Keep all physical-device interaction out of the initial development loop.

## Patch hygiene

- One conceptual change per patch.
- Include rationale, upstream references, affected configurations, and test evidence.
- Mark platform-specific code explicitly.
- Never copy a Qualcomm-specific patch and merely rename its machine identifier.
- Do not describe a patch as working until the exact test and hardware are recorded.

## Current state

- XNU source selected: candidate only (`xnu-8796`).
- Exact commit pinned: no.
- Baseline build reproduced: no.
- A10 platform implementation: not started.
- iPhone9,1 boot validation: not run.
