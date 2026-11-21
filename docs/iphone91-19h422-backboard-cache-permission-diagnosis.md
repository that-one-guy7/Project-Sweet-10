# iPhone9,1 / 19H422 BackBoard loader query: permission diagnosis

## Finding

The first four target-side loader queries did not reach image lookup. The combined
report supplied on 2026-11-20 shows exit status 1 for every requested framework
and the identical error:

```text
open /home/hey/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64: permission denied
```

This is a host filesystem access failure on the main dyld shared-cache file.
It is not evidence that any of the four frameworks is absent, and it does not
indicate a framework-name or loader-record mismatch. No target loader rows were
captured; the four stdout files are empty.

## Bounded next diagnostic

Do not rerun the four queries yet. First collect the mount/path permissions and
tool version, without changing permissions or the mounted IPSW:

```sh
TARGET_CACHE="$HOME/19H422-full-fs-mount/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
namei -l "$TARGET_CACHE"
ls -ld "$HOME/19H422-full-fs-mount" "$HOME/19H422-full-fs-mount/root" \
  "$(dirname "$TARGET_CACHE")"
ls -l "$TARGET_CACHE"
ipsw version
```

Provide the complete output. This will identify which directory or file denies
the current user access and preserve the exact ipsw version used for the audit.

Do not use recursive chmod/chown on the mounted IPSW tree, do not remount it
read-write, and do not modify or rename any dyld cache component. The physical
iPhone 7 remains on iOS 12.1.4. This work is limited to read-only host-side
inspection; it does not connect to, boot, or alter the phone.

## Status and evidence boundary

- Four requested image queries: failed before cache parsing (exit status 1).
- Target PrebuiltLoaderSet records collected by this attempt: zero.
- Framework presence/absence conclusions: none.
- M6 remains in progress; M7/SpringBoard has not started.

After the path permissions are understood, choose a non-destructive way to make
the cache readable to the unprivileged inspection process, then rerun the
existing four-image collection plan and preserve each command's stdout, stderr,
and exit status. Do not infer compatibility or runtime behavior from static
loader metadata alone.
