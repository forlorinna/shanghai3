#!/usr/bin/env python3
"""Fetch and verify the pinned CC0 benchmark texture set."""
import csv
import hashlib
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "UnityProject/Assets/Skyline/BenchmarkTextures"
ASSET = "concrete_floor_02"
BASE_URL = "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k"
FILES = {
    "diff": (776097, "1cfee53d2f82fa59726ab7ae6a2e8c09"),
    "nor_gl": (192757, "c2065fd81f571f4e39163ea5661128fb"),
    "rough": (318550, "653d60d0db1872a49138455cf31c8326"),
    "ao": (376977, "a806f59837ef4783642e157eecea0ce5"),
}


def main():
    rows = []
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for channel, (size, md5) in FILES.items():
        filename = f"{ASSET}_{channel}_1k.jpg"
        path = DESTINATION / filename
        url = f"{BASE_URL}/{ASSET}/{filename}"
        if path.exists():
            content = path.read_bytes()
        else:
            with urlopen(url, timeout=30) as response:
                content = response.read(size + 1)
        if (len(content) != size or not content.startswith(b"\xff\xd8\xff")
                or hashlib.md5(content).hexdigest() != md5):
            raise ValueError(f"Invalid provider payload: {filename}")
        if not path.exists():
            path.write_bytes(content)
        rows.append({
            "asset_id": f"{ASSET}_{channel}", "building_id": "",
            "source_page": f"https://polyhaven.com/a/{ASSET}", "download_url": url,
            "author": "Rob Tuytel", "license": "CC0-1.0",
            "license_evidence": "https://polyhaven.com/license",
            "offline_allowed": "yes", "redistribution_allowed": "yes",
            "source_type": "photographic PBR benchmark surface", "geo_coverage": "",
            "source_date": "", "sha256": hashlib.sha256(content).hexdigest(), "bytes": size,
            "source_format": "JPEG", "mesh_stats": "", "texture_stats": "1K provider variant",
            "local_path": str(path.relative_to(ROOT)), "unity_guid": "", "prefab_path": "",
            "lod_level": "", "status": "downloaded", "blocker": "Unity import not run",
        })
    manifest_path = ROOT / "Docs/ASSET_MANIFEST.csv"
    if manifest_path.exists():
        updated_ids = {row["asset_id"] for row in rows}
        with manifest_path.open(encoding="utf-8", newline="") as existing:
            rows.extend(row for row in csv.DictReader(existing) if row["asset_id"] not in updated_ids)
    with manifest_path.open("w", encoding="utf-8", newline="") as manifest:
        writer = csv.DictWriter(manifest, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
