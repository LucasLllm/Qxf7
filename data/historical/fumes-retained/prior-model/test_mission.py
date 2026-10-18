import unittest
from pathlib import Path
import importlib.util

class MissionTests(unittest.TestCase):
    def load(self):
        p=Path(__file__).with_name('mission.py')
        self.assertTrue(p.exists(), 'mission implementation missing')
        s=importlib.util.spec_from_file_location('mission',p)
        m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    def test_zero_wind_energy_accounting(self):
        m=self.load();r=m.mission_range(airspeed_mps=20,power_w=200,usable_wh=150,reserve_wh=30,vtol_wh=20)
        self.assertAlmostEqual(r['range_km'],36)
        self.assertAlmostEqual(r['wh_per_km'],200/72)
        self.assertAlmostEqual(r['cruise_wh'],100)

    def test_invalid_energy_and_nonforward_groundspeed_rejected(self):
        m=self.load()
        base=dict(airspeed_mps=20,power_w=200,usable_wh=150,reserve_wh=30,vtol_wh=20)
        for key,value in [('airspeed_mps',0),('power_w',-1),('usable_wh',float('nan')),('reserve_wh',-1),('vtol_wh',-1),('tailwind_mps',-20)]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):m.mission_range(**(base|{key:value}))

    def test_optimum_is_minimum_energy_per_distance_not_minimum_power(self):
        m=self.load()
        self.assertTrue(hasattr(m,'range_curve'),'speed-curve evaluator missing')
        rows=m.range_curve([(10,100),(20,150)],usable_wh=150,reserve_wh=30,vtol_wh=20)
        best=max(rows,key=lambda r:r['range_km'])
        self.assertEqual(best['airspeed_mps'],20)
        self.assertAlmostEqual(best['range_km'],48)

if __name__=='__main__':unittest.main()
