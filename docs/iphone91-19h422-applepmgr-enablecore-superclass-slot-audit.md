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

## Wider executable-reference check

The user searched the corrected generic ApplePMGR executable dump for
page `0xfffffff0079e4000`; the command returned no matching lines.
This is a negative result limited to that one 215,628-byte executable
segment, not evidence that the metaclass object or its owning class is
absent. The initializer may be emitted in another prelinked component.

The next read-only check is to inspect the shared
`__PLK_TEXT_EXEC` segment from the hash-identified 19H422 KernelCache.
Its load-command range is file offset `0x00fd4000–0x02364000`,
VM address `0xfffffff005948000–0xfffffff006cd8000`, and size
`0x01390000` (20,512,768 bytes). IPSW's current
[macho dump command](https://blacktop.github.io/ipsw/docs/cli/ipsw/macho/dump/)
supports dumping a Mach-O virtual-address range to a local file.

```sh
ipsw macho dump "$KC" 0xfffffff005948000 \
  --size 20512768 \
  --output "$HOME/ApplePMGR.plk-text-exec.bin"

stat -c 'Size: %s bytes' "$HOME/ApplePMGR.plk-text-exec.bin"
sha256sum "$HOME/ApplePMGR.plk-text-exec.bin"

aarch64-linux-gnu-objdump -D -b binary -m aarch64 \
  --adjust-vma=0xfffffff005948000 \
  "$HOME/ApplePMGR.plk-text-exec.bin" |
  grep -B 8 -A 12 -i '0xfffffff0079e4000'
```

The expected dump size is 20,512,768 bytes. If any references appear,
inspect for an adjacent `ADD #0xdd0` or a load/store through the
computed address. A no-match result across this larger segment would
still not prove object absence; it would only narrow the direct-code-
reference search. Keep the extracted Apple binary local and uncommitted.

No runtime class hierarchy, callback implementation, D10AP function
instantiation, IOPMGR CPU-start override, secondary-core release, IRQ
behavior, iOS 16 compatibility, boot, or SpringBoard result is established
by this audit.

## Repository and device boundary

This is documentation of user-supplied static inspection output.
No Apple binary is committed, no binary is executed, and no device,
firmware, partition, or boot state is accessed or changed. The physical
iPhone 7 remains on iOS 12.1.4.
