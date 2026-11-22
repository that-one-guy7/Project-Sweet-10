# iPhone9,1 19H422 generic ApplePMGR CPU-function string audit

## Scope and source identity

This note records a read-only inspection of user-supplied output from the generic
`com.apple.driver.ApplePMGR` prelinked KEXT in the iPhone9,1 / D10AP 19H422
KernelCache. It extends the segment map recorded in
[the generic ApplePMGR Mach-O audit](iphone91-19h422-applet8010pmgr-binary-audit.md).

The target KernelCache identity is:

- 19H422 / iOS 15.8.8
- Darwin 21.6.0 / XNU `8020.241.44~1`
- `RELEASE_ARM64_T8010`
- Size: 44,924,928 bytes
- SHA-256: `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`

The generic ApplePMGR prelink header is UUID
`29A10C96-489B-3D22-8D81-974A570645C3`, source version
`939.140.3.0.0`, with `__TEXT_EXEC` VM address
`0xfffffff0065b6000`, inner Mach-O `LC_SEGMENT_64.fileoff` `0x00f4f280`, and size
`0x34a4c`. The header's symbol tables are stripped.

## CPU-related string evidence

The user searched the extracted `ApplePMGR.prelink-text.bin` with
`strings -a -n 5` and a case-insensitive filter for CPU-core, cluster,
idle, and ApplePMGR identifiers. The supplied output includes:

### Core-enable function identifier

- `ApplePMGRFunctionEnableCPUCore`
- `site.ApplePMGRFunctionEnableCPUCore`

These are function/type-name-style identifiers found in the generic
ApplePMGR prelink string region. They are not, by themselves, a named
C++ method definition or proof of a particular callback target.

### Cluster-control methods

- `virtual UInt8 ApplePMGR::getPhysicalClusterID(ApplePMGR::ClusterID)`
- `virtual void ApplePMGR::clearClusterInterruptStatus(ApplePMGR::ClusterID, UInt32)`
- `virtual ApplePMGR::PSLevel ApplePMGR::getClusterPowerState(ApplePMGR::ClusterID, UInt32)`
- `virtual void ApplePMGR::enableCluster(ApplePMGR::ClusterID, bool, bool, UInt32)`

### CPU-idle methods

- `void ApplePMGR::_cpuIdle(ApplePMGR::CPUCore *, bool, UInt64 *)`
- `void ApplePMGR::_cpuIdleTimer(ApplePMGR::CPUCore *, UInt64 *)`
- `void ApplePMGR::_cpuIdleInit(ml_processor_info_t *)`

The same output includes CPU-complex initialization, CPU performance
requests, performance-state accounting, and CPU energy/idle counters. This
places core-enable, cluster-power, and idle-management names in the same
generic PMGR image.

## Exact core-enable string offsets

The user later reran the string scan with `strings -a -t x -n 5` and
provided the extracted generic ApplePMGR prelink-header SHA-256:

`4764017feef6d87c1f8a524bf04ec1148817d61fd482639e252325fd0300f43f`

The extracted header's `__TEXT` base VM address is
`0xfffffff005666d80`. The string offsets are file offsets within that
49,023-byte extracted header. Adding the file offset to the header base
produces these candidate string virtual addresses:

| String | Header file offset | Candidate VM address |
|---|---:|---:|
| `ApplePMGRFunctionEnableCPUCore` | `0xa5ac` | `0xfffffff00567132c` |
| `site.ApplePMGRFunctionEnableCPUCore` | `0xa5cb` | `0xfffffff00567134b` |
| `ApplePMGRFunctionCPUIdle` | `0xa4e6` | `0xfffffff005671266` |
| `site.ApplePMGRFunctionCPUIdle` | `0xa4ff` | `0xfffffff00567127f` |
| `virtual IOReturn ApplePMGRFunctionCPUIdle::callFunction(void *, void *, void *)` | `0xa51d` | `0xfffffff00567129d` |

The same filtered output includes a `callFunction` signature for
`ApplePMGRFunctionCPUIdle`, but no corresponding
`ApplePMGRFunctionEnableCPUCore::callFunction` or
`initWithTargetDataAndSymbol` signature. Other function-class entries
also have different levels of string metadata. This is a difference in
the observed string inventory only; it does not prove that the
EnableCPUCore class lacks an implementation, inherits a default handler,
or is not instantiated.

## Static executable cross-references (2026-11-22)

The user supplied the first-pass AArch64 disassembly lines for all
instructions matching the `0xfffffff005671000` page. Three instruction
pairs construct the exact `ApplePMGRFunctionEnableCPUCore` string
address `0xfffffff00567132c`:

