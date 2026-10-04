import unittest
from settlement_grid import SettlementGrid

class ConstructionRules(unittest.TestCase):
    def setUp(self):self.g=SettlementGrid()
    def test_every_reservation_is_buildable_in_its_era(self):
        for p in self.g.plan['reservations']:
            ok,reason,_=self.g.validate(p['type'],p['anchor'],p['era'],reservation=p['id'])
            self.assertTrue(ok,(p['id'],reason))
    def test_landmark_locked_before_kingdom(self):
        p=next(p for p in self.g.plan['reservations'] if p['type']=='Castle')
        self.assertFalse(self.g.validate('Castle',p['anchor'],'Village',reservation=p['id'])[0])
    def test_occupancy_and_release(self):
        p=self.g.plan['reservations'][0];kw=dict(era=p['era'],reservation=p['id'])
        self.assertTrue(self.g.occupy('one',p['type'],p['anchor'],**kw)[0])
        self.assertFalse(self.g.occupy('two',p['type'],p['anchor'],**kw)[0])
        self.g.release('one');self.assertTrue(self.g.validate(p['type'],p['anchor'],**kw)[0])
    def test_wrong_building_and_public_land_rejected(self):
        p=next(p for p in self.g.plan['reservations'] if p['type']=='Chapel')
        self.assertFalse(self.g.validate('CommonerHouse',p['anchor'],reservation=p['id'])[0])
        self.assertFalse(self.g.validate('CommonerHouse',self.g.world_to_cell(0,0))[0])
        self.assertFalse(self.g.validate('CommonerHouse',(-1,-1))[0])
    def test_reserved_plots_do_not_overlap(self):
        ids=[c for p in self.g.plan['reservations'] for c in p['cells']]
        self.assertEqual(len(ids),len(set(ids)))

if __name__=='__main__':unittest.main()
