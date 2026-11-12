import unreal as u,json
from pathlib import Path
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun');setup=json.loads((r/'Saved/native_weapon_setup.json').read_text());report={'success':False,'animations':{}}
for key,clips in setup['animations'].items():
 body,role=key.split('_',1)
 for label,path in clips.items():
  anim=u.load_asset(path);ground=role in ['Tank','Ranger'] and label in ['Ready','Action1','Action2'];assert u.GolemClothTools.normalize_equipment_root(anim,label!='Ready',ground),(key,label);assert u.EditorAssetLibrary.save_loaded_asset(anim,only_if_is_dirty=False);report['animations'][key+'_'+label]={'path':path,'neutral_root':True,'preserved_body_height':True,'grounded_feet':ground}
report['success']=True;(r/'Saved/native_weapon_root_correction.json').write_text(json.dumps(report,indent=2))