| ADRP / ADD sequence | Instructions |
|---|---|
| `0xfffffff0065dae00` / `0xfffffff0065dae04` | `ADRP x1, 0xfffffff005671000`; `ADD x1, x1, #0x32c` |
| `0xfffffff0065daed0` / `0xfffffff0065daed4` | `ADRP x1, 0xfffffff005671000`; `ADD x1, x1, #0x32c` |
| `0xfffffff0065ddf04` / `0xfffffff0065ddf08` | `ADRP x1, 0xfffffff005671000`; `ADD x1, x1, #0x32c` |

Each sequence then sets the class-size argument `w3 = 0x38` and calls
`0xfffffff0065ea680`, the stub previously resolved through GOT slot
`0xa8` to the `OSMetaClass` constructor.

The first two sequences load their `x2` argument through
`LDR x2, [0xfffffff006f18000 + 0xfd8]`, i.e. GOT VA
`0xfffffff006f18fd8` (offset `0x158` from the generic ApplePMGR GOT
base `0xfffffff006f18e80`). The third sequence supplies `x2 = x19`
and `x0 = 0xfffffff007ae14c0` before calling the same constructor.
The class-name reference, class-size argument, and OSMetaClass call
strongly identify these as metaclass initialization/registration sequences
for `ApplePMGRFunctionEnableCPUCore`; they do not identify its
`callFunction` callback or prove that the site is instantiated on D10AP.

The first-pass output contains no adjacent `ADD #0x34b` reference to the
`site.ApplePMGRFunctionEnableCPUCore` string. This only means that this
filtered code-reference output did not show a direct immediate construction
of that site-string address. It does not rule out a pointer stored in
read-only data, generated tables, or another indirect registration path.

### Superclass-slot result (2026-11-22)

The user read the 64-bit value at ApplePMGR GOT offset `0x158`:

```
00000158: fffffff0079e4dd0
```

The raw pointer therefore resolves to VA `0xfffffff0079e4dd0`. The same
value was mapped against the target 19H422 KernelCache:

- File offset: `0x2690dd0`
- Segment/section: `__PRELINK_DATA.__data`
- Segment permissions: `rw-/rw-`
- Segment VM range: `0xfffffff0079e4000–0xfffffff007b38000`
- Segment file range: `0x02690000–0x027e4000`

The user then read 0x80 bytes from file offset `0x2690dd0`; all sixteen
reported 64-bit words were zero. This is an on-disk observation about this
range, not proof that it is a particular class object, a true zero-fill
section, or an initialized runtime object.

Because the pointer is loaded into x2 for the previously identified
`OSMetaClass(const char *, const OSMetaClass *, unsigned int)` call, it is
the superclass-metaclass pointer for `ApplePMGRFunctionEnableCPUCore`.
The later shared-prelink initializer identifies the storage at this
address as the `AppleARMFunction` metaclass; see the confirmed hierarchy
section below.
The third initialization sequence's x0 value
`0xfffffff007ae14c0` separately maps to file offset `0x278d4c0` in
`__PRELINK_DATA.__data`; no bytes at that second address were supplied.

