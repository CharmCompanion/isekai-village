"""Engine-independent construction rules for the saved settlement plan.

This is a logical/editor foundation. Gameplay UI, costs and save-game integration
are separate systems; they must call equivalent rules when construction is wired.
"""
import json
from pathlib import Path

DEFAULT=Path(__file__).resolve().parents[1]/'Content/IsekaiVillage/AdventureWorld/Design/SettlementGrid.json'
class SettlementGrid:
    def __init__(self,path=DEFAULT):
        self.plan=json.loads(Path(path).read_text())
        self.cells={(c['i'],c['j']):c for c in self.plan['cells']}
        self.reserved={p['id']:p for p in self.plan['reservations']}
        self.occupied={}
    def world_to_cell(self,x_m,y_m):
        import math
        x,y=self.plan['origin'];s=self.plan['cell_size']
        return math.floor((x_m-x)/s),math.floor((y_m-y)/s)
    def validate(self,building,anchor,era='Village',rotation=0,reservation=None):
        if building not in self.plan['catalogue']:return False,'unknown building',[]
        if era not in self.plan['eras']:return False,'unknown era',[]
        if rotation not in (0,90,180,270):return False,'rotation must be a quarter turn',[]
        spec=self.plan['catalogue'][building]
        if self.plan['eras'].index(era)<self.plan['eras'].index(spec['era']):return False,'era locked',[]
        if reservation:
            plot=self.reserved.get(reservation)
            if not plot or plot['type']!=building:return False,'wrong reserved building',[]
            if tuple(anchor)!=tuple(plot['anchor']):return False,'reserved anchor mismatch',[]
        w,d=spec['cells']
        if rotation in (90,270):w,d=d,w
        keys=[(anchor[0]+x,anchor[1]+y) for x in range(w) for y in range(d)]
        for key in keys:
            c=self.cells.get(key)
            if c is None:return False,'outside grid',[]
            if key in self.occupied:return False,'occupied',[]
            if c['status']=='reserved':
                if c.get('reservation')!=reservation:return False,'reserved for another plot',[]
            elif c['status']!='available':return False,c['status'],[]
        heights=[self.cells[k]['center'][2] for k in keys]
        if max(heights)-min(heights)>max(4,w*1.3):return False,'foundation relief exceeded',[]
        return True,'valid',keys
    def occupy(self,instance_id,building,anchor,**options):
        if instance_id in self.occupied.values():return False,'duplicate instance id'
        ok,reason,keys=self.validate(building,anchor,**options)
        if ok:self.occupied.update({k:instance_id for k in keys})
        return ok,reason
    def release(self,instance_id):
        self.occupied={k:v for k,v in self.occupied.items() if v!=instance_id}

