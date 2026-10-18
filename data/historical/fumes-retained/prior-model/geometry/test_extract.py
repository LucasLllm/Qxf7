import unittest
import importlib.util
from pathlib import Path
import numpy as np

OUT=Path(__file__).resolve().parent
class ContourTests(unittest.TestCase):
    def test_outer_excludes_nested_internal_contours(self):
        spec=importlib.util.spec_from_file_location('extract',OUT/'extract.py')
        self.assertIsNotNone(spec)
        self.assertTrue((OUT/'extract.py').exists(), 'missing outer-contour implementation')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        outer=np.array([[0,0],[2,0],[2,1],[0,1],[0,0]],float)
        inner=np.array([[.2,.2],[.4,.2],[.4,.4],[.2,.4],[.2,.2]])
        seg=np.concatenate([np.stack([a[:-1],a[1:]],axis=1) for a in [outer,inner]])
        p,diag=mod.outer_contour(seg)
        self.assertEqual(p.area,2)
        self.assertEqual(len(p.interiors),0)
        self.assertTrue(p.exterior.is_closed)
        self.assertTrue(np.isfinite(p.exterior.coords).all())
        self.assertEqual(diag['retained_outer_contours'],1)
    def test_no_internal_only_profile_when_native_outer_is_open(self):
        import json
        result=json.loads((OUT/'GEOMETRY.json').read_text())
        foils=[f for f in result['airfoils'] if f['part']=='RUDDER 2 L']
        self.assertGreater(len(foils),0,'native internal loop must not conceal missing outer contour; inspect original physical STL')
        for foil in result['airfoils']:
            self.assertGreater(foil['outline_chord_coverage_ratio'],.98)
            self.assertEqual(foil['internal_contours_exported'],0)

    def test_airfoil_similarity_area_order_and_documented_motor(self):
        import json
        result=json.loads((OUT/'GEOMETRY.json').read_text())
        self.assertAlmostEqual(result['documented_motor_dimensions'][0]['diameter_m'],.0334)
        for foil in result['airfoils']:
            points=np.loadtxt(OUT/foil['file'],skiprows=1)
            area=abs(np.sum(points[:-1,0]*points[1:,1]-points[1:,0]*points[:-1,1]))/2
            expected=foil['source_outline_area_mm2']/(foil['chord_m']*1000)**2
            self.assertAlmostEqual(area,expected,places=6)
            le=np.argmin(points[:,0])
            self.assertGreater(points[1:le,1].mean(),points[le+1:-1,1].mean())
            self.assertGreater(points[0,0],.98)

    def test_actual_source_geometry_deliverable(self):
        import json, hashlib
        spec=importlib.util.spec_from_file_location('extract',OUT/'extract.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        self.assertTrue(hasattr(mod,'main'),'missing actual-source extraction')
        result=mod.main()
        self.assertEqual(result['units']['length'],'m')
        self.assertGreater(result['wing']['span_m'],1.6)
        self.assertLess(result['wing']['span_m'],1.7)
        self.assertGreater(result['tail']['projected_union_area_m2'],.01)
        self.assertGreater(len(result['airfoils']),2)
        self.assertGreater(result['fuselage']['wetted_area_estimate_m2'],.1)
        for source in result['sources']:
            self.assertEqual(hashlib.sha256(Path(source['path']).read_bytes()).hexdigest(),source['sha256'])
        for foil in result['airfoils']:
            points=np.loadtxt(OUT/foil['file'],skiprows=1)
            self.assertTrue(np.isfinite(points).all())
            self.assertTrue(np.allclose(points[0],points[-1],atol=1e-9))
            self.assertLess(points[:,0].min(),1e-8)
            self.assertAlmostEqual(points[:,0].max(),1,places=5)
            self.assertGreater(len(points),30)
            self.assertEqual(foil['retained_outer_contours'],1)
            self.assertEqual(foil['internal_contours_exported'],0)
            self.assertGreater(foil['source_outline_area_mm2'],0)
        self.assertTrue((OUT/'GEOMETRY.json').exists())

if __name__=='__main__':unittest.main()
