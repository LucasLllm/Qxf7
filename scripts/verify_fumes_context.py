#!/usr/bin/env python3
"""Offline integrity/transfer checks only; no simulation or hardware actions."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_mass_rows(rows: list[dict], originals: list[dict]) -> dict:
    assert len(rows) == len(originals) == 58, 'definition count'
    assert len({r['part_name'] for r in rows}) == 58, 'duplicate names'
    source = {r['filename']: r for r in originals}
    assert {r['part_name'] for r in rows} == set(source), 'part membership'
    for row in rows:
        old = source[row['part_name']]
        assert int(row['quantity']) == int(old['installed_quantity']), row['part_name']
        assert row['filament'] == old['filament'], row['part_name']
        for a, b in [('mass_g_each', 'mass_per_piece_g'), ('installed_mass_g', 'installed_mass_g')]:
            assert float(row[a]) == float(old[b]), (row['part_name'], a)
            assert math.isfinite(float(row[a])) and float(row[a]) > 0
        # Source released rows have rounded per-piece/installed columns.
        assert abs(float(row['mass_g_each']) * int(row['quantity']) - float(row['installed_mass_g'])) < 0.00001
        assert all(row[c] == '' for c in ['x_cg_mm', 'y_cg_mm', 'z_cg_mm']), 'unregistered centroid'
        assert row['status'] == old['status']
        assert row['evidence_path'] == 'fumes-import/evidence/' + old['evidence']
    assert sum(int(r['quantity']) for r in rows) == 82, 'installed piece count'
    total = sum(float(r['installed_mass_g']) for r in rows)
    assert abs(total - 965.642456) < 1e-8, total
    return {'definitions': len(rows), 'installed_pieces': 82, 'predicted_installed_g': total}


def check(root: Path) -> dict:
    dst = root / 'data/hardware/fumes-import'
    manifest = json.loads((dst / 'IMPORT_MANIFEST.json').read_text())
    for item in manifest['files']:
        assert digest(root / item['destination']) == item['sha256'], item['destination']
    receipt = json.loads((dst / 'PRINTED_MASS_COMPLETION_VERIFICATION.json').read_text())
    assert digest(dst / 'PART_MASS_RESULTS.csv') == receipt['csv_sha256']
    originals = list(csv.DictReader((dst / 'PART_MASS_RESULTS.csv').open()))
    rows = list(csv.DictReader((root / 'data/hardware/slicer_weights.csv').open()))
    masses = validate_mass_rows(rows, originals)
    for row in originals:
        assert digest(dst / 'evidence' / row['evidence']) == receipt['evidence_sha256'][row['filename']]
    before = json.loads((root / 'docs/fumes-context-before.json').read_text())
    permitted_changes = {
        'CLAUDE.md', 'README.md', 'context/00_INDEX.md',
        # Lucas-authorized requirement/budget clarification; preserve original hashes.
        'context/01_project_overview.md', 'context/02_requirements.md',
        'context/04_stork_baseline_aircraft.md',
        'context/05_cad_geometry_extraction.md', 'context/06_performance_method.md',
        'context/09_open_questions_risks.md', 'context/11_history_log.md',
        'context/reference/qxf7-stork-baseline-geometry.md',
        'data/hardware/slicer_weights.csv', 'prompts/01_onboarding.md',
        'prompts/02_performance_simulation.md',
        # 2026-10-18 Lucas-authorized local git setup: build/scratch/credential excludes appended.
        '.gitignore',
    }
    changed = []
    geometry_count = 0
    for name, oldhash in before.items():
        assert (root / name).is_file(), 'missing original: ' + name
        if name.startswith('data/stork-geometry-bundle/'):
            geometry_count += 1
        if digest(root / name) != oldhash:
            changed.append(name)
            assert name in permitted_changes, 'unexpected original change: ' + name
    assert geometry_count > 0
    assert digest(root / 'data/hardware/hardware.yaml') == before['data/hardware/hardware.yaml']
    centroids = json.loads((dst / 'mass-closure/predicted-print-centroids.json').read_text())
    assert centroids['axes'] == {'+X': 'forward', '+Y': 'left', '+Z': 'up'}
    assert centroids['summary']['aircraft_mass_g'] is None
    assert centroids['summary']['aircraft_centroid_assembly_mm'] is None
    reference = json.loads((root / 'data/hardware/standard_stork_reference.json').read_text())
    assert reference['lift']['ESC_architecture'] == '4-in-1'
    assert reference['final_qxf7']['lift_ESC_architecture'] is None
    assert reference['final_qxf7']['cruise_airspeed_target_min_km_h'] == 70
    assert reference['study_budget']['active_cost_constraint'] is None
    assert reference['mass_reference']['aircraft_CG_mm'] is None
    assert reference['battery']['actual_finished_mass_g'] is None
    ledger = json.loads((dst / 'MASS_RECONCILIATION.json').read_text())
    cases = {case['name']: case for case in ledger['scenarios']}
    for case, source_case in [('low', 'low'), ('central', 'central'), ('high', 'higher_installation')]:
        assert abs(reference['mass_reference']['dry_' + case + '_g'] - cases[source_case]['dry_equipped_planning_g']) < 1e-8
        parts = cases[source_case]['parts']
        assert abs(sum(parts.values()) - cases[source_case]['dry_equipped_planning_g']) < 1e-8
    assert abs(reference['battery']['nominal_energy_Wh'] - reference['battery']['nominal_voltage_V'] * reference['battery']['capacity_mAh'] / 1000) < 1e-10
    for name in ['CLAUDE.md', 'README.md', 'context/00_INDEX.md', 'prompts/01_onboarding.md', 'prompts/02_performance_simulation.md']:
        text = (root / name).read_text()
        assert '12_fumes_handoff.md' in text and 'CONTEXT_CONFLICTS.md' in text, 'missing entrypoint: ' + name
    for name in ['context/12_fumes_handoff.md', 'docs/CONTEXT_CONFLICTS.md', 'data/hardware/README.md']:
        assert (root / name).stat().st_size > 300
    return {
        'status': 'PASS', 'scope': 'Context-transfer integrity only; not physics/process/flight validation',
        'source_copies_hash_checked': len(manifest['files']),
        'parent_release_evidence_hashes_checked': len(originals),
        **masses, 'geometry_bundle_original_files_unchanged': geometry_count,
        'hardware_yaml_unchanged': True, 'unregistered_CG_cells_blank': True,
        'changed_original_files': sorted(changed),
        'reference_mass_cases_match_retained_ledger': True,
        'user_clarifications': {'budget': 'deferred', 'modified_qxf7_cruise_min_km_h': 70, 'standard_stork_lift_ESC': '4-in-1'},
        'future_work_not_blocking_stock_baseline': ['final QxF7 ESC trade', 'validated final weather envelope', 'loaded-case packaging membership'],
        'simulation_executed': False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path, help='Optional local JSON receipt output')
    args = parser.parse_args()
    report = check(ROOT)
    text = json.dumps(report, indent=2) + '\n'
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
