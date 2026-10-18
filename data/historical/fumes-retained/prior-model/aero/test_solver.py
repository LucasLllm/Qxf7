import unittest
import numpy as np
try:
    import solver
except ModuleNotFoundError:
    solver = None

class SourceBoundary(unittest.TestCase):
    def test_no_generic_airfoil_fallback(self):
        self.assertIsNotNone(solver, 'actual contour loader not implemented')
        with self.assertRaisesRegex(ValueError, 'actual contour'):
            solver.load_contour(None)

    def test_component_drag_is_dimensional_and_speed_dependent(self):
        self.assertTrue(hasattr(solver, 'component_drag'), 'component drag missing')
        geom={'fuselage':{'dimensions_m':[0.9,0.1,0.12], 'wetted_area_estimate_m2':0.25},
              'external_hardware':[], 'nominal_or_illustrative_hardware':[]}
        low=solver.component_drag(geom,14.,'aligned','smooth')
        high=solver.component_drag(geom,20.,'crossflow','rough')
        self.assertGreater(high['fuselage_N'], low['fuselage_N'])
        self.assertGreater(high['lift_props_N'], low['lift_props_N'])
        self.assertAlmostEqual(high['parasite_N'],sum(v for k,v in high.items() if k.endswith('_N') and k!='parasite_N'))

    def test_actual_DAT_fit_has_error_metrics_and_neuralfoil_confidence(self):
        self.assertTrue(hasattr(solver,'contour_diagnostics'),'contour diagnostics missing')
        p=solver.Path(__file__).resolve().parent.parent/'geometry/airfoils/wing_R_200_021/airfoil.dat'
        af=solver.load_contour(p)
        d=solver.contour_diagnostics(af)
        self.assertTrue(np.isfinite(d['fit_rms_chord']))
        self.assertGreater(d['point_count'],20)
        self.assertGreaterEqual(d['confidence'],0)
        self.assertLessEqual(d['confidence'],1)

    def test_geometry_conversion_preserves_actual_contour_chord_and_axis(self):
        self.assertTrue(hasattr(solver,'build_airplane'),'source geometry adapter missing')
        import json
        root=solver.Path(__file__).resolve().parent.parent/'geometry'
        self.assertTrue((root/'GEOMETRY.json').exists(),'geometry child not ready')
        g=json.loads((root/'GEOMETRY.json').read_text())
        plane,meta=solver.build_airplane(g,root)
        self.assertGreater(len(plane.wings),2)
        self.assertTrue(all(w.xsecs[0].airfoil.coordinates is not None for w in plane.wings))
        self.assertGreater(meta['modeled_surface_area_m2'],0.15)
        self.assertTrue(all(x.chord>0 for w in plane.wings for x in w.xsecs))
        self.assertTrue(any(w.name.startswith('tail') for w in plane.wings))

    def test_level_trim_returns_drag_closure_and_residuals(self):
        self.assertTrue(hasattr(solver,'solve_point'),'VLM plus NeuralFoil trim missing')
        import json
        root=solver.Path(__file__).resolve().parent.parent/'geometry'
        g=json.loads((root/'GEOMETRY.json').read_text())
        out=solver.solve_point(g,root,60.,mass=2.9837,mesh=(1,3))
        self.assertLess(abs(out['lift_residual_N']),.05)
        self.assertLess(abs(out['pitch_residual_Nm']),.01)
        self.assertGreater(out['profile_N'],0.)
        self.assertGreater(out['induced_N'],0.)
        self.assertGreater(out['NF_min_confidence'],0.)
        self.assertAlmostEqual(out['drag_N'],out['profile_N']+out['induced_N']+out['parasite_N'])

    def test_missing_geometry_produces_explicit_blocked_artifact_without_curves(self):
        self.assertTrue(hasattr(solver,'run_analysis'),'execution pipeline missing')
        import tempfile,json
        with tempfile.TemporaryDirectory(dir=solver.Path(__file__).resolve().parent) as temp:
            p=solver.Path(temp)
            result=solver.run_analysis(p/'nonexistent.json',p)
            self.assertEqual(result['status'],'blocked')
            self.assertIn('GEOMETRY.json',result['blocker'])
            self.assertTrue((p/'AERO.json').exists())
            self.assertFalse((p/'CURVES.csv').exists())

    def test_ready_geometry_batch_executes_real_solver_and_reuses_orientation_only(self):
        self.assertTrue(hasattr(solver,'generate_curves'),'curve generation missing')
        import json
        root=solver.Path(__file__).resolve().parent.parent/'geometry'
        g=json.loads((root/'GEOMETRY.json').read_text())
        rows=solver.generate_curves(g,root,speeds=[60],masses=[2.9837],surfaces=['smooth'],mesh=(1,3))
        self.assertEqual(len(rows),2)
        self.assertGreater(rows[1]['drag_N'],rows[0]['drag_N'])
        self.assertEqual(rows[1]['induced_N'],rows[0]['induced_N'])
        self.assertEqual(rows[1]['profile_N'],rows[0]['profile_N'])

    def test_ready_pipeline_exports_curves_and_real_mesh_convergence(self):
        self.assertTrue(hasattr(solver,'execute_analysis'),'ready pipeline not implemented')
        import json,tempfile
        root=solver.Path(__file__).resolve().parent.parent/'geometry'
        with tempfile.TemporaryDirectory(dir=solver.Path(__file__).resolve().parent) as temp:
            result=solver.execute_analysis(root/'GEOMETRY.json',solver.Path(temp),speeds=[60],masses=[2.9837],surfaces=['smooth'])
            self.assertEqual(result['status'],'executed_unvalidated')
            self.assertEqual(result['curve_rows'],2)
            self.assertEqual(len(result['mesh_convergence']),3)
            self.assertTrue((solver.Path(temp)/'CURVES.csv').exists())
            self.assertTrue((solver.Path(temp)/'CONTOUR_FITS.json').exists())
            self.assertIn('workingCG',result)

if __name__ == '__main__': unittest.main()
