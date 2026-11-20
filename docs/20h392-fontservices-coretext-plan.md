# 20H392 FontServices and CoreText dependency inspection plan

## Scope

This is a read-only host-side inspection plan for the iPhone X iOS 16.7.16
(20H392) donor SystemOS shared cache. It follows four font-chain images named
by the user's successful loader queries:

- `libFontParser.dylib`
- `FontServices`
- `libGSFontCache.dylib`
- `CoreText`

The actual Project Sweet-10 target remains iPhone 7 `iPhone9,1` / D10AP /
A10-T8010. Donor cache metadata is not target firmware and does not establish
iPhone9,1 compatibility.

## Why these images

The observed donor graph has:

- CoreGraphics → libFontParser (regular)
- GraphicsServices → libGSFont (weak-link + re-export; raw kind 3)
- libGSFont → CoreText (weak-link + re-export; raw kind 3)
- libGSFont → FontServices (weak-link + re-export; raw kind 3)
- libGSFont → libGSFontCache (weak-link + re-export; raw kind 3)

This bounded set follows only those direct edges. Preserve the weak-link and
re-export flags. Do not treat these rows as ordinary strong dependencies.

## Commands on the analysis PC

Use the already mounted, read-only SystemOS Cryptex cache:

```sh
CACHE="$HOME/20H392/systemos-mnt/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
OUT="$HOME/20H392/framework-closures"
mkdir -p "$OUT"

for IMAGE in \
  /System/Library/PrivateFrameworks/FontServices.framework/libFontParser.dylib \
  /System/Library/PrivateFrameworks/FontServices.framework/FontServices \
  /System/Library/PrivateFrameworks/FontServices.framework/libGSFontCache.dylib \
  /System/Library/Frameworks/CoreText.framework/CoreText
do
  NAME=$(basename "$IMAGE")
  printf '\n=== Inspecting %s ===\n' "$NAME"

  ipsw dyld image "$CACHE" "$IMAGE" \
    > "$OUT/$NAME.txt" 2> "$OUT/$NAME.err"
  STATUS=$?

  printf 'Exit status: %s\n' "$STATUS"
  if [ -s "$OUT/$NAME.err" ]; then
    cat "$OUT/$NAME.err"
  fi
  if [ -s "$OUT/$NAME.txt" ]; then
    sed -n '/^Dependents:/,/^BindTargets:/p' "$OUT/$NAME.txt"
  fi
done
```

Keep the full text and stderr files locally. A missing loader or nonzero exit
is a result to report, not a reason to substitute another file. If two
requested images share a basename, save each under a distinct name manually
rather than overwriting a previous output file.

## Record rules

- Preserve the exact output kind; record raw kind 3 as weak-link + re-export
  using the pinned source mapping documented in
  `20h392-platform-framework-dependency-results.md`.
- Keep bind targets separate from dependency edges.
- Preserve per-image printed ordering in the evidence record.
- Deduplicate only in a separate derived graph view.
- A root-filesystem-only miss is not proof of absence from the complete donor
  system; the root filesystem and SystemOS Cryptex are separate volumes.
- Do not commit the cache, proprietary binaries, IPSW/DMG files, private
  identifiers, or raw device-specific machine data.

## What this inspection can and cannot answer

These queries extend the static iPhone X donor font dependency graph. They
cannot prove:

- that the font libraries are loaded by a specific GUI process at runtime;
- that the font libraries or CoreText work on an iPhone9,1 device;
- that the donor's graphics, GPU, display, or framebuffer stack is available
  on A10/T8010;
- that SpringBoard starts or remains stable.

After these four records are reviewed, stop expanding generic framework
dependencies and prioritize matching concrete userland service, IOKit
personality, and display/HID requirements against verified iPhone9,1
stock-firmware and public XNU evidence.

M6 remains in progress; M7 has not started.

## References

- [20H392 IOKit and font-framework dependency results](20h392-iokit-font-framework-dependency-results.md)
- [20H392 service and graphics dependency results](20h392-platform-framework-dependency-results.md)
- [Apple dyld LinkedDylibAttributes](https://github.com/apple-oss-distributions/dyld/blob/fd8d0c4d52320ebf64db34f3cb280310d905c5ae/mach_o/UnsafeHeader.h)
- [ipsw 3.1.749 dependent-kind formatter](https://github.com/blacktop/ipsw/blob/a7dfadbcaca8375b424c12a68dae40767e5e07c1/pkg/dyld/prebuilt_types.go)
