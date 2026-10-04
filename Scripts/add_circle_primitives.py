"""
Adds the generator-derived primitive function graphs to BP_ProceduralMagicCircle
(Docs/magic_circle_system.md sections 3-4).

Run with the editor CLOSED:
  UnrealEditor-Cmd.exe SpellCraft.uproject -run=pythonscript ^
     -script="F:\DEVELOPMENT\Games\SpellCraft\Scripts\add_circle_primitives.py"

Idempotent. Graph bodies still have to be built in-editor -- UE 5.8 exposes no
node-spawn API to Python.
"""
import unreal

BEL = unreal.BlueprintEditorLibrary
CIRCLE = "/Game/SpellCraft/Blueprints/MagicCircle/BP_ProceduralMagicCircle"

# Each maps to one toggle/primitive in the reference renderer.
NEW_FUNCTIONS = [
    "BuildPointList",      # getPoint + rotMat  (renderer.js:2274, 2313)
    "ConnectPoints",       # chords, skip-aware (renderer.js:1938)
    "ConnectBorder",       # arcs along border
    "ConnectMidPoints",    # chords between edge midpoints
    "LinesToCenter",       # radial spokes
    "InscribePoints",      # small circles at points
    "GetShapeForElement",  # ElementSymmetry / ElementSkip lookup
    "RebuildCircle",       # orchestrator: calls the above per toggle
]

bp = unreal.load_asset(CIRCLE)
report = []

existing = {str(n) for n in BEL.list_graph_names(bp)}
for fn in NEW_FUNCTIONS:
    if fn in existing:
        report.append(f"skip {fn} (exists)")
        continue
    graph = BEL.add_function_graph(bp, fn)
    report.append(f"{'add ' if graph else 'FAIL'} {fn}")

BEL.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp)

report.append("")
report.append("graphs now on BP_ProceduralMagicCircle:")
for n in sorted(str(x) for x in BEL.list_graph_names(bp)):
    report.append(f"  {n}")

with open("F:/DEVELOPMENT/Games/SpellCraft/Scripts/primitives_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print("done")
