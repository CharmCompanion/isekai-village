from pathlib import Path
import json,traceback,unreal as u
r=Path('D:/DEVELOPMENT/Games/Tower of Elrhun')
try:
 setup=json.loads((r/'Saved/native_weapon_setup.json').read_text())
 for body in ['BodyA','BodyB']:
  anim=u.load_asset(setup['animations'][body+'_Ranger']['Action2']);duration=anim.get_play_length();assert u.GolemClothTools.set_equipment_curve(anim,'ElrhunBowDraw',[float(p*duration) for p in [0,.065,.08,.25,1]],[1.,1.,0.,0.,0.]);assert u.EditorAssetLibrary.save_loaded_asset(anim,only_if_is_dirty=False)
 (r/'Saved/native_clearance_release_setup.json').write_text(json.dumps({'success':True,'release_before_finger_opening':True},indent=2))
 p=r/'Scripts/playtest_native_clipping_fixes.py';exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__'})
except Exception:(r/'Saved/native_clearance_release_error.txt').write_text(traceback.format_exc());raise
