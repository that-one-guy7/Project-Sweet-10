# iPhone9,1 19H422 ApplePMGR EnableCPUCore superclass-slot audit

## Scope and source identity

This note records the user's host-side static inspection of the generic
`com.apple.driver.ApplePMGR` prelinked KEXT in the iPhone9,1 / D10AP
19H422 KernelCache. It follows the three metaclass-construction references
recorded in the [CPU-function string audit](iphone91-19h422-applepmgr-cpu-function-string-audit.md).

Target KernelCache identity:

- 19H422 / iOS 15.8.8
- Darwin 21.6.0 / XNU `8020.241.44~1`
- `RELEASE_ARM64_T8010`
- Size: 44,924,928 bytes
- SHA-256: `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`

The source KernelCache is the target iPhone 7 reference artifact. The
physical iPhone 7 remains on iOS 12.1.4; this work does not access or
change the device.

## GOT[0x158] value

The user supplied this read from the 1,024-byte generic ApplePMGR GOT dump:

```
xxd -e -g8 -c8 -s 0x158 -l 8 "$HOME/ApplePMGR.got.bin"

00000158: fffffff0079e4dd0
```

The raw 64-bit pointer is therefore `0xfffffff0079e4dd0`. The user
mapped it against the hash-identified target KernelCache:

```
ipsw macho a2o "$KC" 0xfffffff0079e4dd0

Offset dec=40439248 hex=0x2690dd0
section=__data segment=__PRELINK_DATA
```

The target KernelCache load-command output gives the containing segment:

| Property | Value |
|---|---|
| Segment | `__PRELINK_DATA` |
| Section | `__PRELINK_DATA.__data` |
| File range | `0x02690000–0x027e4000` |
| VM range | `0xfffffff0079e4000–0xfffffff007b38000` |
| Segment protections | `rw-/rw-` |
| Relocation display | `NoReLoc` |

The user then read 0x80 bytes from outer KernelCache file offset
`0x2690dd0`. All sixteen displayed 64-bit words were zero. This is
strictly an observation about the on-disk bytes in that range. The load
command identifies a writable `__data` section; the observation does not
establish a separate zero-fill section, the runtime value, or the identity
of the object.

## Constructor argument interpretation

The three previously documented AArch64 sequences construct the exact
string address for `ApplePMGRFunctionEnableCPUCore`, set class size
`0x38`, and call the resolved `OSMetaClass` constructor stub. In the
first two sequences, x2 is loaded through GOT VA
`0xfffffff006f18fd8`, which is offset `0x158` in the generic
ApplePMGR GOT dump.

Public XNU's constructor declaration is
`OSMetaClass(const char *inClassName, const OSMetaClass *inSuperClass, unsigned int inClassSize)`.
The x2 argument is therefore the superclass-metaclass argument under
that signature. Combined with the mapped GOT value, the strongest
supported statement is:

**`0xfffffff0079e4dd0` is the candidate superclass-metaclass pointer
passed to the `ApplePMGRFunctionEnableCPUCore` metaclass constructor.**

The class name represented by that pointer is not yet known. The all-zero
on-disk bytes do not identify it. Do not infer that its name is
`ApplePMGRFunction`, `IOPlatformFunction`, or another plausible base
class from naming conventions alone.

The third sequence separately passes x0 =
`0xfffffff007ae14c0`. The user mapped this address to file offset
`0x278d4c0`, also in `__PRELINK_DATA.__data`. No byte dump at that
second address was supplied, and it is not interchangeable with the
GOT[0x158] target.

## Unproductive lookup attempts and limits

The user searched the local .a2s text for `fffffff006f18000` and
`#0xfd8`; grep returned no matches. This does not negate the earlier
disassembly supplied from the corrected generic ApplePMGR executable
dump. It only records that those search strings were not found in that
particular .a2s text file.

The user also ran:

```sh
ipsw kernel cpp "$KC"
ipsw kernel cpp "$KC" --class ApplePMGRFunctionEnableCPUCore --inheritance
ipsw kernel cpp "$KC" --class ApplePMGRFunctionCPUIdle --inheritance
```

