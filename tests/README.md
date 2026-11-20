# Tests

These host-side checks validate project metadata, the pinned XNU source lock, and the
read-only source-verification workflow. They do not compile XNU, test a kernel, or
interact with a device.

Run the checks locally:

    python3 tools/check_project.py
    python3 -m unittest discover -s tests -p 'test_*.py' -v

The GitHub Actions workflow reads the expected XNU commit from
xnu/BASELINE.lock.json, checks out that exact revision, and runs the verifier.
Repository permissions are read-only.
