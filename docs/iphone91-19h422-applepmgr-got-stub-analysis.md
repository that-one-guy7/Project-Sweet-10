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
code dump, plus the displayed stub disassembly. The corrected dump's
explicit whole-file stat size and SHA-256 were not included in that message,
so those artifact-identification fields remain pending.

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

These mappings establish locations, not the contents of the GOT entries.
The resolved pointer values at 0x6f18f28, 0x6f18f30, 0x6f19080,
0x6f19088, and 0x6f191f8 have not yet been supplied.

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

This is not a confirmed symbol identification. The target function pointer
stored in GOT slot 0xfffffff006f18f28 has not been read, and public XNU main
is a structural comparison, not proof of the exact private 19H422 target
implementation. This routine has not been proven to implement
ApplePMGRFunctionEnableCPUCore.

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
zero are consistent with a vtable-like pointer. The repeated three-argument
calls resemble copy-helper calls, but the imported function is not yet known.

This routine is an object-initialization candidate, but no exact C++ method
name is assigned. It is not established as ApplePMGR::initDriver,
ApplePMGR::enableCluster, or a CPU-start method.

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

## Next host-side check: read the GOT contents

First map the start and last byte of the GOT against the outer KernelCache:

~~~sh
ipsw macho a2o "$KC" 0xfffffff006f18e80
ipsw macho a2o "$KC" 0xfffffff006f1927f
~~~

If both map into __PLK_DATA_CONST as expected, dump the 1,024-byte GOT
region by virtual address and inspect the five relevant entries:

~~~sh
ipsw macho dump "$KC" 0xfffffff006f18e80 --size 1024 \
  --output "$HOME/ApplePMGR.got.bin"

stat -c 'Size: %s bytes' "$HOME/ApplePMGR.got.bin"
sha256sum "$HOME/ApplePMGR.got.bin"

# GOT-relative offsets: 0xa8, 0xb0, 0x200, 0x208, and 0x378.
xxd -e -g8 -c8 "$HOME/ApplePMGR.got.bin" |
  grep -E '^000000a8:|^000000b0:|^00000200:|^00000208:|^00000378:'
~~~

Keep this binary local; do not add it to GitHub. If pointer values are
kernel virtual addresses, map each back into the same KernelCache with
ipsw macho a2o. If they are zero, relative, or otherwise encoded, record
the raw value first rather than guessing its meaning.

Also capture the corrected executable dump's size and SHA-256. The
supplied disassembly is useful, but the explicit whole-file identity
was omitted.

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