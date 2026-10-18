"""Fixtures exercise coupling mechanics, not claimed Stork drag measurements."""
import unittest
from couple import couple
class CouplingTests(unittest.TestCase):
    def test_real_map_energy_accounting(self):
        rows=couple(airspeed_kmh=60,drag_n=3,voltage_v=14.4,usable_wh=190,reserve_wh=40,vtol_wh=20)
        self.assertEqual(len(rows),6)
        for r in rows:
            self.assertGreater(r['shaft_w'],0)
            self.assertGreater(r['battery_terminal_power_w'],r['shaft_w'])
            if r['voltage_feasible']:
                self.assertAlmostEqual(r['range_km'],130*60/r['battery_terminal_power_w'])
    def test_low_voltage_is_not_reported_as_achieved_range(self):
        rows=couple(airspeed_kmh=60,drag_n=8,voltage_v=10,usable_wh=190,reserve_wh=40,vtol_wh=20)
        failed=[r for r in rows if not r['voltage_feasible']]
        self.assertTrue(failed)
        for r in failed:self.assertIsNone(r['range_km'])
    def test_missing_prop_point_rejected(self):
        with self.assertRaises(ValueError):couple(airspeed_kmh=500,drag_n=3,voltage_v=14.4,usable_wh=190,reserve_wh=40,vtol_wh=20)
if __name__=='__main__':unittest.main()
