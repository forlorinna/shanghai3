#!/usr/bin/env python3
"""Check the native libraries of an Android ARM64 APK for 16 KiB ELF alignment."""
import argparse
import struct
from zipfile import ZipFile

PAGE_SIZE = 16 * 1024
ELF_HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
PROGRAM_HEADER = struct.Struct("<IIQQQQQQ")


def check_library(apk, entry):
    with apk.open(entry) as library:
        header = library.read(ELF_HEADER.size)
        if len(header) != ELF_HEADER.size:
            raise ValueError(f"{entry.filename}: truncated ELF header")
        ident, elf_type, machine, version, _, offset, _, _, _, width, count, *_ = (
            ELF_HEADER.unpack(header)
        )
        if ident[:7] != b"\x7fELF\x02\x01\x01" or (elf_type, machine, version) != (3, 183, 1):
            raise ValueError(f"{entry.filename}: expected a little-endian AArch64 ELF shared library")
        if (width < PROGRAM_HEADER.size or offset < ELF_HEADER.size
                or offset + width * count > entry.file_size):
            raise ValueError(f"{entry.filename}: invalid program header table")
        loads = 0
        for index in range(count):
            library.seek(offset + index * width)
            kind, _, file_offset, vaddr, _, _, _, align = PROGRAM_HEADER.unpack(
                library.read(PROGRAM_HEADER.size)
            )
            if kind != 1:  # PT_LOAD
                continue
            loads += 1
            if align < PAGE_SIZE or align & (align - 1) or (vaddr - file_offset) % PAGE_SIZE:
                raise ValueError(f"{entry.filename}: PT_LOAD {index} incompatible with a 16 KiB page")
        if loads == 0:
            raise ValueError(f"{entry.filename}: no loadable segments")
        print(f"{entry.filename}: AArch64, {loads} load segments aligned for 16 KiB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk")
    args = parser.parse_args()
    with ZipFile(args.apk) as apk:
        libraries = [entry for entry in apk.infolist()
                     if entry.filename.startswith("lib/") and entry.filename.endswith(".so")]
        names = {entry.filename for entry in libraries}
        if "lib/arm64-v8a/libil2cpp.so" not in names or len(names) != len(libraries):
            parser.exit(1, "Missing IL2CPP library or duplicate native library entries\n")
        try:
            for entry in libraries:
                if not entry.filename.startswith("lib/arm64-v8a/"):
                    raise ValueError(f"{entry.filename}: APK contains a non-ARM64 ABI")
                check_library(apk, entry)
        except ValueError as error:
            parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
