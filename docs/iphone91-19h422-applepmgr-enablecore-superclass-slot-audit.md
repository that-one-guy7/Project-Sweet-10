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

**`0xfffffff0079e4dd0` is the `AppleARMFunction` metaclass storage and
is passed as the superclass-metaclass pointer to the
`ApplePMGRFunctionEnableCPUCore` metaclass constructor.**

The all-zero on-disk bytes do not identify the object, but the later
shared-prelink registration audit resolves its class identity: the
metaclass initializer for `AppleARMFunction` uses this exact address as
its destination storage (`x0`). See the confirmed registration evidence
below. Do not infer the identity from zero-filled file bytes alone.

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

## Shared prelink registrations and resolved class-name strings

The user confirmed local tool versions:

- IPSW `3.1.749`, build commit
  `a7dfadbcaca8375b424c12a68dae40767e5e07c1`
- GNU `aarch64-linux-gnu-objdump` / Binutils `2.42`

The broad shared `__PLK_TEXT_EXEC` disassembly previously aborted near
`0xfffffff0059928b0` with the
`get_sreg_qualifier_from_value` assertion. The signature matches
[Binutils PR 31595](https://sourceware.org/bugzilla/show_bug.cgi?id=31595);
a downstream patch specifically backported the fix to a Binutils 2.42
recipe ([2.42 backport](https://patchwork.yoctoproject.org/project/oe-core/patch/20240524201214.3858538-2-mark.hatle%40amd.com/)).
This is consistent with a disassembler bug, not evidence that the target
KernelCache is corrupt.

The user mapped both x1 string pointers to actual class names:

| String VA | File offset | String |
|---|---:|---|
| `0xfffffff0052ea1a4` | `0x9761a4` | `AppleARMFunctionSlowAdaptiveClocking` |
| `0xfffffff0052ea1fc` | `0x9761fc` | `AppleARMFunctionSlowAdaptiveClockingAggressor` |

Both map into `__PRELINK_TEXT.__text`. The local 256-byte string
window confirms the strings at offsets `0x24` and `0x7c` from
window base `0xfffffff0052ea180`.

The bounded disassembly of
`0xfffffff00598e060–0xfffffff00598e190` completed successfully.
Together with the supplied surrounding output, it confirms:

| Call-site VA | x1 class name | x2 | w3 class size | Call target |
|---|---|---|---:|---|
| `0xfffffff00598dd14` / `0xfffffff00598dde4` | `AppleARMFunctionSlowAdaptiveClocking` | `0xfffffff0079e4dd0` | `0x40` | `0xfffffff005993844` |
| `0xfffffff00598e07c` / `0xfffffff00598e14c` | `AppleARMFunctionSlowAdaptiveClockingAggressor` | `0xfffffff0079e4dd0` | `0x38` | `0xfffffff005993844` |

A further sequence at `0xfffffff00598e5a4` supplies static class
storage x0=`0xfffffff0079e57c0`, the
`AppleARMFunctionSlowAdaptiveClocking` name in x1,
`0xfffffff0079e4dd0` in x2, and class size `0x40`.

The two subclass registrations and the earlier
`ApplePMGRFunctionEnableCPUCore` registration all pass
`0xfffffff0079e4dd0` as x2, the superclass argument. The user then
located the exact `AppleARMFunction` class-name string and its own
metaclass initializer in the shared prelink text, resolving the pointer's
identity.

### Exact AppleARMFunction string locations

| String | KernelCache file offset | Virtual address | Section |
|---|---:|---:|---|
| `AppleARMFunction` | `0x96de3c` | `0xfffffff0052e1e3c` | `__PRELINK_TEXT.__text` |
| `site.AppleARMFunction` | `0x96de4d` | `0xfffffff0052e1e4d` | `__PRELINK_TEXT.__text` |

The user mapped both offsets with `ipsw macho o2a` against the
same hash-identified 19H422 KernelCache. The empty `.a2s` grep is
only a symbol-cache non-match; it does not negate the raw strings or
the disassembly evidence.

### AppleARMFunction metaclass initializer

The decisive sequence at
`0xfffffff005964fe4–0xfffffff005965004` is:

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

The address arithmetic gives x19 =
`0xfffffff0079e4dd0`; the ADRP/ADD pair gives x1 =
`0xfffffff0052e1e3c`, the exact `AppleARMFunction` string. The
sequence then passes x0=x19, class size `0x28`, and calls the
previously identified `OSMetaClass` constructor at
`0xfffffff005993844`. Under the constructor layout used in this
audit, x0 is the metaclass object being initialized, x1 is its class
name, x2 is its superclass metaclass, and w3 is its class size.

This directly ties `0xfffffff0079e4dd0` to the
`AppleARMFunction` metaclass storage. Two additional
constructor-shaped sequences at `0xfffffff0059642e8` and
`0xfffffff0059643b8` also use the exact class-name string and
class-size argument `0x28`, corroborating the same initializer family.

### Resolved subclass relationships

The previously documented registrations pass the now-identified
`AppleARMFunction` metaclass address as x2:

| Registered class | Call-site VA(s) | x2 superclass metadata | Class size |
|---|---|---|---:|
| `AppleARMFunctionSlowAdaptiveClocking` | `0xfffffff00598dd14` / `0xfffffff00598dde4` | `0xfffffff0079e4dd0` (`AppleARMFunction`) | `0x40` |
| `AppleARMFunctionSlowAdaptiveClockingAggressor` | `0xfffffff00598e07c` / `0xfffffff00598e14c` | `0xfffffff0079e4dd0` (`AppleARMFunction`) | `0x38` |
| `ApplePMGRFunctionEnableCPUCore` | `0xfffffff0065dae00` / `0xfffffff0065daed0` / `0xfffffff0065ddf04` | `0xfffffff0079e4dd0` (`AppleARMFunction`) | `0x38` |

**Conclusion:** static metaclass-construction evidence in the 19H422
KernelCache confirms that `ApplePMGRFunctionEnableCPUCore`,
`AppleARMFunctionSlowAdaptiveClocking`, and
`AppleARMFunctionSlowAdaptiveClockingAggressor` use
`AppleARMFunction` as their superclass.

This does not prove that `ApplePMGRFunctionEnableCPUCore` is instantiated
for D10AP, identify its `callFunction` callback, establish a concrete
`IOPMGR::enableCPUCore` override, or demonstrate secondary-core release,
IRQ delivery, device boot, iOS 16 compatibility, or SpringBoard. The
broad shared-segment disassembly remains partial under Binutils 2.42;
the specific supplied windows and references are the evidence recorded
here.

### Next static research question

The superclass identity is resolved. The next useful static question is
whether the `ApplePMGRFunctionEnableCPUCore` class has an identifiable
callback implementation and how its registration data refers to that
callback. Keep that analysis confined to local, read-only examination of
the hash-identified KernelCache; class registration alone does not
establish runtime behavior.


The bounded disassembly already completed successfully:

~~~sh
aarch64-linux-gnu-objdump -D -b binary -m aarch64 \
  --adjust-vma=0xfffffff005948000 \
  --start-address=0xfffffff00598e060 \
  --stop-address=0xfffffff00598e190 \
  "$HOME/ApplePMGR.plk-text-exec.bin"
~~~

Keep Apple binary artifacts local. The broad shared-segment disassembly
remains incomplete under Binutils 2.42.

No runtime class hierarchy, callback implementation, D10AP function
instantiation, IOPMGR CPU-start override, secondary-core release, IRQ
behavior, iOS 16 compatibility, boot, or SpringBoard result is established
by this audit.

## Repository and device boundary

This is documentation of user-supplied static inspection output.
No Apple binary is committed, no binary is executed, and no device,
firmware, partition, or boot state is accessed or changed. The physical
iPhone 7 remains on iOS 12.1.4.
