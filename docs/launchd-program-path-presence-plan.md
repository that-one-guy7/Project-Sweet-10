# Selected LaunchDaemon Program-path presence inventory

## Purpose

The launchd inventories identify configured jobs and their Program paths. Before treating a selected GUI-chain job as a filesystem dependency, record whether its declared Program path is present in the already-extracted target/donor filesystem roots.

This is a bounded host-side metadata check. It does not run daemons or inspect executable contents.

## Inputs and selected jobs

- Target reference: iPhone9,1 / D10AP / A10-T8010, iOS 15.8.8 build 19H422.
- Donor reference: iPhone10,3 / D22AP / A11-T8015, iOS 16.7.16 build 20H392.
- Inputs: the saved JSON outputs from `tools/inspect_launchd_jobs.py`, plus the already-mounted filesystem roots.

By default the tool checks these nine selected job labels:

- `com.apple.backboardd`
- `com.apple.runningboardd`
- `com.apple.SpringBoard`
- `com.apple.configd`
- `com.apple.notifyd`
- `com.apple.mediaserverd`
- `com.apple.wifid`
- `com.apple.bluetoothd`
- `com.apple.mobileactivationd`

The two supplied launchd JSON inventories contain all nine selected labels. Repeated job labels, if any, are retained as separate records.

## Method

For each selected absolute Program path, the script checks the exact path under every supplied filesystem root. It additionally checks up to two repeated leading `root/` wrapper components by default because the user's extracted IPSW mount directories have different wrapper depths. The wrapper-depth checks are explicit in the JSON report; the script does not recursively search the filesystem.

Each path component is inspected with `lstat`. A symlink is recorded and is not followed. The script never opens, hashes, reads, or executes the target Program file. It records missing paths, symlink components, directories, non-regular file types, and permission/stat errors distinctly.

A `regular-file-found` result means only that a regular filesystem object exists at one checked path. It does not establish that the file is Mach-O, signed, entitled, loadable, ABI-compatible, or able to launch. `not-found-under-scanned-roots` is limited to the exact roots and wrapper depths provided; it is not a global absence claim for other volumes, Cryptexes, or runtime content.

## Run on the host

First locate the previously generated launchd JSON files if they are not already in the project directory:

```sh
find "$HOME" -type f \(
  -name '19H422-launchd-inventory.json' -o
  -name 'launchd-inventory.json' -o
  -name 'launchd-inventory(1).json'
\) -print
```

Then run from the Project-Sweet-10 repository root, substituting the two exact JSON file paths found above:

```sh
OUT="$HOME/sweet10-launchd-program-paths"
mkdir -p "$OUT"

python3 tools/inspect_launchd_program_paths.py \
  --target-launchd "/path/to/19H422-launchd-inventory.json" \
  --donor-launchd "/path/to/launchd-inventory.json" \
  --target-root "/home/hey/19H422-full-fs-mount" \
  --donor-root "/home/hey/20H392/mnt" \
  --donor-root "/home/hey/20H392/systemos-mnt" \
  --wrapper-depth 2 \
  > "$OUT/launchd-program-path-presence.json"

echo "Report: $OUT/launchd-program-path-presence.json"
```

Do not use `sudo` for this check. If the host account cannot inspect a path, the report records a permission result rather than changing filesystem permissions. The output is written under the home directory; the mounted source roots are not modified.

Upload `launchd-program-path-presence.json` for review. The actual target/donor filesystem path-presence result remains pending until that report is supplied.

## Validation

Ten synthetic tests cover direct files, bounded root wrappers, final and intermediate symlinks, missing paths, non-directory components, invalid Program paths, duplicate job labels, schema validation, status aggregation, and wrapper-depth bounds. CI runs the full host-side test suite.

## Evidence boundary

This is static filesystem metadata only. It does not establish launchd registration, process creation, daemon startup, service availability, runtime compatibility, kernel behavior, boot, or SpringBoard readiness. M6 remains in progress; M7/SpringBoard has not started. The physical iPhone 7 remains on iOS 12.1.4.
