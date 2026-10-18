"""Regression tests for the migrated mass table integrity checker (no physics claims)."""
import copy
import csv
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_fumes_context import validate_mass_rows


class TransferChecks(unittest.TestCase):
    def setUp(self):
        with (ROOT / 'data/hardware/slicer_weights.csv').open() as f:
            self.rows = list(csv.DictReader(f))
        with (ROOT / 'data/hardware/fumes-import/PART_MASS_RESULTS.csv').open() as f:
            self.originals = list(csv.DictReader(f))

    def test_current_import(self):
        self.assertEqual(validate_mass_rows(self.rows, self.originals)['installed_pieces'], 82)

    def test_reject_changed_quantity(self):
        self.rows[0]['quantity'] = str(int(self.rows[0]['quantity']) + 1)
        with self.assertRaises(AssertionError):
            validate_mass_rows(self.rows, self.originals)

    def test_reject_changed_mass(self):
        self.rows[0]['mass_g_each'] = str(float(self.rows[0]['mass_g_each']) + 1)
        with self.assertRaises(AssertionError):
            validate_mass_rows(self.rows, self.originals)

    def test_reject_unregistered_cg(self):
        self.rows[0]['x_cg_mm'] = '47'
        with self.assertRaises(AssertionError):
            validate_mass_rows(self.rows, self.originals)

    def test_reject_duplicate_or_missing_part(self):
        self.rows[1] = copy.deepcopy(self.rows[0])
        with self.assertRaises(AssertionError):
            validate_mass_rows(self.rows, self.originals)


if __name__ == '__main__':
    unittest.main()
