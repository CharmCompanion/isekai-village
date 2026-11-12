import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');built=json.loads((r/'ArtSource/Golems/NativeWardrobe/Built/build_report.json').read_text());changed={}
for body in ['BodyA','BodyB']:
 key=body+'_Healer';mesh=u.load_asset('/Game/Elrhun/Golems/PlayerBody/Outfits/SK_Native_'+key);specs=built['outfits'][key]['materials'];names=[str(s.material_slot_name) for s in mesh.get_editor_property('materials')];physics=mesh.get_editor_property('physics_asset');u.GolemClothTools.reset_cape_cloth(mesh);sections=json.loads(u.GolemClothTools.inspect_clothing(mesh))['sections']
 for section in sections:
  name=names[section['material']]
  if specs.get(name,{}).get('coat',False):assert u.GolemClothTools.create_cape_cloth(mesh,section['section'],physics,100.,1.)
 u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False);changed[key]={'coat_tail_maximum_movement_cm':1.,'upper_coat_pinned':True,'physics':physics.get_path_name()}
(r/'Saved/native_coat_motion_tuning.json').write_text(json.dumps({'success':True,'changes':changed},indent=2))
