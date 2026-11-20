#!/usr/bin/env python3
"""Capture selected dyld PrebuiltLoader records from a mounted shared cache.

This is a host-side metadata collector. It invokes the local ipsw CLI to read a
cache and writes the CLI's text output plus a JSON capture manifest. It never
executes an iOS binary, changes a cache, or communicates with a device.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCHEMA = "project-sweet-10.dyld-loader-capture.v1"

DEFAULT_IMAGES = (
    "/System/Library/PrivateFrameworks/BackBoardHIDEventFoundation.framework/BackBoardHIDEventFoundation",
    "/System/Library/PrivateFrameworks/BackBoardHIDEventProcessors.framework/BackBoardHIDEventProcessors",
    "/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices",
    "/System/Library/PrivateFrameworks/BoardServices.framework/BoardServices",
    "/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer",
    "/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit",
    "/System/Library/Frameworks/IOSurface.framework/IOSurface",
    "/System/Library/Frameworks/QuartzCore.framework/QuartzCore",
    "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics",
    "/System/Library/Frameworks/Metal.framework/Metal",
    "/System/Library/PrivateFrameworks/RunningBoard.framework/RunningBoard",
    "/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices",
    "/System/Library/PrivateFrameworks/SpringBoard.framework/SpringBoard",
    "/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard",
    "/System/Library/Frameworks/Foundation.framework/Foundation",
    "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation",
)


class CaptureError(Exception):
    """Raised when the requested capture cannot safely be started."""


def _output_stem(index, image_path):
    name = image_path.rsplit("/", 1)[-1]
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return "{:02d}-{}".format(index, safe_name or "image")


def capture_records(cache, output_dir, ipsw_bin="ipsw", images=None, overwrite=False):
    """Capture loader text for each requested absolute image path.

    Failed image lookups are recorded and do not prevent later images from
    being inspected. Existing output files are preserved unless overwrite=True.
    """
    cache_path = Path(cache).expanduser().resolve()
    if not cache_path.is_file():
        raise CaptureError("cache path is not a readable file: {}".format(cache_path))

    selected_images = tuple(images) if images is not None else DEFAULT_IMAGES
    if not selected_images:
        raise CaptureError("at least one image path must be selected")
    if any(not isinstance(item, str) or not item.startswith("/") for item in selected_images):
        raise CaptureError("each image must be supplied as an absolute install path")
    if len(set(selected_images)) != len(selected_images):
        raise CaptureError("duplicate image paths were supplied")

    executable = shutil.which(ipsw_bin)
    if executable is None:
        raise CaptureError("cannot find ipsw executable: {}".format(ipsw_bin))

    destination = Path(output_dir).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)

    output_paths = []
    for index, image_path in enumerate(selected_images, start=1):
        stem = _output_stem(index, image_path)
        output_paths.extend((
            destination / (stem + ".txt"),
            destination / (stem + ".stderr.txt"),
        ))
    manifest_path = destination / "capture-manifest.json"
    existing = [path for path in output_paths + [manifest_path] if path.exists()]
    if existing and not overwrite:
        raise CaptureError(
            "output already exists; choose a new directory or pass --overwrite: {}".format(
                ", ".join(str(path.name) for path in existing)
            )
        )

    try:
        version_result = subprocess.run(
            [executable, "version"],
            capture_output=True,
            text=True,
            check=False,
        )
        version_text = (version_result.stdout or version_result.stderr).strip()
    except OSError as exc:
        version_text = "unavailable: {}".format(exc)

    records = []
    for index, image_path in enumerate(selected_images, start=1):
        stem = _output_stem(index, image_path)
        stdout_path = destination / (stem + ".txt")
        stderr_path = destination / (stem + ".stderr.txt")
        command = [executable, "dyld", "image", str(cache_path), image_path]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            return_code = result.returncode
        except OSError as exc:
            stdout = ""
            stderr = str(exc)
            return_code = 127

        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        records.append({
            "image": image_path,
            "exit_code": return_code,
            "status": "captured" if return_code == 0 else "failed",
            "stdout_file": stdout_path.name,
            "stderr_file": stderr_path.name,
            "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
        })

    manifest = {
        "schema": SCHEMA,
        "tool": "ipsw",
        "tool_version_output": version_text,
        "cache_path": str(cache_path),
        "record_count": len(records),
        "successful_count": sum(row["status"] == "captured" for row in records),
        "failed_count": sum(row["status"] == "failed" for row in records),
        "records": records,
        "scope_notes": [
            "The collector stores ipsw text output verbatim; it does not parse loader fields.",
            "A failed lookup is recorded and is not silently treated as an absent dependency.",
            "The cache is opened as an input; only the selected output directory is written.",
            "No iOS executable is run and no device or firmware is accessed.",
            "All observations remain specific to the selected donor cache until independently matched to target evidence.",
        ],
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Capture read-only ipsw dyld loader records for selected cache images."
    )
    parser.add_argument("--cache", required=True, help="path to the mounted SystemOS dyld shared-cache main file")
    parser.add_argument("--output-dir", required=True, help="new or existing directory for text outputs")
    parser.add_argument("--ipsw", default="ipsw", help="ipsw executable name or path (default: ipsw)")
    parser.add_argument(
        "--image",
        action="append",
        help="absolute image install path; repeat to override the built-in priority list",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace output files with matching names in the selected output directory",
    )
    args = parser.parse_args(argv)

    try:
        manifest = capture_records(
            args.cache,
            args.output_dir,
            ipsw_bin=args.ipsw,
            images=args.image,
            overwrite=args.overwrite,
        )
    except (CaptureError, OSError) as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 1

    json.dump(manifest, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if manifest["failed_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
