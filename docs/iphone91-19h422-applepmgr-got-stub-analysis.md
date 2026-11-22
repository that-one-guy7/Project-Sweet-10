# iPhone9,1 19H422 generic ApplePMGR GOT and stub analysis

## Scope and inputs

This note records user-supplied, read-only AArch64 disassembly of the
correctly mapped generic ApplePMGR executable segment and its stub section
from the target iPhone9,1 / D10AP 19H422 KernelCache.

Verified source KernelCache:
- Size: 44,924,928 bytes
- SHA-256: 7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee
- Darwin 21.6.0 / XNU 8020.241.44~1
- RELEASE_ARM64_T8010

The corrected executable VM range is 0xfffffff0065b6000–0xfffffff0065eaa4b,
size 0x34a4c. The user independently mapped its start, end of text, start
of stubs, and final byte into __PLK_TEXT_EXEC. The prior 0x00f4f280
extraction remains invalid and is not used here.

The user supplied the first 64 bytes and first 100 lines of the corrected
code dump and its displayed stub disassembly. The user later supplied the
whole-file sizes and SHA-256 identities for both the corrected executable
dump and the GOT dump; see the GOT resolution addendum below.

## Stub format and GOT slot mapping

The displayed stubs use the same three-instruction pattern:

1. ADRP x16, page
2. LDR x16, [x16, #offset]
3. BR x16

This is an indirect branch through an eight-byte pointer slot in generic
ApplePMGR's __DATA_CONST.__got region. The load-command map reports __got
at VM 0xfffffff006f18e80, size 0x400.

The calls in the first 100 code lines resolve to these GOT slot addresses:

| Caller instruction | Stub target | GOT slot VM | Offset within __got |
|---|---|---|---:|
| 0xfffffff0065b6020 | 0xfffffff0065ea680 | 0xfffffff006f18f28 | 0xa8 |
| 0xfffffff0065b6038 | 0xfffffff0065ea68c | 0xfffffff006f18f30 | 0xb0 |
| 0xfffffff0065b6060 | 0xfffffff0065ea860 | 0xfffffff006f19088 | 0x208 |
| 0xfffffff0065b6118 | 0xfffffff0065ea980 | 0xfffffff006f191f8 | 0x378 |
| 0xfffffff0065b612c | 0xfffffff0065ea980 | 0xfffffff006f191f8 | 0x378 |
| 0xfffffff0065b6140 | 0xfffffff0065ea980 | 0xfffffff006f191f8 | 0x378 |

The first routine separately loads a pointer from 0xfffffff006f19080,
which is offset 0x200 within __got.

The user mapped these additional data addresses into the outer KernelCache:

| VM address | Outer KernelCache offset | Segment |
|---|---:|---|
| 0xfffffff006f19080 | 0x025a5080 | __PLK_DATA_CONST |
| 0xfffffff006f192d0 | 0x025a52d0 | __PLK_DATA_CONST |
| 0xfffffff006f1c020 | 0x025a8020 | __PLK_DATA_CONST |

The resolved GOT pointer values and their target symbols/sections are now
recorded in the GOT resolution addendum below. The 0x200 entry points into
__DATA.__common; its exact object/symbol identity remains unresolved.

## First routine: ApplePMGR metaclass-initialization candidate

At 0xfffffff0065b6000, the routine prepares these arguments:

- x0: incoming object pointer (this under the AArch64 C++ member-function convention)
- x1: pointer to the string ApplePMGR, confirmed by the user's header
  hexdump at prelink-header offset 0x1382
- x2: pointer loaded from GOT slot 0xfffffff006f19080
- w3: immediate 0x34e98
- call through stub 0xfffffff0065ea680, whose GOT slot is 0xfffffff006f18f28

It then stores pointer 0xfffffff006f1c020 through [x0].

This argument shape is a strong pattern match for an OSMetaClass constructor
call. Apple's public XNU source declares the constructor as:

    OSMetaClass(const char *inClassName, const OSMetaClass *inSuperClass, unsigned int inClassSize)

Under AArch64, those three arguments follow the object pointer in x0,
matching the observed x1, x2, and w3 setup. Public XNU source also explains
that metaclass constructors participate in C++ initialization and class
registration for kernel extensions. See:

https://github.com/apple/darwin-xnu/blob/main/libkern/c%2B%2B/OSMetaClass.cpp

The leading interpretation is therefore an ApplePMGR metaclass initializer,
with 0x34e98 as a candidate class-size argument and 0xfffffff006f19080 as a
candidate superclass metaclass pointer. The post-call store of
0xfffffff006f1c020 is consistent with installing a vtable pointer into
the metaclass object.

The GOT value at 0xfffffff006f18f28 resolves to
__ZN11OSMetaClassC2EPKcPKS_j, confirming the OSMetaClass constructor call.
The pointer passed in x2 remains an unidentified __DATA.__common object,
so its superclass identity is unresolved. Public XNU main is structural
corroboration, not proof of the exact private 19H422 implementation. This
routine has not been proven to implement ApplePMGRFunctionEnableCPUCore.

## Second routine: ApplePMGR object-initialization candidate

A second routine begins at 0xfffffff0065b603c. The supplied excerpt shows it:

- preserving the incoming object pointer in x19
- making a call through stub 0xfffffff0065ea860, GOT slot 0xfffffff006f19088
- storing 0xfffffff006f192d0 through [x0]
- writing the value 4 at object offset 232
- zeroing and initializing object fields
- copying fixed-size regions from prelink text / data-constant addresses
- making several calls through stub 0xfffffff0065ea980, GOT slot
  0xfffffff006f191f8, with destination/source/length-shaped arguments

The pointer 0xfffffff006f192d0 is inside generic PMGR's
__DATA_CONST.__const region. Its placement and the store at object offset
zero are consistent with a vtable-like pointer. GOT resolution now confirms
that the call through slot 0x208 targets IOPMGR::IOPMGR and the repeated
three-argument calls through slot 0x378 target _memmove. The caller's
receiver pointer still needs inspection before assigning a base-subobject
versus embedded/member-object layout.

No exact ApplePMGR method name is assigned, and this routine has not been
shown to be a CPU-start method.

## What this establishes about CPU-start research

The code and stubs establish that:

- The generic PMGR executable contains ordinary AArch64 code, and calls
  in the excerpt pass through an embedded GOT/stub dispatch scheme.
- The first code sequence uses the literal class name ApplePMGR and an
  argument pattern matching public OSMetaClass construction.
- The same generic image contains the previously recorded
  ApplePMGRFunctionEnableCPUCore, cluster-control, and CPU-idle strings.

They do not establish that the metaclass function is the CPU-core-enable
callback, that the GOT dispatch target implements XNU IOPMGR::enableCPUCore,
that the concrete target PMGR releases a secondary CPU from reset, or that
XNU 8796 is ABI-compatible with this private 19H422 driver.

## GOT follow-up status

The GOT dump, five pointer reads, address mappings, and corrected
executable-dump identity are complete. Their values and symbol resolutions
are recorded in the GOT resolution addendum below. Both binary artifacts
remain local to the user's Ubuntu environment and are not committed.

## Milestone status and limits

- M1: static hardware/KEXT inventory complete.
- M2: exact 20H392 source provenance and reproducible target-compatible
  XNU baseline remain unresolved.
- M4: this narrows the PMGR metadata and dispatch path, but secondary-core
  release remains unproven.
- M7: SpringBoard not started.

All evidence above is host-side static inspection of the target-native
19H422 KernelCache. No Apple binary is committed, no binary is executed,
and no device, firmware, partition, or boot state is accessed or changed.
The physical iPhone 7 remains on iOS 12.1.4.

## GOT resolution addendum (2026-11-22)

This addendum supersedes the earlier statements above that the GOT pointer
contents and corrected executable-dump identity were still pending. The
user supplied both local artifact identities and the disassembly/address
mapping results below.

### Local artifact identities

| Artifact | Size | SHA-256 |
|---|---:|---|
| Correct ApplePMGR executable segment | 215,628 bytes | `fd5ca1551e1019e6dd979f245d34eb60802f607c1802fcf7044dac3c556dbd3a` |
| Generic ApplePMGR GOT dump | 1,024 bytes | `dfb327ae28453ef489e5da46bc073726e65696cc9e588e8fd4caf1320f1d4d75` |

Both binary artifacts remain local to the user's Ubuntu environment.

### Resolved GOT values

**Symbol-cache qualification:** the supplied disassembly output reports that
`ipsw` loaded 5,647 symbols from the local
`kernelcache.release.iPhone9,1_3.a2s` cache file. The labels below are
therefore symbol-cache labels assigned to target addresses; they are not
evidence that the stripped KernelCache itself contains a populated native
symbol table. The exact provenance/build match of that `.a2s` file should
be checked separately before treating these labels as final symbol
provenance. The addresses, section mappings, raw GOT values, and instruction
bytes remain independently useful evidence even if a label later changes.

| GOT offset | Pointer value | Disassembler symbol / section | Outer KernelCache offset |
|---:|---|---|---:|
| `0xa8` | `0xfffffff0076dde78` | `__ZN11OSMetaClassC2EPKcPKS_j` (`OSMetaClass` constructor), `__TEXT_EXEC.__text` | `0x6d9e78` |
| `0xb0` | `0xfffffff0076de600` | `__ZN11OSMetaClassD2Ev` (`OSMetaClass` destructor), `__TEXT_EXEC.__text` | `0x6da600` |
| `0x200` | `0xfffffff00789bee8` | `__DATA.__common`; exact object/symbol identity unresolved | `0x897ee8` |
| `0x208` | `0xfffffff00776326c` | `__ZN6IOPMGRC2EPK11OSMetaClass` (`IOPMGR` constructor), `__TEXT_EXEC.__text` | `0x75f26c` |
| `0x378` | `0xfffffff007180890` | `_memmove`, `__TEXT_EXEC.__hib_text` | `0x17c890` |

### Updated interpretation

1. **ApplePMGR metaclass initialization is now symbol-confirmed.** The
   first ApplePMGR routine calls the target at GOT slot `0xa8`, which is
   `OSMetaClass::OSMetaClass`. The caller supplies the `ApplePMGR` string
   in x1, the pointer from GOT slot `0x200` in x2, and `0x34e98` in w3.
   This matches the constructor's class-name, superclass-pointer, and
   class-size argument positions. The pointer value
   `0xfffffff00789bee8` is in `__DATA.__common`, but its exact symbol and
   superclass identity have not been established. The post-call store of
   `0xfffffff006f1c020` remains consistent with a metaclass vtable write.

2. **The ApplePMGR object-initialization routine calls an IOPMGR
   constructor.** Its call through GOT slot `0x208` resolves to
   `IOPMGR::IOPMGR(const OSMetaClass *)`. The supplied target disassembly
   writes 1 at object offset 8, stores the IOPMGR vtable pointer at object
   offset 0, and returns. The caller's x0 value at
   `0xfffffff0065b6060` must still be inspected before deciding whether
   this receiver is a base subobject or an embedded/member object.

3. **The fixed-size copy calls are confirmed as `_memmove`.** The three
   calls through GOT slot `0x378` resolve to `_memmove` at
   `0xfffffff007180890`, in `__TEXT_EXEC.__hib_text`.

4. The `0xb0` entry resolves to `OSMetaClass::~OSMetaClass()`, but the
   supplied caller excerpt does not identify a call site using this stub.
   Do not assign it to a specific cleanup path yet.

### What this does not establish

The GOT results identify constructor/destructor/copy-helper targets. They
do not identify `ApplePMGRFunctionEnableCPUCore`, prove that the concrete
T8010 PMGR implementation fulfills XNU's `IOPMGR::enableCPUCore`
contract, demonstrate secondary-CPU reset release, or prove ABI
compatibility between the 19H422 target kernel and the 20H392 donor.

### Next host-side check

Inspect the receiver setup immediately before the IOPMGR-constructor call
at `0xfffffff0065b6060`:

~~~sh
ipsw macho disass "$KC" --vaddr 0xfffffff0065b603c --count 100
~~~

Record the x0 value or pointer arithmetic immediately before the call.
Do not infer base-class layout from the constructor symbol alone.

All evidence remains host-side static inspection. No Apple binary was added
to the repository, and the physical iPhone 7 remains on iOS 12.1.4.
