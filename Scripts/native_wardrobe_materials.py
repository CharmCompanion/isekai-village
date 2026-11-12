import unreal as u,hashlib
BASE='/Game/Elrhun/Golems/PlayerBody/Materials';A=u.EditorAssetLibrary;M=u.MaterialEditingLibrary;T=u.AssetToolsHelpers.get_asset_tools();material_cache={};instance_cache={};CLOTH_ROOTS=set()
PALETTES={'Tank':(.32,.38,.50),'Mage':(.18,.36,.78),'Ranger':(.24,.38,.16),'Healer':(.88,.80,.60),'Necromancer':(.13,.035,.22),'Evil_Crimson':(.28,.035,.045),'Evil_Blight':(.20,.29,.045),'Evil_Void':(.045,.018,.09)}
GLOW={'Tank':(1,.025,.01),'Mage':(.015,.16,1),'Ranger':(.015,.8,.06),'Healer':(1,.65,.025),'Necromancer':(.5,.015,.9),'Evil_Crimson':(1,.005,.025),'Evil_Blight':(.2,.8,.015),'Evil_Void':(.25,.005,.7)}
def wardrobe_material_hash(path):return hashlib.sha1(path.encode()).hexdigest()[:10]
def connect(a,b,pin='',output=''):
 ins=list(M.get_material_expression_input_names(b))
 wanted=pin.replace(' ','').replace('_','').lower()
 name=next((n for n in ins if n.replace(' ','').replace('_','').lower()==wanted),ins[0] if len(ins)==1 else pin)
 assert M.connect_material_expressions(a,output,b,name),(a.get_class().get_name(),b.get_class().get_name(),name,ins)
