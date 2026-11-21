# 20H392 donor / 19H422 target MultitouchSupport export audit plan

## Scope and image identity

This plan defines a read-only host-side comparison of the dyld export metadata for the same cached image path in two existing shared caches:

```text
/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport
```

- Target: iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8 build `19H422`.
- Donor: iPhone X `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16 build `20H392`.
- Target cache image-list record: index 1249, version `5100.27.0.0.0`, UUID `0EAF98B3-8D31-3A90-A578-1787797B9467`.
- Donor cache image-list record: index 1648, version `6140.3.0.0.0`, UUID `1B6ABB86-B8A9-3941-A66A-EC9715F6B034`.

The physical iPhone 7 remains on iOS 12.1.4. This comparison uses only the already-mounted cache files on the host. It does not contact, boot, modify, update, restore, or otherwise interact with a device.

## Pinned parser behavior

The project uses the recorded `ipsw 3.1.749` parser source revision:

[`cmd/ipsw/cmd/dyld/dyld_macho.go` at pinned source commit](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/dyld/dyld_macho.go).

At that revision:

- The command syntax is `ipsw dyld macho <DSC> <DYLIB>`.
- `--symbols` enables the symbols report.
- The global verbose option `-V` additionally prints the `Dyld Exports` section when the parsed Mach-O has a non-empty `LC_DYLD_EXPORTS_TRIE`.
- The section is emitted from the parser's `m.DyldExports()` result. The command also prints symbol-table and bind information; the shell filter below displays only the export section.
- Do not use `--extract`; extraction is not needed for this metadata query.

This is a parser-output inspection, not an independent validation of export-trie bytes or a signature check.

### Optional broader text-stub cross-check

The same pinned source revision also provides
`ipsw dyld tbd <DSC> <DYLIB> --output <directory>`. It writes a
text-based stub that gathers external symbol-table entries, dyld export-trie
entries, Mach-O exports, re-export declarations, and Objective-C class/ivar
metadata when present. This is a broader interface summary than the focused
`Dyld Exports` section above and does not preserve the export-trie flags in
the same per-entry display. It may be used as a secondary cross-check, but
the primary comparison remains `dyld macho --symbols -V`.

Pinned implementation references:
- [dyld_tbd.go](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/cmd/ipsw/cmd/dyld/dyld_tbd.go)
- [dsc.go](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/internal/commands/dsc/dsc.go)
- [tbd.go](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/pkg/tbd/tbd.go)
- [template.go](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/pkg/tbd/template.go)


## Read-only cache locations

The existing cache paths recorded by this project are:

- Target: `$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`
- Donor: `$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`

## Exact host-side command

The following Bash command runs the pinned `ipsw` binary against both existing cache files, saves the complete parser logs separately, and prints only the `Dyld Exports` section. It does not use the extract option.

```bash
BIN="$(find "$HOME/ipsw-standalone" -type f -name ipsw -executable -print -quit)"

IMAGE="/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport"
TARGET="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
DONOR="$HOME/20H392/systemos-mnt/root/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"

TARGET_LOG="$HOME/19H422-MultitouchSupport-exports.txt"
DONOR_LOG="$HOME/20H392-MultitouchSupport-exports.txt"

if [ -z "$BIN" ] || [ ! -x "$BIN" ]; then
    echo "Could not locate the standalone ipsw executable."
elif [ ! -r "$TARGET" ] || [ ! -r "$DONOR" ]; then
    echo "One or both expected cache files are not readable."
else
    "$BIN" dyld macho "$TARGET" "$IMAGE" --symbols -V > "$TARGET_LOG" 2>&1
    TARGET_STATUS=$?

    "$BIN" dyld macho "$DONOR" "$IMAGE" --symbols -V > "$DONOR_LOG" 2>&1
    DONOR_STATUS=$?

    echo "Target parser exit code: $TARGET_STATUS"
    echo "Donor parser exit code: $DONOR_STATUS"

    for ITEM in "TARGET:$TARGET_LOG" "DONOR:$DONOR_LOG"; do
        LABEL="${ITEM%%:*}"
        FILE="${ITEM#*:}"

        echo
        echo "===== $LABEL EXPORTS ====="

        if grep -q '^Dyld Exports$' "$FILE"; then
            awk '
                /^Dyld Exports$/ { printing=1 }
                printing && NF==0 { exit }
                printing { print }
            ' "$FILE"
        else
            echo "No Dyld Exports section was printed."
            echo "Last parser output lines:"
            tail -n 12 "$FILE"
        fi
    done
fi

read -r -p "Press Enter to close..."
```

## What to record from the output

For each cache, record:

1. Whether the parser exited successfully and whether a `Dyld Exports` section appeared.
2. The number of parsed export entries.
3. Exported symbol names and their flags.
4. Re-export entries, including the referenced library/name where the parser resolves them.
5. Parser errors or unresolved re-export references.

Compare symbol names and export flags as the primary fields. Keep the reported addresses as source-specific reference data only: target and donor cache layouts and load addresses differ, so raw address equality is not a compatibility test. Keep exported symbols distinct from the separate symbol-table and dependent-loader records.

If the parser does not emit the section or reports an error, preserve that result as a parser/evidence limitation; do not interpret it as proof that the image exports no symbols.

## Interpretation limits

Matching export names would show only an overlapping exported-name surface. It would not establish matching implementations, calling conventions, structure layouts, ownership/lifetime rules, ABI compatibility, dependency resolution, successful plugin loading, IOKit provider attachment, touch-event delivery, or SpringBoard stability.

Different export names or flags would identify additional static differences, but would not by themselves explain a runtime failure. Do not substitute donor binaries or libraries into the target.

No cache file, binary, filesystem image, firmware file, or device state is modified or committed by this plan.
