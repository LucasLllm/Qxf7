"""Copy retained Fumes evidence into data/historical/fumes-retained/ (read-only source).

Lucas authorized this import on 2026-10-18. Sources under ~/.hermes are only read.
Each copied file is recorded in MANIFEST.json with its original absolute path and SHA-256.
Files larger than GZIP_ABOVE bytes are stored gzipped; the manifest keeps the original hash.

Run: .venv/bin/python scripts/import_fumes_retained.py
"""
import gzip
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "historical" / "fumes-retained"
SD = Path("/Users/lucasliu/.hermes/profiles/fumes/notes/stork-development")
PRIOR = SD / "performance-scenarios/original-manual-range/aircraft-specific-analysis"

GZIP_ABOVE = 5_000_000
TEXT_EXT = {".md", ".json", ".csv", ".py", ".txt", ".dat", ".log"}
SKIP_PARTS = {"deps", "__pycache__", "components", "sources"}

# (source dir or file, destination subdir, allowed extensions or None for TEXT_EXT, provenance label)
GROUPS = [
    (PRIOR, "prior-model", TEXT_EXT | {".png"},
     "model (prior Fumes AeroSandbox/NeuralFoil + mission model, 2026-10-09); historical, not validated"),
    (SD / "performance-scenarios/original-manual-range/REPORT.md", "prior-model/parent", None,
     "model (parent original-manual-range report)"),
    (SD / "performance-scenarios/original-manual-range/RESULTS.json", "prior-model/parent", None,
     "model (parent original-manual-range results)"),
    (SD / "stock-validation-methods/benchmark-v1", "benchmark-v1", TEXT_EXT,
     "documentary benchmark freeze (third-party Flightony claims + official manual)"),
    (SD / "flightony-independent-check", "flightony-independent-check", TEXT_EXT,
     "model (prior independent accounting of Flightony claims)"),
    (SD / "cfd-exterior-v2/hardware-research-motors", "hardware-placement", {".md", ".json", ".py"},
     "model (approximate installed motor/boom placement; +X fwd, +Y left, +Z up, metres)"),
    (SD / "stork-aero-geometry/fuselage-with-hatches/results.json", "fuselage-dense", None,
     "model (dense 419-station fuselage envelope result)"),
    (SD / "stork-aero-geometry/fuselage-with-hatches/envelope_loft.npz", "fuselage-dense", None,
     "model (dense envelope loft arrays)"),
    (SD / "performance-scenarios/range-first/worst-case/lift-research", "lift-evidence/lift-research",
     {".md", ".json", ".jpg"},
     "manufacturer F90 spec/bench images (6S only) + prior notes; no 4S/7-inch matched test"),
    (SD / "performance-scenarios/range-first/source-refresh/f90.json", "lift-evidence", None,
     "retailer listing capture (HobbyRC): 5-6S recommended"),
    (SD / "stock-validation-methods/seller-specs.txt", "lift-evidence", None, "third-party vendor claim (Flightony)"),
    (SD / "stock-validation-methods/seller-performance.txt", "lift-evidence", None,
     "third-party vendor claim (Flightony)"),
]
# The propulsion/data folder holds manufacturer/vendor source files; extensions widened for images.
PROP_DATA = (PRIOR / "propulsion/data", "prior-model/propulsion/data",
             {".dat", ".csv", ".txt", ".json", ".png", ".jpg"},
             "APC = manufacturer-computed map (not measured); BH2812 = vendor bench sheet; "
             "P50B = manufacturer chart + prior digitization (test-condition labels conflict)")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def files_of(src: Path, exts):
    if src.is_file():
        return [(src, Path(src.name))]
    out = []
    for p in sorted(src.rglob("*")):
        rel = p.relative_to(src)
        if not p.is_file() or SKIP_PARTS & set(rel.parts) or p.suffix.lower() not in exts:
            continue
        if rel.parts[0] == "propulsion" and len(rel.parts) > 1 and rel.parts[1] == "data":
            continue  # handled by PROP_DATA
        out.append((p, rel))
    return out


def main():
    records = []
    for src, sub, exts, prov in GROUPS + [PROP_DATA]:
        for p, rel in files_of(src, exts or TEXT_EXT):
            dst = DEST / sub / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            digest = sha256(p)
            size = p.stat().st_size
            if size > GZIP_ABOVE:
                dst = dst.with_name(dst.name + ".gz")
                with open(p, "rb") as fi, open(dst, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as fo:
                    shutil.copyfileobj(fi, fo)
            else:
                shutil.copy2(p, dst)
                assert sha256(dst) == digest
            records.append({"source": str(p), "dest": str(dst.relative_to(ROOT)), "sha256_original": digest,
                            "bytes_original": size, "gzipped": dst.suffix == ".gz", "provenance": prov})
    manifest = {"imported_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "authority": "Lucas, 2026-10-18: import retained evidence; Fumes workspace read-only",
                "publication": "LOCAL ONLY. Contains vendor-derived data/images; review before any upload.",
                "files": records}
    (DEST / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    print(f"{len(records)} files, {sum(r['bytes_original'] for r in records)/1e6:.1f} MB original")


if __name__ == "__main__":
    main()
