# Reference source matrix

This matrix records what each upstream source can and cannot substantiate for Project Sweet-10.

| Source | What it establishes | What it does not establish for iPhone9,1 |
|---|---|---|
| [Apple XNU](https://github.com/apple-oss-distributions/xnu) | Public XNU source and release history | Complete A10/iPhone7 platform support in a chosen build |
| [ios-sweet README](https://github.com/dipa-studio/ios-sweet/blob/main/README.md) | Its stated xnu-8796/iOS 16.7.16 bring-up on Redmi Note 10 Pro / SM7150 | Transferability of Qualcomm platform code to A10 |
| [ios-sweet NOTES](https://github.com/dipa-studio/ios-sweet/blob/main/NOTES.md) | Project-specific engineering observations and milestone history | iPhone7 hardware facts or a verified iPhone7 boot path |
| [ios-sweet shim](https://github.com/dipa-studio/ios-sweet/tree/main/shim) | Their boot shim and handoff implementation | An iPhone7-compatible boot handoff |
| [ios-sweet QEMU guide](https://github.com/dipa-studio/ios-sweet/blob/main/docs/QEMU_TESTING.md) | Their virtual ARM64 test workflow | Real iPhone7 hardware emulation |
| [Project Sandcastle](https://github.com/corellium/projectsandcastle) | Linux-on-iPhone research utilities and PongoOS loader architecture | XNU boot support through its Linux loader |

## Interpretation rules

- Attribute claims to the project that made them.
- Keep observed upstream behavior separate from our hypotheses.
- Pin commit SHAs before copying or adapting any code.
- Review license and provenance before vendoring source.
- Never infer platform support from a symbol name, chip string, or successful compile alone.
