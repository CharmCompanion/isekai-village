> Current status (2026-10-07): BodyA and HeadA_01 are confirmed by the user. Reference rendering and FBX exports are complete. Fifteen editable rigged Blender monster models and 75 starter animation exports are authored in ArtSource/Monsters/Models_v01. See that folder's README and Docs/Monster_Model_Handoff.md for current Unreal verification and remaining production work. The older inspection findings below are historical and do not require another player confirmation.
# IsekaiVillage monster art brief

Status: four visual concept sheets completed, representing fifteen proposed variants. See `ArtSource/Monsters/Concepts/MONSTER_DESIGNS.md` for the gallery and remaining production work. No creature meshes, texture maps, rigs, animations or playable enemies have been authored yet. The user explicitly confirmed the StylizedCharacters BodyA player as the reference. The question about playable 3D versus illustrations remains unanswered; do not describe these concepts as playable content.

## User request

Create slimes of different types, skeletons of different classes, goblins, and ogres. All must match the user's character and existing game art. Preserve the existing world and reuse appropriate project assets.

## Verified project references

- Project: `D:\DEVELOPMENT\Games\IsekaiVillage\IsekaiVillage.uproject`, engine association 5.8.
- `Docs/FAB_LINKS.md` records `MageSet01` and `StylizedCharacters` as the BodyA mage appearance.
- `Source/IsekaiVillage/OverworldCharacter.cpp` loads `/Game/StylizedCharacters/BodyA/Body/SKM_BodyA` and the modular `/Game/StylizedCharacters/BodyA/Heads/Head_01/SKM_HeadA_01`.
- `Source/IsekaiVillage/IsekaiVillageCharacter.cpp` still defaults to Manny. Blueprint overrides may change the actual appearance, so source alone does not confirm the final player look.
- Potential player Blueprints include `/Game/IsekaiVillage/Input/BP_OverworldCharacter`, `/Game/IsekaiVillage/Input/BP_ThirdPersonCharacter`, and `/Game/SpellCraft/Blueprints/Character/BP_MageCharacter`.
- `AOverworldMonsterAvatar` already provides patrol, chase, stun, and encounter triggering. It currently loads a human BodyA placeholder. This is an integration point, not an existing creature model or complete combat AI.
- `/Game/IsekaiVillage/ABP/ABP_IsekaiEnemy` exists; inspect its skeleton compatibility before reuse.
- Installed outfit and equipment libraries include MageSet01 and WarriorSet01. Animation libraries include CloseCombatAnimSet, CombatMagicAnims, Attaku, and the Motifect Fantasy/Magic pack. Retargeting and licensing compatibility must be checked rather than assumed.
- A filename inspection did not identify dedicated slime, goblin, or ogre meshes. Animation skeleton assets are rig definitions, not skeletal undead enemies. Basic_VFX is effects content and does not establish that slime models exist.

## Proposed first roster — editable, not claimed GDD requirements

| Family | Proposed variants | Visual distinction |
| --- | --- | --- |
| Slime | Meadow, water, flame, frost, poison, crystal | Body silhouette, embedded core, surface treatment and accents as well as color |
| Skeleton | Fighter, shield knight, archer, mage | Bone body shared where appropriate; distinct equipment, stance and readable class silhouette |
| Goblin | Scout, fighter, shaman | Pointed ears, expressive faces, light equipment; distinct role silhouettes |
| Ogre | Brute, armored champion | Broad heavy anatomy, readable exaggerated hands and face; convincing body mass and weight |

## Art and production requirements

Match the confirmed player's proportions, face language, palette, material response and texture detail. Inspect the character visually under neutral lighting and in the current world before declaring a match. Smooth sculpted stylized forms, clear shapes at gameplay distance, and coherent cloth/leather/metal/bone surfaces should carry the family resemblance. Avoid realistic horror detailing or visibly crude primitive assemblies.

For a playable 3D deliverable, author editable Blender sources, UVs and texture maps, deformation rigs, weights, skeletal mesh exports and Unreal assets. Provide idle, movement, attack, hit and death animation coverage; slimes also need squash/stretch. Adapt humanoid animation libraries only where anatomy and rig mapping support it. Test equipment attachment, bounds, collision, foot contact, deformation, and animation transitions. Place previews in a separate monster review map before populating the existing world.

A rendered illustration is a concept reference, not a game-ready model. An imported static mesh is not a rigged playable enemy. Report each milestone accurately.

## Next steps

1. BodyA is now confirmed by the user. Render the real BodyA and HeadA_01 under neutral lighting as the visual reference. Do not ask the user to identify the player again.
2. Visually inspect/export that character and its materials; inspect the existing enemy animation Blueprint.
3. Establish one finished slime and one humanoid creature as style and deformation benchmarks, then extend the families consistently.
4. Keep new authored content under `/Game/IsekaiVillage/Monsters` and editable sources in a dedicated project art-source folder. Do not replace installed pack assets or modify the world map merely to create a preview.

## Player inspection findings, 2026-10-07

The user clarified: use the character model already used for the player.

Read-only Unreal inspection saved `Saved/MonsterArtReference/player_audit.json`. Both Map_Village and Map_AnimeAdventure have no explicit world-settings GameMode override and no placed Character actors. Config defaults Map_Village to IsekaiVillageGameMode, whose C++ default pawn is IsekaiVillageCharacter with Manny. The separate OverworldCharacter code forces BodyA at BeginPlay; its Blueprint CDO has a null main mesh and the separate HeadA_01, using MI_Eyes_01_a and MI_HeadA_01_a. Therefore a null Blueprint main mesh does not mean the overworld has no visible body. BP_ThirdPersonCharacter instead references the SoStylized UE4 mannequin. The old BP_MageCharacter fails to load its obsolete SpellCraft parent.

The project therefore contains different player appearances across configurations. Confirm the user's intended currently played appearance before claiming a visual match. A screenshot of the player in-game can resolve this directly if the intended mode remains ambiguous.

The metadata report was written successfully. An attempted subsequent reference FBX export under -nullrhi caused an engine assertion and the dedicated inspection process exited; no maps or Content assets were saved. The export step has been removed from the audit script. Visual inspection and reference export remain unfinished.

