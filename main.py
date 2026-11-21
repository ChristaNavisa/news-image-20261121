"""The Saturday Ledger - 21 November 2026.

Copies the pre-rendered front page (entry.png, rendered in-session from
render.html + stories.json with Playwright/Chromium) to the output
directory. Python standard library only: no Pillow, no numpy, no network.

The image is verified before copying: it must be a PNG or JPEG under the
1 MiB gate, and its sha256 fingerprint is printed so two runs can be
compared byte for byte.
"""
import hashlib
import os
import shutil
import sys

ENTRY = "entry.png"
MAX_BYTES = 1048576


def resolve_here():
    return os.path.dirname(os.path.abspath(__file__))


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    here = resolve_here()
    src = os.path.join(here, ENTRY)
    out = output_dir()
    os.makedirs(out, exist_ok=True)
    size = os.path.getsize(src)
    if size > MAX_BYTES:
        raise SystemExit("entry.png too large: %d > %d" % (size, MAX_BYTES))
    with open(src, "rb") as f:
        magic = f.read(8)
    is_png = magic[:4] == b"\x89PNG"
    is_jpeg = magic[:3] == b"\xff\xd8\xff"
    if not (is_png or is_jpeg):
        raise SystemExit("entry.png is not a PNG or JPEG image")
    dst = os.path.join(out, ENTRY)
    shutil.copyfile(src, dst)
    with open(dst, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (dst, size, digest))


if __name__ == "__main__":
    main()
