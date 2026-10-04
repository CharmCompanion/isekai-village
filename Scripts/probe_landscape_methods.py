import unreal

for cls_name in ["Landscape", "LandscapeProxy", "ProceduralFoliageEditorLibrary", "InstancedFoliageActor"]:
    cls = getattr(unreal, cls_name, None)
    print(f"\n=== {cls_name} methods ===")
    if not cls:
        print("MISSING")
        continue
    for m in sorted(dir(cls)):
        if not m.startswith("_") and ("layer" in m.lower() or "grass" in m.lower() or "foliage" in m.lower() or "weight" in m.lower() or "import" in m.lower() or "paint" in m.lower()):
            print(f"  {m}")
