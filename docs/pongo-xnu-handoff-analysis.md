# PongoOS and the XNU handoff: source-based assessment

## Scope and revisions

This note separates the public PongoOS pre-boot environment from the XNU kernel image Sweet-10 intends to run.

Reviewed sources:

- PongoOS repository: [checkra1n/PongoOS](https://github.com/checkra1n/PongoOS)
- PongoOS revision: [`4c9b7541629234147fcc778f0ce4162482aaccef`](https://github.com/checkra1n/PongoOS/commit/4c9b7541629234147fcc778f0ce4162482aaccef), the repository's inspected `master` commit at review time
- PongoOS README and KPF source: [README](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/README.md), [`checkra1n/kpf/main.c`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/checkra1n/kpf/main.c)
- PongoOS boot-stage source: [`src/boot/stage3.c`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/boot/stage3.c)
- Apple XNU: [`xnu-8796.141.3/pexpert/pexpert/arm64/boot.h`](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/boot.h), [`osfmk/arm64/start.s`](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/start.s)

This is source analysis, not a device procedure. No exploit invocation, Pongo command sequence, firmware installation, partition write, or boot attempt is specified.

## What upstream PongoOS documents

The PongoOS README distinguishes four build outputs:

- `Pongo`: the main PongoOS Mach-O.
- `Pongo.bin`: a bare-metal binary form of PongoOS.
- `checkra1n-kpf-pongo`: the checkra1n kernel patchfinder built as a Pongo module.
- `PongoConsolidated.bin`: PongoOS and the kernel patchfinder combined.

The README describes the Pongo-only output as reaching the Pongo shell without KPF. It describes the consolidated output as automatically running KPF and then proceeding to XNU; a separate option keeps execution at the Pongo shell after KPF is loaded.

This is evidence that PongoOS can be an early execution stage in an Apple boot path. It is **not** a documented promise that the consolidated image accepts an arbitrary custom XNU binary, converts any KernelCache into a loadable image, or constructs a new iPhone9,1-specific XNU boot environment.

## What the KPF source actually does

The pinned `checkra1n/kpf/main.c` source contains pattern-search and patch callbacks that operate on XNU kernel code. Examples in the reviewed source include:

- a dyld path-check callback;
- an AMFI/trust-cache related callback;
- a root mount (`mac_mount`) callback.

These routines search instruction streams and modify matched instructions or branch behavior. That is kernel patching of a kernel image already present in the supported boot flow. It is distinct from implementing a general image loader and does not add the missing A10/T8010 platform support to XNU 8796.

Accordingly, Sweet-10 should not treat the stock PongoOS + KPF path as its custom-kernel loader. The KPF source is useful to understand what the existing checkra1n flow does, but its patches and security-policy changes are not a replacement for a platform port. Sweet-10's own research should preserve kernel security semantics rather than importing unrelated patch behavior.

## XNU 8796 boot-argument contract visible in public source

The pinned XNU header defines an ARM64 `boot_args` structure with these fields, in order:

| Field | Meaning recorded by the header |
|---|---|
| `Revision`, `Version` | Structure revision and version |
| `virtBase`, `physBase`, `memSize` | Memory virtual base, physical base, and size |
| `topOfKernelData` | Highest physical address used in the kernel data area |
| `Video` | Boot video information |
| `machineType` | Machine type |
| `deviceTreeP`, `deviceTreeLength` | Flattened DeviceTree pointer and byte length |
| `CommandLine[608]` | Kernel command-line buffer |
| `bootFlags` | Bootloader-provided flags |
| `memSizeActual` | Actual memory size |

The same header declares boot-argument revisions and versions. In `start.s`, the first-CPU startup path receives a boot-argument pointer and reads the virtual base, physical base, memory size, and boot flags before establishing early kernel mappings and entering the C initialization path.

This is a concrete, revision-specific XNU contract. It is not a complete loader specification: a compatible handoff also has execution-state, memory ownership, kernel image layout, CPU, and DeviceTree requirements. The public source structure does not supply the missing iPhone9,1 values.

## Implications for Project Sweet-10

The intended chain has at least three separate engineering components:

1. **Pre-boot environment:** PongoOS executes on the target and provides the facilities needed by the selected boot design.
2. **Sweet-10 image-loading/handoff layer:** a separately validated design must identify the intended custom XNU image and provide the correct entry context, memory layout, boot arguments, and DeviceTree contract.
3. **A10/T8010 XNU platform:** XNU must contain or be adapted to contain the board configuration, CPU/platform initialization, interrupt/timer support, and required early services for iPhone9,1.

The PongoOS README establishes the existence of a Pongo-to-XNU flow for its documented KPF path. It does not establish component 2 for a custom Sweet-10 kernel, and it does not establish component 3.

The current `20H392` reference remains an iPhone X/A11/T8015 userland donor. The available iPhone7 `19H422` reference is iOS 15.8.8 and can inform target-side DeviceTree research only. Neither release label is proof that the other device's kernel image or boot arguments are interchangeable.

## Evidence gates before a custom XNU loader is designed

| Gate | Required evidence | Status |
|---|---|---|
| P1 — Pongo environment identity | Exact PongoOS revision/build and target support evidence for the device | Upstream source reviewed; no Sweet-10 device-session record is claimed |
| P2 — Custom image format | Exact format and metadata of the selected XNU image, including the relationship between the public XNU source and the image | Open |
| P3 — Entry contract | Revision-matched entry state and register/exception-level requirements | Partially documented from XNU source; loader-specific mapping open |
| P4 — Boot arguments | Valid `boot_args` revision/version and values, including memory bounds and DeviceTree pointer/length | Structure identified; target values unknown |
| P5 — Memory ownership | Verified available/reserved regions and lifetime/overlap constraints | Open |
| P6 — Target DeviceTree | Hash-verified iPhone9,1 tree and required property encodings/values | Open; public 19H422 survey is provisional and its `reg` totals are heuristic |
| P7 — A10 platform | T8010 machine configuration and required CPU/platform dependencies in the chosen XNU baseline | Open; pinned public XNU 8796 normal ARM64 machine allowlist omits T8010 |

No Pongo transport, exploit, or kernel-loading code should be added until these contracts can be stated and tested independently. First complete host-side artifact inspection and source review.

## Project decision

Keep PongoOS as the proposed early boot environment, but track its shell, its KPF-assisted XNU path, and a future custom Sweet-10 XNU handoff as separate items. Do not label PongoConsolidated as a custom XNU loader. Do not infer target addresses, memory ranges, DeviceTree properties, or entry values.

This document does not claim that PongoOS has been run on a Sweet-10 build, that a custom XNU image has been loaded, or that iOS 16 has booted on iPhone7.
