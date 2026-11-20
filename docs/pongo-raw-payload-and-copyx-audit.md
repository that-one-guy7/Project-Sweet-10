# PongoOS raw-payload and KernelCache-copy path audit

## Scope and source pin

This is a read-only source audit of the public PongoOS revision
[`4c9b7541629234147fcc778f0ce4162482aaccef`](https://github.com/checkra1n/PongoOS/commit/4c9b7541629234147fcc778f0ce4162482aaccef).
It distinguishes the existing boot-argument pass-through, raw-payload entry,
KernelCache-copy helper, and KPF-assisted stock XNU path.

Reviewed implementation files:

- [`src/boot/stage3.c`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/boot/stage3.c#L109-L151)
- [`src/boot/main.c`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/boot/main.c#L31-L41)
- [`src/kernel/entry.c`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/kernel/entry.c#L123-L327)
- [`src/boot/jump_to_image.S`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/boot/jump_to_image.S#L28-L52)
- [`src/shell/main.c`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/shell/main.c#L40-L66)
- [`src/drivers/xnu/xnu.c`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/drivers/xnu/xnu.c#L69-L103)
- [`src/kernel/pongo.h`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/kernel/pongo.h#L77-L130)
- [PongoOS README](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/README.md#L28-L40)

No Pongo command was run. No payload was uploaded, no XNU image was replaced, and no device or firmware was changed.

## 1. Existing Apple boot-argument and entry-point pass-through

The stage-3 code receives a boot-argument pointer and an image entry point. For the kernel case, it records those pointers and enters Pongo's main path with them; the hypervisor case uses a separate argument handoff. The boot-stage main function calls `pongo_entry()` using the supplied kernel arguments and entry point.

In `pongo_entry()`, Pongo retains the incoming `boot_args` pointer and original entry point. Its cached entry code derives the DeviceTree pointer from `boot_args.deviceTreeP`, reads the `arm-io/ranges` property, and identifies the SoC from the supplied `arm-io/device_type`. The source includes a `t8010` recognition branch that assigns SoC number `0x8010`.

This is useful evidence that the reviewed PongoOS source knows the T8010 SoC identifier and operates on an Apple-provided boot-argument/DeviceTree context. It is **not** proof that every PongoOS driver or boot-stage assumption works on the iPhone 7 `iPhone9,1`, and it does not show Pongo synthesizing the final runtime DeviceTree or a new target memory map.

## 2. Raw uploaded-payload entry path (`bootr`)

The shell's raw-boot handler checks that an upload exists, marks the boot mode as `BOOT_FLAG_RAW`, and yields to the boot flow. In `pongo_entry()`, that mode dispatches to `jump_to_image_extended()` with three inputs:

1. The address of the uploaded raw payload in Pongo's transfer buffer.
2. The existing Apple `boot_args` pointer.
3. The original kernel entry-point pointer.

The assembly helper sets the uploaded payload as the branch destination, places the boot-argument pointer in `x0`, places the original kernel entry point in `x8`, clears `x1` through `x3`, and branches to the payload.

This is a real extension point for a separately supplied raw stage. It is more specific than saying Pongo has no custom-payload handoff at all. However, the reviewed path itself does not parse a Mach-O KernelCache, validate or relocate its segments, allocate a new kernel memory layout, construct new `boot_args`, or populate the missing runtime DeviceTree fields. Those responsibilities would belong to a future payload/loader and remain unimplemented in Project Sweet-10.

## 3. ARM64 `boot_args` layout cross-check

The pinned PongoOS header defines `BOOT_LINE_LENGTH_iOS13` as `0x260` (608 bytes). The pinned XNU 8796 ARM64 header defines `BOOT_LINE_LENGTH` as 608 bytes. The PongoOS `iOS13` union member and XNU 8796's ARM64 `boot_args` therefore use the same command-line length.

The structures also have matching field offsets on ARM64. PongoOS marks its structure packed and supplies explicit padding fields; XNU uses the platform compiler's natural 8-byte alignment for 64-bit pointers and `unsigned long`. The explicit PongoOS padding corresponds to the alignment gaps in XNU:

| Field | PongoOS/XNU ARM64 offset |
|---|---:|
| `Revision` | `0x000` |
| `Version` | `0x002` |
| `virtBase` | `0x008` |
| `physBase` | `0x010` |
| `memSize` | `0x018` |
| `topOfKernelData` | `0x020` |
| `Video` | `0x028` |
| `machineType` | `0x058` |
| `deviceTreeP` | `0x060` |
| `deviceTreeLength` | `0x068` |
| `CommandLine[608]` | `0x06c` |
| `bootFlags` (`iOS13` view) | `0x2d0` |
| `memSizeActual` (`iOS13` view) | `0x2d8` |
| `sizeof(boot_args)` | `0x2e0` |

The offsets are derived directly from the two declarations for the ARM64 ABI. This is a positive source-level layout match for the PongoOS `iOS13` view and the pinned XNU 8796 structure. It removes a suspected structure-layout mismatch between these two headers; it does **not** establish the live `Revision`, `Version`, flags, physical/virtual bases, memory sizes, framebuffer fields, DeviceTree address/length, or a matching iPhone9,1 KernelCache. No runtime boot-argument block has been captured for this project.

Sources: [PongoOS `pongo.h`](https://github.com/checkra1n/PongoOS/blob/4c9b7541629234147fcc778f0ce4162482aaccef/src/kernel/pongo.h#L40-L115) and [XNU 8796 ARM64 `boot.h`](https://github.com/apple-oss-distributions/xnu/blob/1b191cb58250d0705d8a51287127505aa4bc0789/pexpert/pexpert/arm64/boot.h#L15-L90).

## 4. Existing KernelCache-copy helper (`loadx`) 

The XNU driver registers a shell command named `loadx`, whose handler is `pongo_copy_xnu()`. The handler:

- Requires uploaded bytes.
- Uses the current `gEntryPoint` to search backward for the existing 64-bit Mach-O header.
- Copies the uploaded bytes over the located in-memory KernelCache image.

The source comment is decisive: it says this function performs only the copy and expects the caller to modify `gEntryPoint`; it leaves Mach-O parsing and setting `gEntryPoint` as a TODO.

Therefore, `loadx` is a low-level in-place replacement helper, not a self-contained, validated custom-XNU image loader. It does not establish that an arbitrary Sweet-10 kernel is correctly laid out, relocated, entered, or compatible with the existing boot arguments and memory map. It must not be treated as a ready-to-run replacement path.

## 5. Distinguish the normal XNU/KPF route

The normal Pongo XNU route retains the incoming XNU entry point and boot arguments. The registered `bootx` and `bootux` handlers choose the KPF-hooked or unhooked route. The main entry flow runs the corresponding XNU preparation and then returns through the stage-3 image-exit path. The README's consolidated PongoOS/KPF build description refers to this existing XNU path.

The KPF source performs pattern-based modifications to code in the loaded XNU image. That is distinct from the raw-payload entry point and distinct from implementing all of the image parsing, relocation, memory ownership, and boot-argument work required by a custom kernel.

## 6. What this changes for Project Sweet-10

The source now supports this more precise architecture description:

| PongoOS capability | What the reviewed code establishes | What it does not establish |
|---|---|---|
| Boot-stage handoff | Passes existing Apple boot arguments and original entry point into Pongo | Correct iPhone9,1 runtime values or full target compatibility |
| SoC recognition | Contains a `t8010` identifier branch | Complete T8010 board/driver support |
| Raw payload (`bootr`) | Branches to an uploaded raw stage with existing boot args and original entry in registers | A Mach-O/XNU loader, relocation, new memory map, or corrected DeviceTree |
| Kernel copy (`loadx`) | Copies uploaded bytes over the in-memory KernelCache | Mach-O validation, entry-point update, safe replacement, or XNU compatibility |
| KPF route | Applies code-pattern patches to the already loaded XNU image | Native A10 platform support or a general custom-kernel loader |

The 19H422 iPhone9,1 DeviceTree we parsed is a static IPSW component. Its zero-valued clock and memory/panic fields do not supply the final runtime values consumed by Pongo or XNU. The separate `20H392` reference remains the selected iOS 16 userland target, not proof of an iPhone9,1 KernelCache identity.

## 7. Next evidence gates

Before implementing or invoking a Sweet-10 payload, the project still needs:

- A verified XNU source/build identity for the chosen 20H392 userland strategy.
- A documented payload format and complete Mach-O/KernelCache parsing and relocation design.
- A revision-matched XNU entry-state and `boot_args` specification.
- A verified runtime iPhone9,1 memory map and DeviceTree, including values absent or zero in the static IPSW tree.
- A target-specific A10/T8010 XNU machine/platform plan and reproducible host build.
- Host-side tests for bounds, image segments, address arithmetic, and boot-argument validation before any device integration.

**Current decision:** Treat PongoOS `bootr` as a possible future raw-stage entry point and `loadx` as an incomplete in-place copy helper. Neither is a finished Project Sweet-10 loader. Keep M3 (boot contract) open; do not run `bootr` or `loadx`, replace a kernel image, or attempt a device boot on the strength of this source audit alone.
