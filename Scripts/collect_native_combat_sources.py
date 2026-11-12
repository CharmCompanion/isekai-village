out=r/'ArtSource/Golems/NativeMotion';manifest=json.loads((out/'manifest.json').read_text())
for path in ['/Game/CombatMagicAnims/Animations/AS_CastSpell','/Game/CombatMagicAnims/Animations/AS_StaffStrike+CastSpell','/Game/CloseCombatAnimSet/Animations/InPlace/Attacks/NinjaLeftJab','/Game/CloseCombatAnimSet/Animations/InPlace/Attacks/NinjaRightCross']:
 anim=u.load_asset(path);assert anim,path;manifest['combat'][path]={'skeleton':anim.get_editor_property('skeleton').get_path_name(),'duration':anim.get_play_length()}
manifest['success']=True;manifest.pop('error',None);(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
p=r/'Scripts/retarget_native_motion_checks.py';exec(compile(p.read_text(),str(p),'exec'),globals())