The user also ran `ipsw kernel cpp "$KC"` and two class-filtered
inheritance queries. All three returned `no classes discovered`. This
means the tool did not recover a class list or inheritance chain from this
input. It does **not** show that the classes are absent. The inspected
upstream IPSW implementation opens the Mach-O and runs its C++ scanner,
then emits this warning when its display set is empty:
[kernel_cpp.go](https://github.com/blacktop/ipsw/blob/26b65938cf4c9479cb5627d2d479492a1dcdd13e/cmd/ipsw/cmd/kernel/kernel_cpp.go).
No IPSW version string was included in the user's output, so this source
inspection is explanatory rather than proof of the exact local binary version.

A separate grep for `fffffff006f18000` and `#0xfd8` in the local
`.a2s` text returned no matches. That empty search is not evidence that
the earlier AArch64 call-site instructions are absent; the exact three
class-name references were previously supplied from the corrected generic
ApplePMGR executable disassembly.

### Wider executable-reference check (2026-11-22)

The user ran the requested disassembly search against the corrected
215,628-byte generic ApplePMGR executable segment. The pipeline returned
no matching lines for page `0xfffffff0079e4000`. This means the supplied
generic ApplePMGR executable dump did not expose a direct ADRP/page
reference to the AppleARMFunction metaclass storage. It does not
establish that the address is unused: the owning class initializer is
in another prelinked component, as the later shared-section reference
analysis demonstrates.

### Shared prelink references and confirmed superclass identity (2026-11-22)

The user confirmed local tool versions:

- IPSW `3.1.749`, build commit
  `a7dfadbcaca8375b424c12a68dae40767e5e07c1`
- GNU `aarch64-linux-gnu-objdump` / Binutils `2.42`

The broad shared `__PLK_TEXT_EXEC` disassembly previously aborted near
`0xfffffff0059928b0` with the
`get_sreg_qualifier_from_value` assertion. This matches
[Binutils PR 31595](https://sourceware.org/bugzilla/show_bug.cgi?id=31595);
a downstream patch backported a fix to a Binutils 2.42 recipe
([2.42 backport](https://patchwork.yoctoproject.org/project/oe-core/patch/20240524201214.3858538-2-mark.hatle%40amd.com/)).
The broad scan remains incomplete; the bounded disassembly windows
recorded below completed successfully.

The user mapped the class-name strings in the outer KernelCache:

| VA | File offset | Section | String |
|---|---:|---|---|
| `0xfffffff0052ea1a4` | `0x9761a4` | `__PRELINK_TEXT.__text` | `AppleARMFunctionSlowAdaptiveClocking` |
| `0xfffffff0052ea1fc` | `0x9761fc` | `__PRELINK_TEXT.__text` | `AppleARMFunctionSlowAdaptiveClockingAggressor` |
| `0xfffffff0052e1e3c` | `0x96de3c` | `__PRELINK_TEXT.__text` | `AppleARMFunction` |
| `0xfffffff0052e1e4d` | `0x96de4d` | `__PRELINK_TEXT.__text` | `site.AppleARMFunction` |

The user mapped the final two offsets with
`ipsw macho o2a`. The local `.a2s` grep did not find
`AppleARMFunction`; that is a symbol-cache non-match, not evidence
against the raw strings or direct code references.

A bounded disassembly of
`0xfffffff00598e060–0xfffffff00598e190` and the supplied surrounding
output show these registrations:

| Call-site VA(s) | x1 class name | x2 superclass metadata | w3 size | Call target |
|---|---|---|---:|---|
| `0xfffffff00598dd14` / `0xfffffff00598dde4` | `AppleARMFunctionSlowAdaptiveClocking` | `0xfffffff0079e4dd0` | `0x40` | `0xfffffff005993844` |
| `0xfffffff00598e07c` / `0xfffffff00598e14c` | `AppleARMFunctionSlowAdaptiveClockingAggressor` | `0xfffffff0079e4dd0` | `0x38` | `0xfffffff005993844` |

A further registration sequence at `0xfffffff00598e5a4` uses
static class storage x0=`0xfffffff0079e57c0`, the
SlowAdaptiveClocking class name in x1, x2=`0xfffffff0079e4dd0`,
and w3=`0x40`.

### Exact AppleARMFunction metaclass initializer

The user found the exact base-class strings:

- `AppleARMFunction`: file offset `0x96de3c`, VA
  `0xfffffff0052e1e3c`.
- `site.AppleARMFunction`: file offset `0x96de4d`, VA
  `0xfffffff0052e1e4d`.

The shared-section disassembly contains three references using
`ADD #0xe3c` for the exact class name. The decisive initializer is
at `0xfffffff005964fe4–0xfffffff005965004`:

```asm
0xfffffff005964fe4: adrp x19, 0xfffffff0079e4000
0xfffffff005964fe8: add  x19, x19, #0xdd0
0xfffffff005964fec: adrp x1, 0xfffffff0052e1000
0xfffffff005964ff0: add  x1, x1, #0xe3c
0xfffffff005964ff4: adrp x2, 0xfffffff006cdf000
0xfffffff005964ff8: ldr  x2, [x2, #0x7c0]
0xfffffff005964ffc: mov  x0, x19
0xfffffff005965000: mov  w3, #0x28
0xfffffff005965004: bl   0xfffffff005993844
```

This sequence sets x0 to `0xfffffff0079e4dd0`, x1 to the exact
`AppleARMFunction` class-name string, w3 to `0x28`, and calls the
previously identified `OSMetaClass` constructor stub. Thus
`0xfffffff0079e4dd0` is the metaclass storage for
`AppleARMFunction`. Two additional constructor-shaped sequences at
`0xfffffff0059642e8` and `0xfffffff0059643b8` use the same
class-name string and class-size value.

The earlier generic ApplePMGR audit established that the
`ApplePMGRFunctionEnableCPUCore` registrations pass the same
`0xfffffff0079e4dd0` value in x2, the superclass argument, after
loading it from generic ApplePMGR GOT slot `0x158`. That value maps
to outer KernelCache offset `0x2690dd0` in writable
`__PRELINK_DATA.__data`; the zero-filled on-disk sample at that
address did not identify the object, but the independent
`AppleARMFunction` initializer now does.

**Resolved static hierarchy:** the shared pointer is
`AppleARMFunction` metaclass storage. The registrations therefore
establish `AppleARMFunction` as the superclass of
`ApplePMGRFunctionEnableCPUCore`,
`AppleARMFunctionSlowAdaptiveClocking`, and
`AppleARMFunctionSlowAdaptiveClockingAggressor` in this 19H422
KernelCache.

This is metaclass-construction evidence, not proof that the EnableCPUCore
class is instantiated for D10AP, that its callback is present or invoked,
that a concrete `IOPMGR::enableCPUCore` override releases a CPU, or that
the kernel boots. The complete broad shared-segment disassembly remains
partial because of the Binutils 2.42 assertion.

The next static question is to determine whether the registered
`ApplePMGRFunctionEnableCPUCore` class has a recoverable callback
implementation and how its registration data refers to it. Keep the
work local and read-only; class registration alone does not establish
runtime behavior.

See the dedicated
[EnableCPUCore superclass-slot audit](iphone91-19h422-applepmgr-enablecore-superclass-slot-audit.md).



### Historical A10 AppleARMFunction symbol precedent

The third-party `iometa` symbol inventory for the iOS 12.0 A10 release
lists `AppleARMFunction::initWithTargetDataAndSymbol` and
`AppleARMFunction::callFunction`, and separately lists the
`ApplePMGRFunctionEnableCPUCore` class. It also lists
`ApplePMGR::enableCPUCores(unsigned int, bool)`. The inventory does
not enumerate separate method entries below the
`ApplePMGRFunctionEnableCPUCore` class heading.

This older A10 inventory is useful as historical context for the
`AppleARMFunction` dispatch model, but it is not the target 19H422
binary and cannot establish that the target class inherits the same
callback implementation or that the older `enableCPUCores` symbol maps
to XNU's `IOPMGR::enableCPUCore` virtual method. See the
[callback and XNU contract cross-check](iphone91-19h422-enablecpu-core-contract-crosscheck.md)
for the evidence boundary and next static check.

## Interpretation boundary

This is a meaningful lead for the unresolved A10 secondary-core path:

1. Public XNU 8796's `IOPMGR::enableCPUCore(cpu_id, entry_pa)` contract
   concerns releasing a secondary CPU from reset and enabling external IRQ
   delivery; its base fallback reaches an unimplemented panic, as documented
   in the prior audit.
2. The target 19H422 generic ApplePMGR string region names
   `ApplePMGRFunctionEnableCPUCore`.
3. The same region names generic PMGR cluster-control and CPU-idle methods.

However, no supplied evidence yet shows that
`ApplePMGRFunctionEnableCPUCore` is registered or instantiated for the
D10AP target, which method it dispatches to, whether the concrete
`ApplePMGR`/ `AppleT8010PMGR` class satisfies the XNU interface, or whether
the operation performs the required hardware/firmware reset release. The
string filter did not produce a scoped method named
`ApplePMGR::enableCPUCore`; absence from this string output is not proof
that such an implementation is absent.

The separate `AppleT8010PMGR` personality and its declared dependency on
`com.apple.driver.ApplePMGR` remain bundle-level metadata. They do not
establish C++ inheritance or runtime provider matching.

## Executable-segment extraction anomaly

The user extracted the reported `__TEXT_EXEC` range from the local KernelCache:

| Field | Value |
|---|---|
| Inner Mach-O `LC_SEGMENT_64.fileoff` | `0x00f4f280` (not an outer-KernelCache offset) |
| Reported size | `0x34a4c` / 215,628 bytes |
| Extracted size | 215,628 bytes |
| SHA-256 | `355a6e2728742cf65d6d0fe5138b702ee898b3d74a631627de03e584b6a62b99` |
| `file` output | `data` |

The supplied AArch64 objdump begins at VM
`0xfffffff0065b6000`, but its first bytes render as readable diagnostic
strings rather than an identifiable instruction sequence. The full-container
mapping checks now explain the discrepancy:

| Check | Result |
|---|---|
| `ipsw macho a2o "$KC" 0xfffffff0065b6000` | offset `0x01c42000`, section `__text`, segment `__PLK_TEXT_EXEC` |
| `ipsw macho o2a "$KC" 0x00f4f280` | address `0xfffffff0058c3280`, section `__text`, segment `__PRELINK_TEXT` |

Therefore the 215,628-byte artifact extracted at `0x00f4f280` is **not**
the outer-KernelCache bytes backing ApplePMGR's `__TEXT_EXEC` start address.
Its SHA-256 (`355a6e2728742cf65d6d0fe5138b702ee898b3d74a631627de03e584b6a62b99`)
is retained only to identify that mistaken extraction; its diagnostic strings
and disassembly must not be attributed to ApplePMGR executable code. The
correct mapped outer-container offset for the segment's starting virtual
address is `0x01c42000`. The inner KEXT's `LC_SEGMENT_64.fileoff` values are
not absolute outer-KernelCache offsets.

The user tested `ipsw kernel extract` and received
`kernelcache type is not MH_FILESET (KEXT extraction not supported yet)`.
This is expected for the legacy prelinked 19H422 KernelCache: IPSW documents
KEXT extraction for modern `MH_FILESET` images only ([kernel guide](https://blacktop.github.io/ipsw/docs/guides/kernel/)).
Do not repeat that command for this target.

The user has now confirmed all four boundary mappings. They place the
segment start at outer offset `0x01c42000`, the last `__text` byte at
`0x01c76583`, the first `__stubs` byte at `0x01c76584`, and the final
segment byte at `0x01c76a4b`. All map to `__PLK_TEXT_EXEC`; text and stubs
are contiguous and the total range matches `0x34a4c`.

The user has now supplied the first 64 bytes and first 100 lines of the
corrected virtual-address dump. It begins with valid-looking AArch64 function
prologues. The first routine references a string pointer at
`0xfffffff005668102` (offset `0x1382` in the extracted header), data at
`0xfffffff006f19080`, and stores a pointer at `0xfffffff006f1c020`.
The second routine stores `0xfffffff006f192d0` and copies several fixed-size
regions from text/data-const addresses.

Stub decoding shows that those branch/call targets load eight-byte
function pointers from __DATA_CONST.__got. The caller at
0xfffffff0065b6000 passes the literal ApplePMGR, a GOT-loaded pointer, and
0x34e98 before calling the stub at 0xfffffff0065ea680; this closely matches
the public XNU OSMetaClass constructor argument pattern, but the actual GOT
import target remains unresolved. The later routine calls stubs at
0xfffffff0065ea860 and 0xfffffff0065ea980; their imported functions are also
unresolved. Do not assign exact C++ names or CPU-start behavior from these
patterns alone. The next checks capture the corrected executable dump's
hash and read the relevant GOT slots:

```sh
stat -c 'Size: %s bytes' "$HOME/ApplePMGR.text-exec.bin"
sha256sum "$HOME/ApplePMGR.text-exec.bin"

test "$(stat -c %s "$HOME/ApplePMGR.text-exec.bin")" -eq 215628 || exit 1
tail -c $((0x4c8)) "$HOME/ApplePMGR.text-exec.bin" \\
  > "$HOME/ApplePMGR.stubs.bin"
aarch64-linux-gnu-objdump -D -b binary -m aarch64 \\
  --adjust-vma=0xfffffff0065ea584 \\
  "$HOME/ApplePMGR.stubs.bin"

xxd -g 1 -s $((0x1382)) -l 96 "$HOME/ApplePMGR.prelink-text.bin"
ipsw macho a2o "$KC" 0xfffffff006f19080
ipsw macho a2o "$KC" 0xfffffff006f192d0
ipsw macho a2o "$KC" 0xfffffff006f1c020
```

Keep the files local. This can identify what the first anonymous routine
references and which imported functions the stubs dispatch to; it still
cannot establish secondary-core release by itself.

## Milestone impact

- **M1:** adds target-native PMGR string inventory only.
- **M2 / G1-G3:** unchanged; exact 20H392 XNU source provenance and a
  reproducible target-compatible baseline build remain open.
- **M4 / CPU early initialization:** narrows a candidate PMGR function path,
  but does not close the secondary-core release contract.
- **M7 / SpringBoard:** not started.

This note records static strings and a host-side extraction discrepancy only.
No Apple binary is committed, no runtime behavior is claimed, and no device,
firmware, partition, or boot state was accessed or changed. The physical
iPhone 7 remains on iOS 12.1.4.