Each invocation printed `no classes discovered`. Accordingly, this
input did not yield a class list or inheritance chain through that
command. It does **not** prove those classes or their metaclass objects
are absent. The inspected upstream IPSW source at commit
`26b65938cf4c9479cb5627d2d479492a1dcdd13e` opens the KernelCache as
Mach-O, runs its C++ scanner, and emits the warning when no displayable
classes are returned:
[kernel_cpp.go](https://github.com/blacktop/ipsw/blob/26b65938cf4c9479cb5627d2d479492a1dcdd13e/cmd/ipsw/cmd/kernel/kernel_cpp.go).
The user's local IPSW version was not included, so this source reference
explains the inspected upstream implementation rather than proving the
exact local binary revision.

## Shared prelink cross-references and disassembler abort

The user successfully dumped the shared `__PLK_TEXT_EXEC` range
(file offsets `0x00fd4000–0x02364000`, VM range
`0xfffffff005948000–0xfffffff006cd8000`, size 20,512,768 bytes).
The AArch64 disassembly emitted useful lines but did not complete. GNU
`objdump` aborted near `0xfffffff0059928b0` with:

```
opcodes/aarch64-dis.c:251: get_sreg_qualifier_from_value:
Assertion `value <= 0x4 && aarch64_get_qualifier_standard_value (qualifier) == value' failed.
```

This exact assertion signature matches the AArch64 disassembler abort
reported as [Binutils bug 31595](https://sourceware.org/bugzilla/show_bug.cgi?id=31595).
The user's installed Binutils version was not included; the exact local
version and trigger are therefore unknown. Treat the shared-segment
disassembly as partial, not as a complete scan.

Before the abort, the user-supplied output contains several registration-
shaped sequences that set x2 to `0xfffffff0079e4dd0` and call
`0xfffffff005993844` with a class-name pointer in x1 and class size
in w3. Two examples:

- At `0xfffffff00598e07c`, x1 is constructed as
  `0xfffffff0052ea1fc`, x2 as `0xfffffff0079e4dd0`, w3 is
  `0x38`, then the code calls `0xfffffff005993844`.
- At `0xfffffff00598e14c`, the same class-name pointer, x2 value,
  class size, and call target are used.
- At `0xfffffff00598dd14` and `0xfffffff00598dde4`, x1 is
  `0xfffffff0052ea1a4`, x2 is `0xfffffff0079e4dd0`, and
  w3 is `0x40`.
- At `0xfffffff00598e5a4`, x0 is explicitly set to
  `0xfffffff0079e57c0`, x1 to `0xfffffff0052ea1a4`, and x2
  to `0xfffffff0079e4dd0`, with class size `0x40`.

The argument arrangement is consistent with further OSMetaClass-style
registrations. x1 is the class-name string of the class being registered;
x2 is the candidate superclass-metaclass pointer. The two class-name
strings have not been extracted, so these results do not yet identify
the class at `0xfffffff0079e4dd0`. They support its use as a common
parent metadata object by multiple registrations, including the
previously identified `ApplePMGRFunctionEnableCPUCore` registration.

### Next checks

Record local tool versions, map the two class-name string addresses, and
extract a small window containing both strings:

```sh
ipsw version
aarch64-linux-gnu-objdump --version

ipsw macho a2o "$KC" 0xfffffff0052ea1fc
ipsw macho a2o "$KC" 0xfffffff0052ea1a4

ipsw macho dump "$KC" 0xfffffff0052ea180 \
  --size 256 \
  --output "$HOME/ApplePMGR-classname-window.bin"

strings -a -t x -n 4 "$HOME/ApplePMGR-classname-window.bin"
```

For a bounded recheck of the two `0x598e...` sites, stay below the
known abort address:

```sh
aarch64-linux-gnu-objdump -D -b binary -m aarch64 \
  --adjust-vma=0xfffffff005948000 \
  --start-address=0xfffffff00598e060 \
  --stop-address=0xfffffff00598e190 \
  "$HOME/ApplePMGR.plk-text-exec.bin"
```

This short range is intended to avoid the recorded abort point; it does
not fix Binutils or make the full-segment disassembly complete. The
local Apple binary stays outside GitHub.

No runtime class hierarchy, callback implementation, D10AP function
instantiation, IOPMGR CPU-start override, secondary-core release, IRQ
behavior, iOS 16 compatibility, boot, or SpringBoard result is established
by this audit.

## Repository and device boundary

This is documentation of user-supplied static inspection output.
No Apple binary is committed, no binary is executed, and no device,
firmware, partition, or boot state is accessed or changed. The physical
iPhone 7 remains on iOS 12.1.4.
