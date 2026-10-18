import unittest
from accounting import pack_energy,cruise_budget,range_km,ideal_hover_w
class AccountingTests(unittest.TestCase):
    def test_energy(self):
        self.assertAlmostEqual(pack_energy(4,4),288)
        self.assertAlmostEqual(pack_energy(4,3),216)
    def test_no_double_reserve(self):
        self.assertAlmostEqual(cruise_budget(288,.1,0),259.2)
        self.assertAlmostEqual(cruise_budget(288,.1,40/3),245.8666666666667)
    def test_range_identity(self):
        self.assertAlmostEqual(range_km(259.2,108,54),129.6)
    def test_invalid(self):
        for args in [(0,100,54),(100,float('nan'),54)]:
            with self.assertRaises(ValueError):range_km(*args)
        with self.assertRaises(ValueError):cruise_budget(288,.1,300)
    def test_hover_scaling(self):
        self.assertAlmostEqual(ideal_hover_w(4)/ideal_hover_w(2),2**1.5)
        self.assertGreater(ideal_hover_w(2.9),300)
if __name__=='__main__':unittest.main()
