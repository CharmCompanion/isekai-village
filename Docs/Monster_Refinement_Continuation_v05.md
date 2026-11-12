# Monster refinement checkpoint — 2026-10-08

## User request and art direction

Continue actual 3D humanoid enemy refinement in IsekaiVillage. The user says the enemies still look rough and repeatedly rejects stopping after small cosmetic changes. Match the BodyA player and an original Korean action-fantasy manhwa enemy style, with Solo Leveling as a tonal reference. All six approved elemental slimes are excluded from further changes.

Roster: Skeleton Fighter/Knight/Archer/Mage; Goblin Scout/Fighter/Shaman; Ogre Brute/Champion. Do not revise the island/world for this task. Do not substitute illustrated concept sheets for finished game meshes.

## Saved actual work

Latest sources: `ArtSource/Monsters/Models_v05`. Separate native assets and review map: `/Game/IsekaiVillage/Monsters/Refined_v05/Maps/Map_MonsterReview_v05`. Existing v01-v04 revisions and installed packs are retained. Gameplay enemy classes have not been redirected to the new meshes.

v05 reconstructs skull anatomy, jaw/dentition/orbits, flatter rib forms, long-bone condyles and skeletal gripping fingers. Ogre hair is now scalp-fitted swept pointed clumps. Equipment has tapered chest armor, fitted trim, chased heraldry, belt holes and stitched tasset hems. Every humanoid has its own 2048 color/AO map and an additional UV channel; player-derived normals remain on UV0. Head normals are 0.22, body normals 0.48. Blender and native material response are synchronized. Neutral studio lighting and directional comparison views are saved separately.

## Verified evidence

- `ArtSource/Monsters/Models_v05/source_validation.json`: passed, nine models and 45 clips; units, normalized weights, single roots, original and authored UV channels, texture presence and finite evaluated deformations.
- `Saved/monster_import_v05.json`: complete, nine meshes, 45 animation sequences, no recorded import errors; SkeletonKnight/OgreChampion trim subsequently corrected and reimported.
- `Saved/monster_unreal_validation_v05.json`: passed, three decreasing LODs per mesh, correct animation skeletons, and individual color-map assignments checked for every material slot.
- `Saved/monster_render_v05.json`: twelve final native views complete.
- `Previews/motion_render_report.json`: six representative Blender motion views. These are deformation samples, not an animation-quality certificate.
- `Saved/slime_preservation_v05.json`: all 71 tracked approved slime/shared-material files unchanged by SHA256.

## Art defects still visible

The actual native models remain below the requested finished AAA target. Do not confuse technical checks with visual acceptance. Ogre hair clumps remain too orderly. Creature lower faces show strong dark chin/mouth bands; inspect geometry, original UV shading and normals in close-up before further ornament. Skeleton ribs and spine still read as repeated constructions, despite the better skull. Equipment silhouettes/materials and costume identity need a coherent character-art pass. Hand contact, left-hand fist shape, extreme armor deformation, foot planting and attack timing need more polish. Some native LOD reduction logs warn about edges shared by more than two triangles; topology has not received a full manifold/intersection audit.

Do not report this checkpoint as accepted AAA art. The next meaningful work should establish a close-up creature anatomy and costume benchmark, then carry it across the roster, rather than adding more small decorative strips to the current forms.

## Safe continuation

Read this file, `Monster_Production_Art_Target.md`, the v05 README and the actual native/source previews first. Preserve the current sources before destructive regeneration. The full builder chain is v01 → v02 → v03 → v04 → v05; each later builder loads earlier function definitions and overrides them. A complete new build must precede unique surface baking. The standalone trim repair reads dedicated pre-repair backups and must not be run on newly generated models, whose builder now already fits the trim.

Persistent Unreal runner: `Scripts/monster_editor_session.py`. Launch with `-ExecCmds="py D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/monster_editor_session.py"`; `-ExecutePythonScript` exits after the script. The runner has a reentrancy guard and reads new requests from `Saved/monster_request.json`. Latest issued request is id 42, native v05 validation. Use a new id and wait for ongoing imports/captures before dependent changes. Launched editor PID is recorded in `Saved/monster_editor_v05_pid.txt`; do not close unrelated editor sessions.
