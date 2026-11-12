"""Tone new Gosain-only foliage and rock instances to match the ground."""
import unreal,json,math,time,shutil
from pathlib import Path
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');O=B/'ArtSource/World/Gosain59';D='/Game/IsekaiVillage/AdventureWorld/Gosain59';A=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert (O/'applied.json').exists() and not (O/'palette_applied.json').exists();data=json.loads((O/'understory.json').read_text());cache={};fts=[];old=[];bounds=[];groups=[[] for a in data['assets']];inactive=[]
backup=B/'Saved/WorldBackups'/('BeforeGosain59Palette_'+time.strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True);shutil.copy2(B/'Content/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure.umap',backup/'Map_AnimeAdventure.umap')
for i,q in enumerate(data['assets']):
 ft=unreal.load_asset(D+'/Foliage/FT_Gosain59_'+q['key']);assert ft;fts.append(ft);old.append(list(ft.get_editor_property('override_materials')));mesh=unreal.load_asset(q['path']);box=mesh.get_bounding_box();bounds.append((box.min,box.max));mats=[]
 for slot in mesh.static_materials:
  src=slot.material_interface;key=src.get_path_name()
  if q['key'] in ['grass1','grass2','stone','outcrop']:
   if key not in cache:
    dst=D+'/Materials/MI_Gosain59_'+src.get_name();mat=unreal.load_asset(dst) if A.does_asset_exist(dst) else A.duplicate_asset(key.split('.')[0],dst)
    if q['key'].startswith('grass'):
     vectors={'Base Color':(.07,.16,.045,1),'Offgrass Color':(.10,.13,.035,1)};scalars={'Tip Brightness':.04,'Tip Desaturation':.12,'Tip Hue Shift':-.01,'Wind Color Boost':1.,'Emissive Strength':0.}
    else:
     vectors={'Rock Tint':(.75,.77,.69,1),'Moss Color':(.045,.11,.025,1),'Moss Color 2':(.025,.075,.018,1)};scalars={'Moss Multiply':1.4,'Rock Scale':450.,'Metallic':0.,'Specular':.12}
    for name,value in vectors.items():
     M.set_material_instance_vector_parameter_value(mat,name,unreal.LinearColor(*value));actual=M.get_material_instance_vector_parameter_value(mat,name);matches=all(abs(x-y)<1e-5 for x,y in zip(value,[actual.r,actual.g,actual.b,actual.a]))
     if not matches:inactive.append([mat.get_name(),name])
     if name=='Base Color':assert matches,'Active grass base color did not update'
    for name,value in scalars.items():
     M.set_material_instance_scalar_parameter_value(mat,name,value)
     if abs(M.get_material_instance_scalar_parameter_value(mat,name)-value)>1e-4:inactive.append([mat.get_name(),name])
    M.update_material_instance(mat);A.save_loaded_asset(mat);cache[key]=mat
   mats.append(cache[key])
  else:mats.append(src)
 ft.set_editor_property('override_materials',mats);A.save_loaded_asset(ft)
for i,x,y,z,yaw,height in data['instances']:
 i=int(i);lo,hi=bounds[i];scale=height*100/(hi.z-lo.z);angle=math.radians(yaw);cx=(lo.x+hi.x)*.5*scale;cy=(lo.y+hi.y)*.5*scale;groups[i].append(unreal.Transform(location=unreal.Vector(x*100-cx*math.cos(angle)+cy*math.sin(angle),y*100-cx*math.sin(angle)-cy*math.cos(angle),z*100-lo.z*scale),rotation=unreal.Rotator(pitch=0,yaw=yaw,roll=0),scale=unreal.Vector(scale,scale,scale)))
try:
 for ft,rows in zip(fts,groups):unreal.InstancedFoliageActor.remove_all_instances(W,ft);unreal.InstancedFoliageActor.add_instances(W,ft,rows)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
 for ft,mats in zip(fts,old):ft.set_editor_property('override_materials',mats);A.save_loaded_asset(ft)
 raise
(O/'palette_applied.json').write_text(json.dumps({'status':'saved','backup':str(backup),'materials':[m.get_path_name() for m in cache.values()],'source_pack_assets_unchanged':True,'instance_transforms_retained':True,'inactive_optional_parameters_retained':inactive},indent=2))
