#!/usr/bin/env python3
"""Create a privacy-conscious, read-only inventory of an extracted iOS launchd plist.

This script reads System/Library/xpc/launchd.plist below a supplied root.
It never executes jobs, reads their binaries, or modifies the source tree.
Environment variable values and full ProgramArguments are intentionally omitted.
"""
import argparse
import hashlib
import json
import plistlib
import sys
from pathlib import Path


PLIST_RELATIVE_PATH = Path("System/Library/xpc/launchd.plist")
FOCUS_TOKENS = (
    "backboardd",
    "springboard",
    "commcenter",
    "mediaserverd",
    "wifid",
    "bluetoothd",
    "mobileactivationd",
    "runningboardd",
    "launchservicesd",
    "setupassistant",
    "purplebuddy",
    "configd",
    "notifyd",
)
SCHEMA = "project-sweet-10.launchd-inventory.v1"


class InventoryError(Exception):
    """Raised when the supplied root does not contain a usable launchd plist."""


def _sorted_string_keys(value):
    if isinstance(value, dict):
        return sorted(key for key in value if isinstance(key, str))
    if isinstance(value, (list, tuple)):
        return sorted(item for item in value if isinstance(item, str))
    return []


def _optional_bool(value):
    return value if isinstance(value, bool) else None


def _keep_alive_summary(job):
    if "KeepAlive" not in job:
        return {"mode": "unspecified", "condition_keys": []}

    value = job["KeepAlive"]
    if isinstance(value, bool):
        return {"mode": "always" if value else "never", "condition_keys": []}
    if isinstance(value, dict):
        return {"mode": "conditions", "condition_keys": _sorted_string_keys(value)}
    if isinstance(value, (list, tuple)):
        return {"mode": "list", "condition_keys": []}
    return {"mode": "other", "condition_keys": []}


def _job_summary(launchd_key, job):
    label_value = job.get("Label")
    label = label_value if isinstance(label_value, str) else launchd_key

    arguments = job.get("ProgramArguments")
    if not isinstance(arguments, (list, tuple)):
        arguments = []
    argv0 = arguments[0] if arguments and isinstance(arguments[0], str) else None

    program_value = job.get("Program")
    program = program_value if isinstance(program_value, str) else argv0

    mach_services = _sorted_string_keys(job.get("MachServices"))
    sockets = _sorted_string_keys(job.get("Sockets"))
    env_names = _sorted_string_keys(job.get("EnvironmentVariables"))

    focus_text = (label + " " + (program or "")).lower()
    focus_tags = [token for token in FOCUS_TOKENS if token in focus_text]

    return {
        "launchd_key": launchd_key,
        "label": label,
        "program": program,
        "program_arguments_count": len(arguments),
        "mach_services": mach_services,
        "socket_names": sockets,
        "keep_alive": _keep_alive_summary(job),
        "run_at_load": _optional_bool(job.get("RunAtLoad")),
        "disabled": _optional_bool(job.get("Disabled")),
        "enable_transactions": _optional_bool(job.get("EnableTransactions")),
        "process_type": job.get("ProcessType") if isinstance(job.get("ProcessType"), str) else None,
        "posix_spawn_type": job.get("POSIXSpawnType") if isinstance(job.get("POSIXSpawnType"), str) else None,
        "user_name": job.get("UserName") if isinstance(job.get("UserName"), str) else None,
        "group_name": job.get("GroupName") if isinstance(job.get("GroupName"), str) else None,
        "limit_load_to_session_type": job.get("LimitLoadToSessionType")
        if isinstance(job.get("LimitLoadToSessionType"), (str, list))
        else None,
        "environment_variable_names": env_names,
        "focus_tags": focus_tags,
    }


def inspect_root(root):
    """Return a sanitized inventory from an extracted iOS root directory."""
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise InventoryError("root path is not a directory: {}".format(root))

    plist_path = root / PLIST_RELATIVE_PATH
    try:
        raw = plist_path.read_bytes()
    except OSError as exc:
        raise InventoryError(
            "cannot read {}: {}".format(PLIST_RELATIVE_PATH.as_posix(), exc)
        ) from exc

    try:
        plist = plistlib.loads(raw)
    except (plistlib.InvalidFileException, ValueError, TypeError) as exc:
        raise InventoryError("launchd plist is not a valid plist: {}".format(exc)) from exc

    if not isinstance(plist, dict):
        raise InventoryError("launchd plist root must be a dictionary")

    jobs = plist.get("LaunchDaemons")
    if not isinstance(jobs, dict):
        raise InventoryError("launchd plist has no LaunchDaemons dictionary")

    summaries = []
    for key, job in jobs.items():
        if not isinstance(key, str) or not isinstance(job, dict):
            raise InventoryError("LaunchDaemons contains a non-string key or non-dictionary job")
        summaries.append(_job_summary(key, job))

    summaries.sort(key=lambda item: (item["label"].lower(), item["launchd_key"].lower()))

    providers = {}
    for job in summaries:
        for service in job["mach_services"]:
            providers.setdefault(service, []).append(job["label"])

    provider_rows = [
        {"service": service, "provider_labels": sorted(set(labels))}
        for service, labels in sorted(providers.items())
    ]

    focus_rows = [
        {
            "label": job["label"],
            "program": job["program"],
            "matched_tags": job["focus_tags"],
            "mach_services": job["mach_services"],
        }
        for job in summaries
        if job["focus_tags"]
    ]

    return {
        "schema": SCHEMA,
        "source_plist": PLIST_RELATIVE_PATH.as_posix(),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "launch_daemon_count": len(summaries),
        "mach_service_name_count": len(provider_rows),
        "jobs": summaries,
        "mach_service_providers": provider_rows,
        "focus_service_matches": focus_rows,
        "scope_notes": [
            "This is a static plist inventory, not a runtime process or crash report.",
            "MachServices lists advertised providers; it does not reveal every client dependency.",
            "Environment variable values and full ProgramArguments are intentionally omitted.",
            "No program, daemon, script, or binary is executed and no source file is modified.",
            "This inventory covers LaunchDaemons in the central launchd plist only.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read-only inventory of LaunchDaemons in an extracted iOS root."
    )
    parser.add_argument(
        "root",
        help="path to an extracted or mounted iOS root filesystem (read-only access is sufficient)",
    )
    args = parser.parse_args(argv)

    try:
        report = inspect_root(args.root)
    except InventoryError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 1

    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
