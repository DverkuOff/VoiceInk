#!/usr/bin/env python3
"""Patch whisper.cpp's build-xcframework.sh in place so it only builds the macOS slice.

Usage: python3 -I whisper-macos-only.py path/to/build-xcframework.sh
"""
import re
import sys

path = sys.argv[1]
src = open(path).read().splitlines(keepends=True)

out = []
skipping = False
for line in src:
    # Drop whole "echo Building for <non-macOS>..." -> "cmake --build build-xxx" blocks.
    m = re.match(r'echo "Building for (.+)\.\.\."', line)
    if m and m.group(1) != "macOS":
        skipping = True
    if skipping:
        if line.startswith("cmake --build "):
            skipping = False
        continue
    # Drop per-platform lines that reference non-macOS build dirs.
    if re.search(r'build-(ios|visionos|tvos|watchos)', line) and not line.lstrip().startswith("rm -rf"):
        continue
    out.append(line)

text = "".join(out)
for needle in ('cmake -B build-macos', 'combine_static_libraries "build-macos"', '-framework $(pwd)/build-macos'):
    if needle not in text:
        sys.exit(f"patch failed: '{needle}' missing")
if re.search(r'cmake -B build-(ios|visionos|tvos)', text):
    sys.exit("patch failed: non-macOS cmake build still present")

open(path, "w").write(text)
print("whisper build script patched: macOS only")
