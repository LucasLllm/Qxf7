import unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent

class ModelTests(unittest.TestCase):
    def test_import_and_exact_map_node(self):
        self.assertTrue((ROOT/'model.py').exists(),'bounded model not implemented')
        spec=importlib.util.spec_from_file_location('prop_model',ROOT/'model.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        prop=m.Propeller()
        row=prop.blocks[6000][10]
        result=prop.at(6000,row[0])
        self.assertAlmostEqual(result['thrust_N'],row[1])
        self.assertAlmostEqual(result['shaft_W'],row[2])

class InverseTests(unittest.TestCase):
    def test_solve_and_reject_extrapolation(self):
        spec=importlib.util.spec_from_file_location('prop_model',ROOT/'model.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        prop=m.Propeller()
        self.assertTrue(hasattr(prop,'solve'),'thrust inversion not implemented')
        for speed in (50/3.6,60/3.6,70/3.6):
            for thrust in ((2,4,8) if speed==70/3.6 else (1,2,4,8)):
                result=prop.solve(thrust,speed)
                self.assertAlmostEqual(result['thrust_N'],thrust,places=8)
                self.assertGreater(result['shaft_W'],thrust*speed)
        for rpm,speed in ((999,0),(prop.rpms[-1]+1,0),(6000,1000),(6000,float('nan'))):
            with self.assertRaises(m.DomainError):prop.at(rpm,speed)
        for thrust in (-1,10000,float('nan')):
            with self.assertRaises(m.DomainError):prop.solve(thrust,60/3.6)
        with self.assertRaises(m.DomainError):prop.solve(1,10000)

class ElectricalTests(unittest.TestCase):
    def test_motor_energy_identity_and_loaded_voltage_gate(self):
        spec=importlib.util.spec_from_file_location('prop_model',ROOT/'model.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        self.assertTrue(hasattr(m,'evaluate'),'electrical evaluation not implemented')
        r=m.evaluate(4,60/3.6,14.4)
        self.assertEqual(len(r['motor_cases']),6)
        for c in r['motor_cases']:
            reference_emf=c['idle_reference_V']-1.17*c['effective_R_ohm']
            self.assertAlmostEqual(c['no_load_W']/reference_emf,1.17)
            self.assertAlmostEqual(c['electrical_W'],r['shaft_W']+c['copper_W']+c['no_load_W'])
            self.assertAlmostEqual(c['ideal_bus_A'],c['electrical_W']/14.4)
            self.assertGreater(c['electrical_W'],r['shaft_W'])
            self.assertEqual(c['voltage_feasible'],c['required_motor_V']<=14.4)
        high=m.evaluate(8,70/3.6,10)
        self.assertTrue(any(not c['voltage_feasible'] for c in high['motor_cases']))
        for v in (0,9.9,16.81,float('nan')):
            with self.assertRaises(m.DomainError):m.evaluate(4,60/3.6,v)

class BatteryTests(unittest.TestCase):
    def test_curve_integration_keeps_reserve_separate(self):
        spec=importlib.util.spec_from_file_location('prop_model',ROOT/'model.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        self.assertTrue(hasattr(m,'integrate_curve'),'battery integration not implemented')
        curve=[(0,4.2),(1,3.8),(2,3.0)]
        self.assertAlmostEqual(m.integrate_curve(curve,3.0),7.4)
        self.assertAlmostEqual(m.integrate_curve(curve,3.8),4)
        for cutoff in (2.5,4.3,float('nan')):
            with self.assertRaises(m.DomainError):m.integrate_curve(curve,cutoff)
        r=m.energy_budget(200,20,15)
        self.assertEqual(r,dict(source_usable_Wh=200,reserve_Wh=20,noncruise_Wh=15,cruise_Wh=165))
        with self.assertRaises(m.DomainError):m.energy_budget(200,210,0)

class LimitTests(unittest.TestCase):
    def test_selected_prop_rpm_limit_and_unsupported_low_thrust(self):
        spec=importlib.util.spec_from_file_location('prop_model',ROOT/'model.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with self.assertRaises(m.DomainError):m.evaluate(32,50/3.6,16.8)
        with self.assertRaises(m.DomainError):m.Propeller().solve(1,70/3.6)

class BuildTests(unittest.TestCase):
    def test_offline_capture_build_and_hashes(self):
        self.assertTrue((ROOT/'build.py').exists(),'offline build missing')
        spec=importlib.util.spec_from_file_location('prop_build',ROOT/'build.py')
        b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
        curve=b.digitize()
        self.assertGreater(len(curve),1500)
        self.assertLess(curve[0][0],0.01)
        self.assertGreater(curve[-1][0],4.6)
        out=b.build()
        self.assertEqual(out['battery']['qualified_mission_usable_Wh'],None)
        self.assertEqual(out['battery']['nominal_Wh'],216)
        self.assertEqual(len(out['examples']),12)
        for record in out['source_manifest']:
            import hashlib
            self.assertEqual(hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest(),record['sha256'])
        self.assertLess(out['battery']['curve_diagnostic']['pack_equivalent_Wh_to_3V'],216)
        self.assertGreater(out['battery']['curve_diagnostic']['pack_equivalent_Wh_to_3V'],170)

if __name__=='__main__':unittest.main()
