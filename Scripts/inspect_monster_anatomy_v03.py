from pathlib import Path
src=Path(__file__).with_name('build_monsters_v02.py').read_text().split("for role in ['Fighter','Knight','Archer','Mage']:")[0]
src=src.replace("Models_v02","Models_v03").replace("_v02","_v03")
exec(compile(src,'foundation','exec'))
import bmesh
out={}
for family in ['Goblin','Ogre']:
    arm=imported_humanoid(family+'Test',family)
    rows=[]
    for o in parts[:2]:
        bm=bmesh.new();bm.from_mesh(o.data)
        boundary=[v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
        neck=[v for v in boundary if abs(v.co.x)<(.28 if family=='Ogre' else .13) and abs(v.co.z-bonepos(arm,'neck_01').z)<(.3 if family=='Ogre' else .15)]
        rows.append({'name':o.name,'bounds':[[min(v.co[k] for v in o.data.vertices),max(v.co[k] for v in o.data.vertices)] for k in range(3)],'boundary':len(boundary),'neck':[list(v.co) for v in neck]})
        bm.free()
    out[family]={'parts':rows,'head_bone':list(bonepos(arm,'head')),'neck_bone':list(bonepos(arm,'neck_01')),'calf':list(bonepos(arm,'calf_r')),'foot':list(bonepos(arm,'foot_r'))}
    for o in list(parts):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.objects.remove(arm,do_unlink=True)
(ROOT.parents[1]/'Saved/monster_anatomy_v03.json').write_text(json.dumps(out,indent=2))