def glow_root(source):
 path=source.get_path_name()
 if path in material_cache:return material_cache[path]
 name='M_SoulCloth_'+wardrobe_material_hash(path);dest=BASE+'/Parents/'+name;mat=A.load_asset(dest)
 if mat:
  prop=u.MaterialProperty.MP_MATERIAL_ATTRIBUTES if mat.get_editor_property('use_material_attributes') else u.MaterialProperty.MP_EMISSIVE_COLOR
  stack=[M.get_material_property_input_node(mat,prop)];seen=set();complete=False
  while stack:
   e=stack.pop()
   if e is None or e.get_path_name() in seen:continue
   seen.add(e.get_path_name())
   if isinstance(e,u.MaterialExpressionScalarParameter) and str(e.get_editor_property('parameter_name'))=='ELR_GlowStrength':complete=True;break
   stack.extend(M.get_inputs_for_material_expression(mat,e))
  if complete:
   if path in CLOTH_ROOTS:
    M.set_material_usage(mat,u.MaterialUsage.MATUSAGE_CLOTHING);A.save_loaded_asset(mat,only_if_is_dirty=False)
   material_cache[path]=mat;return mat
  assert dest.startswith(BASE+'/Parents/');assert A.delete_asset(dest);mat=None
 mat=T.duplicate_asset(name,BASE+'/Parents',source);assert mat
 def node(cls,x,y):return M.create_material_expression(mat,cls,x,y)
 def param(cls,name,value,x,y):
  n=node(cls,x,y);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',value);return n
 pos=node(u.MaterialExpressionPreSkinnedPosition,-1800,800);interpolator=node(u.MaterialExpressionVertexInterpolator,-1600,800);connect(pos,interpolator,'Input')
 center=param(u.MaterialExpressionVectorParameter,'ELR_GlowCenterLS',u.LinearColor(0,14,139.5,0),-1600,1000);distance=node(u.MaterialExpressionDistance,-1400,800);connect(interpolator,distance,'A');connect(center,distance,'B')
 radius=param(u.MaterialExpressionScalarParameter,'ELR_GlowRadius',7.,-1400,1000);divide=node(u.MaterialExpressionDivide,-1200,800);connect(distance,divide,'A');connect(radius,divide,'B')
 one=node(u.MaterialExpressionOneMinus,-1000,800);connect(divide,one,'Input');clamp=node(u.MaterialExpressionSaturate,-800,800);connect(one,clamp,'Input');smooth=node(u.MaterialExpressionMultiply,-600,800);connect(clamp,smooth,'A');connect(clamp,smooth,'B')
 color=param(u.MaterialExpressionVectorParameter,'ELR_GlowColor',u.LinearColor(.015,.16,1,1),-800,1000);tint=node(u.MaterialExpressionMultiply,-400,800);connect(smooth,tint,'A');connect(color,tint,'B')
 strength=param(u.MaterialExpressionScalarParameter,'ELR_GlowStrength',1.2,-600,1150);glow=node(u.MaterialExpressionMultiply,-200,800);connect(tint,glow,'A');connect(strength,glow,'B')
 if mat.get_editor_property('use_material_attributes'):
  old=M.get_material_property_input_node(mat,u.MaterialProperty.MP_MATERIAL_ATTRIBUTES);oldout=M.get_material_property_input_node_output_name(mat,u.MaterialProperty.MP_MATERIAL_ATTRIBUTES);assert old
  br=node(u.MaterialExpressionBreakMaterialAttributes,0,1150);connect(old,br,'MaterialAttributes',oldout)
  add=node(u.MaterialExpressionAdd,200,800);connect(br,add,'A','EmissiveColor');connect(glow,add,'B')
  setter=node(u.MaterialExpressionSetMaterialAttributes,400,800);setter.set_editor_property('attribute_set_types',[u.Guid(0xB769B54D,0xD08D4440,0xABC21BA6,0xCD27D0E2)]);connect(old,setter,'MaterialAttributes',oldout);connect(add,setter,'EmissiveColor');assert M.connect_material_property(setter,'',u.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
 else:
  old=M.get_material_property_input_node(mat,u.MaterialProperty.MP_EMISSIVE_COLOR);output=M.get_material_property_input_node_output_name(mat,u.MaterialProperty.MP_EMISSIVE_COLOR)
  if old:
   add=node(u.MaterialExpressionAdd,200,800);connect(old,add,'A',output);connect(glow,add,'B');glow=add
  assert M.connect_material_property(glow,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
 
 if path in CLOTH_ROOTS:M.set_material_usage(mat,u.MaterialUsage.MATUSAGE_CLOTHING)
 M.recompile_material(mat);A.save_loaded_asset(mat,only_if_is_dirty=False);material_cache[path]=mat;return mat
def glow_source(source):
 path=source.get_path_name()
 if path in instance_cache:return instance_cache[path]
 if isinstance(source,u.Material):return glow_root(source)
 parent=glow_source(source.get_editor_property('parent'));name='MI_SoulClothSource_'+wardrobe_material_hash(path);dest=BASE+'/Sources/'+name;mi=A.load_asset(dest) or T.duplicate_asset(name,BASE+'/Sources',source);M.set_material_instance_parent(mi,parent);A.save_loaded_asset(mi,only_if_is_dirty=False);instance_cache[path]=mi;return mi
def wardrobe_material(sourcepath,body,role,center,glow=True):
 source=u.load_asset(sourcepath);parent=glow_source(source) if glow else source;name='MI_'+body+'_'+role+'_'+wardrobe_material_hash(sourcepath);mi=A.load_asset(BASE+'/Classes/'+name) or T.create_asset(name,BASE+'/Classes',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew());M.set_material_instance_parent(mi,parent)
 names=[str(n) for n in M.get_vector_parameter_names(source)];tint=[n for n in names if any(x in n.lower() for x in ['color','colour','tint','top','coat','cloth','armor','pants','dress','skirt']) and not any(x in n.lower() for x in ['skin','hair','eye','outline','rim','specular','shadow','button','buckle','chain','metal','lacing','emiss','glow'])]
 if '/Golems/Materials/' in sourcepath:tint=[]
 for i,n in enumerate(tint):
  c=PALETTES[role]
  if i%2:c=tuple(v*.65 for v in c)
  M.set_material_instance_vector_parameter_value(mi,n,u.LinearColor(*c,1))
 M.set_material_instance_vector_parameter_value(mi,'ELR_GlowColor',u.LinearColor(*GLOW[role],1));M.set_material_instance_vector_parameter_value(mi,'ELR_GlowCenterLS',u.LinearColor(*center,0));M.set_material_instance_scalar_parameter_value(mi,'ELR_GlowStrength',1.2);M.set_material_instance_scalar_parameter_value(mi,'ELR_GlowRadius',7.)
 A.save_loaded_asset(mi,only_if_is_dirty=False);return mi
