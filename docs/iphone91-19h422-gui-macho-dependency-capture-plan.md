# iPhone9,1 GUI-chain Mach-O dependency capture plan

## Purpose

The target 19H422 mounted filesystem now has regular-file path-presence
evidence for the selected GUI/platform LaunchDaemon executables. The next
bounded static comparison is to inspect the target-native Mach-O load commands
for the three central GUI-chain executables:

- `backboardd`
- `runningboardd`
- `SpringBoard`

The donor 20H392 equivalents were previously inspected with
`llvm-objdump --macho --dylibs-used` and
`llvm-objdump --macho --rpaths`. The documented donor counts are 46, 6, and
4 direct linked-dylib rows respectively. Those donor results must not be
substituted for target output.

## Target paths established by the path-presence report

The supplied 19H422 report found all three files as regular files under the
mount root's single `root/` wrapper:

| Executable | Relative path beneath `/home/hey/19H422-full-fs-mount` |
|---|---|
| `backboardd` | `root/usr/libexec/backboardd` |
| `runningboardd` | `root/usr/libexec/runningboardd` |
| `SpringBoard` | `root/System/Library/CoreServices/SpringBoard.app/SpringBoard` |

The report only established path/type presence. It did not inspect these
files' contents.

## Read-only host capture

Run from Ubuntu on the host where the 19H422 filesystem is already mounted.
This only asks `file` and `llvm-objdump` to read the three mounted files'
Mach-O metadata. It does not execute the files or change the mounted image.

```bash
set -euo pipefail

ROOT="$HOME/19H422-full-fs-mount"
OUT="$HOME/sweet10-19H422-gui-macho-dependencies.txt"

command -v file
command -v llvm-objdump
llvm-objdump --version

{
  for REL in \
    "root/usr/libexec/backboardd" \
    "root/usr/libexec/runningboardd" \
    "root/System/Library/CoreServices/SpringBoard.app/SpringBoard"
  do
    PATH_TO_FILE="$ROOT/$REL"
    printf '\n===== %s =====\n' "$REL"

    if [ ! -f "$PATH_TO_FILE" ]; then
      printf 'NOT A REGULAR FILE: %s\n' "$PATH_TO_FILE"
      continue
    fi

    file "$PATH_TO_FILE"
    llvm-objdump --macho --dylibs-used "$PATH_TO_FILE"
    llvm-objdump --macho --rpaths "$PATH_TO_FILE"
  done
} > "$OUT" 2>&1

printf 'Saved report: %s\n' "$OUT"
```

If a command reports an unsupported option or cannot parse a file, preserve
the exact error in the report. Do not substitute another executable version
without recording its version. Do not run any of the inspected files.

## What to retain

For each executable, preserve:

- the `file` identification line (format and architecture, if reported);
- every direct `LC_LOAD_DYLIB`, `LC_LOAD_WEAK_DYLIB`,
  `LC_REEXPORT_DYLIB`, or other dylib load-command row as printed;
- all `LC_RPATH` rows;
- command exit status and any stderr text.

Do not include binary contents, private identifiers, or unrelated filesystem
data in the report.

## Comparison rules

After the target output is available, compare it against the already documented
20H392 donor output by **install name and load-command kind**, not merely by
basename. Keep regular, weak, re-export, and upward dependency kinds separate.
Compare `LC_RPATH` entries independently.

Then cross-reference each target install name against the 19H422 target
dyld-cache image inventory and, where relevant, the separate mounted
SystemOS/Cryptex inventory. A name present in the cache image list is not
automatically a resolved runtime dependency; cache membership and a loader's
direct dependency edges are different evidence types.

## Evidence boundary

This is static host-side metadata only. It does not validate code signatures,
entitlements, ABI compatibility, transitive dependency closure, actual dyld
resolution, launchd registration, process launch, IOKit provider attachment,
hardware behavior, or SpringBoard readiness. The 19H422 image is an iOS 15.8.8
stock iPhone 7 reference, while 20H392 is an iOS 16.7.16 iPhone X donor.
Neither static output establishes that the donor userland is compatible with
iPhone9,1.

The physical iPhone 7 remains on iOS 12.1.4. No device or boot operation is
part of this plan.
