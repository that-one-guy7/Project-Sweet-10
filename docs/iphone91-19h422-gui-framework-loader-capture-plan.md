# iPhone9,1 19H422 SpringBoard / RunningBoard framework loader capture plan

## Purpose

The target iPhone 7 19H422 cache image-list cross-reference confirms that the
three GUI-chain executables' 44 unique regular direct dependency paths all
appear in the target `dylibs` image array. The next bounded static step is to
inspect the target PrebuiltLoaderSet records for three higher-level frameworks:

- `/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard`
- `/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard`
- `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices`

Their exact target cache image-list records are:

| Framework | Image-list index | Version | UUID |
|---|---:|---|---|
| SpringBoard | 454 | `4251.53.0.0.0` | `245B5F25-7DE1-329C-9107-87B37883CFB9` |
| RunningBoard | 553 | `618.100.42.0.0` | `68246786-1E83-3892-907F-123EE1F09C68` |
| RunningBoardServices | 62 | `618.100.42.0.0` | `616B8ECB-90ED-38C5-9988-24AD07AE0CE9` |

The image-list index is not a PrebuiltLoader reference index. Keep these
identities separate when recording query output.

## Host-side query

Use the existing target cache at
`$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`.
Use the same standalone Linux `ipsw` version 3.1.749 already recorded in the
target BackBoard loader audit. Save full stdout and stderr separately and
record each exit status:

```bash
set -uo pipefail

TARGET_CACHE="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
OUT="$HOME/19H422-gui-framework-loader-results"
mkdir -p "$OUT"

for IMAGE in \
  /System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard \
  /System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard \
  /System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices
do
  NAME="$(basename "$IMAGE")"
  if ipsw dyld image "$TARGET_CACHE" "$IMAGE" \
      > "$OUT/$NAME.txt" 2> "$OUT/$NAME.err"; then
    STATUS=0
  else
    STATUS=$?
  fi
  printf '%s\t%s\n' "$IMAGE" "$STATUS" >> "$OUT/status.tsv"
done

printf 'Saved results in %s\n' "$OUT"
```

Do not execute or extract these images. The command queries the mounted cache
metadata only and writes text output under the user's home directory.

## What to retain

For each query preserve the exact requested image path, ipsw version,
exit status, stderr, PrebuiltLoader reference index, flags, VM size,
region count, every `Dependents` row in source order and raw kind, and
every `BindTargets` row separately. Do not infer an empty BindTargets list
when no section is printed.

## Comparison rules

Compare the three new records with the previously captured donor 20H392
loader records when available. Keep the following evidence categories
separate:

1. Executable direct Mach-O load commands.
2. Framework PrebuiltLoaderSet dependency rows.
3. The target cache `dylibs` image-list entries.
4. Standalone mounted filesystem paths.
5. Runtime behavior (not part of this audit).

Preserve regular, weak-link, re-export, upward, and unknown dependency kinds
as distinct edge types. A framework appearing in the image list does not
prove dyld resolves it for a process or that its own dependencies are
satisfied.

## Evidence boundary

This is host-side static metadata only. It does not establish ABI
compatibility, code-signing validity, runtime dependency resolution,
launchd registration, process launch, IOKit provider attachment, hardware
operation, kernel compatibility, or SpringBoard readiness. The target cache
belongs to stock iOS 15.8.8 build 19H422 on iPhone9,1; it is not an iOS 16
target build.

The physical iPhone 7 remains on iOS 12.1.4. No device or boot operation is
part of this plan.
