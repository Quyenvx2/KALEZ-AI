#!/usr/bin/env python3
"""Collect ESP-IDF flash images and generate their build-derived flash offsets."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
BUILD_DIR = PROJECT_DIR / "build"
OUTPUT_DIR = PROJECT_DIR / "firmware-artifact"
PARTITIONS_CSV = PROJECT_DIR / "partitions" / "v2" / "4m.csv"
EXPECTED_FLASH_SIZE = 4 * 1024 * 1024


def parse_size(value: str) -> int:
    match = re.fullmatch(r"\s*(\d+)\s*(B|KB|MB)\s*", value, re.IGNORECASE)
    if not match:
        raise ValueError(f"Unsupported flash size in build metadata: {value!r}")
    amount = int(match.group(1))
    unit = match.group(2).upper()
    return amount * {"B": 1, "KB": 1024, "MB": 1024 * 1024}[unit]


def read_partitions() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    with PARTITIONS_CSV.open(encoding="utf-8", newline="") as file:
        for row in csv.reader(file):
            if not row or row[0].strip().startswith("#"):
                continue
            fields = [field.strip() for field in row]
            if len(fields) < 5:
                raise ValueError(f"Invalid partition row: {row}")
            rows.append(
                {
                    "name": fields[0],
                    "type": fields[1],
                    "subtype": fields[2],
                    "offset": int(fields[3], 0),
                    "size": int(fields[4], 0),
                }
            )
    return rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    flasher_path = BUILD_DIR / "flasher_args.json"
    if not flasher_path.is_file():
        raise FileNotFoundError(f"ESP-IDF flash metadata was not generated: {flasher_path}")

    flasher = json.loads(flasher_path.read_text(encoding="utf-8"))
    flash_size = parse_size(flasher["flash_settings"]["flash_size"])
    if flash_size != EXPECTED_FLASH_SIZE:
        raise ValueError(f"Expected 4 MB flash profile, build reports {flash_size} bytes")

    flash_files = flasher.get("flash_files")
    if not isinstance(flash_files, dict) or not flash_files:
        raise ValueError("flasher_args.json has no flash_files entries")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    images_dir = OUTPUT_DIR / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    partitions = read_partitions()
    factory_partition = next(
        (part for part in partitions if part["name"] == "factory"), None
    )
    if factory_partition is None:
        raise ValueError("4 MB partition table has no factory app partition")

    flash_entries: list[dict[str, str | int]] = []
    for offset_text, relative_file in sorted(
        flash_files.items(), key=lambda item: int(item[0], 0)
    ):
        offset = int(offset_text, 0)
        source = (BUILD_DIR / relative_file).resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Flash image listed by ESP-IDF is missing: {source}")
        size = source.stat().st_size
        if offset < 0 or offset + size > flash_size:
            raise ValueError(
                f"Image {relative_file} at {offset_text} exceeds 4 MB flash"
            )

        if offset == factory_partition["offset"] and size > factory_partition["size"]:
            raise ValueError(
                f"App image is {size} bytes but factory partition allows "
                f"{factory_partition['size']} bytes"
            )

        artifact_name = f"{offset:08x}-{source.name}"
        destination = images_dir / artifact_name
        shutil.copy2(source, destination)
        flash_entries.append(
            {
                "offset": f"0x{offset:x}",
                "source": str(Path(relative_file).as_posix()),
                "artifact": f"images/{artifact_name}",
                "size_bytes": size,
                "sha256": sha256(destination),
            }
        )

    if not any(
        int(entry["offset"], 0) == factory_partition["offset"]
        for entry in flash_entries
    ):
        raise ValueError("ESP-IDF flash metadata does not include the factory app image")

    merged = BUILD_DIR / "merged-binary.bin"
    if not merged.is_file():
        raise FileNotFoundError(f"release.py did not create {merged}")
    if merged.stat().st_size > flash_size:
        raise ValueError("Merged binary is larger than 4 MB flash")
    shutil.copy2(merged, OUTPUT_DIR / "merged-binary.bin")
    shutil.copy2(PARTITIONS_CSV, OUTPUT_DIR / "4m-partitions.csv")
    shutil.copy2(BUILD_DIR / "partition_table" / "partition-table.bin", OUTPUT_DIR)

    release_archives = sorted((PROJECT_DIR / "releases").glob("*.zip"))
    if release_archives:
        shutil.copy2(release_archives[-1], OUTPUT_DIR / release_archives[-1].name)

    manifest = {
        "target": "esp32c3",
        "flash_size_bytes": flash_size,
        "flash_settings": flasher["flash_settings"],
        "merged_binary": {
            "artifact": "merged-binary.bin",
            "offset": "0x0",
            "size_bytes": merged.stat().st_size,
            "sha256": sha256(OUTPUT_DIR / "merged-binary.bin"),
        },
        "partition_table": partitions,
        "individual_flash_images": flash_entries,
        "note": "Individual image offsets are copied from ESP-IDF flasher_args.json.",
    }
    (OUTPUT_DIR / "flash-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    settings = flasher["flash_settings"]
    flash_flags = " ".join(
        f"{flag} {settings[key]}"
        for flag, key in (
            ("--flash_mode", "flash_mode"),
            ("--flash_size", "flash_size"),
            ("--flash_freq", "flash_freq"),
        )
    )
    lines = [
        "ESP32-C3 SuperMini firmware flash manifest",
        "Flash size: 4 MB",
        "",
        "Simple full-image flash (merged image includes build-defined offsets):",
        f"  esptool.py --chip esp32c3 --port COMx --baud 460800 write_flash {flash_flags} 0x0 merged-binary.bin",
        "",
        "Individual images (use these exact offsets if flashing files separately):",
    ]
    lines.extend(
        f"  {entry['offset']}  {entry['artifact']}  ({entry['size_bytes']} bytes)"
        for entry in flash_entries
    )
    lines.extend(
        [
            "",
            "The individual offsets and image list come from the ESP-IDF build output.",
            "See flash-manifest.json for partition sizes and SHA-256 hashes.",
        ]
    )
    (OUTPUT_DIR / "FLASH-MANIFEST.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    print(f"Packaged {len(flash_entries)} flash images in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
