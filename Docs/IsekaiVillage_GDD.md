# Isekai Village - GDD v1.0 (New Game, UE 5.8.1)
> Copied from SpellCraft `F:\DEVELOPMENT\Games\SpellCraft` -> `F:\DEVELOPMENT\Games\IsekaiVillage` 2026-08-27. SpellCraft remains untouched.
> This doc is the single source of truth. All prior `Docs/unreal_anime_mage_master_spec.md` / `cursor_migration_context.md` are **archived** - new magic has no `GrimoirePage` deck, no `CompileHandConfig` `Q/E` fusions, no `ElementFatigue/Density/EnvAffinity`.

## 1. High Concept
Isekai reincarnated villager. Slice-of-life 20min day (farm/craft/shop/inn) -> weekly horde from hidden dungeon (forest/mountain/waterfall sealed 15-20yrs, barrier thins). Loop: `Day tasks (short missions) -> Trust/SP -> Sphere Grid -> Weekly Horde -> Town grows Village -> Large Town (Barons Rank B quests) -> End: Expedition clear dungeon core -> Postgame: Design dungeon + Kingdom DLC`.
Think `Tales of Symphonia artes` + `Adventure Quest 64 +1 stats` + `Farming Life` tool, not `Loner Life` titles.

## 2. Core Loop & Pacing
- Day 6am-6pm: 3-4 short missions `Billy Hatcher` style `Fetch 5 logs / Repair wall 30% / Cook 3` `+1 SP +5 Trust` `WBP_Shop` board.
- Night: regen, inn sleep/food `ECONOMY` handles.
- Week: 1 horde `4min` `Basic_VFX` slimes, scales `15 -> 40` mixed, week 13 `2/week`. `Large Town` adds `Baron` Rank B quests.
- Endgame: Expedition finds waterfall cave `IslandTerrainActor.cpp:TowerPlateau 2000,0,450` behind mountain ridge, clear core -> unlock `DUNGEON MASTER` edit.

## 3. Party / Reserve (No Grimoire)
- Start solo `AIsekaiVillageCharacter` `Source/IsekaiVillage/IsekaiVillageCharacter.h` (renamed from `SpellCraftCharacter`).
- `UPartyReserve 6` `TArray<FHiredAdventurer> Reserve` - hire `+1` early (`Party 2`), `+3` late (`Party 4` with you). Via `NPC Guild Master` desk `AdvancedVillagePack/Blueprints`. Not a deck.
- Rampage: `if Reserve==6 spawn 6` `GetAllActorsOfClass` assist `OrbitShield` style. Urgent = `Assign 2-3 + you`.
- Guild buys `monster parts` `Gald +`, adventurers `Rank D->B` on quests/rampages. You feed `Inn` `ApplySelfHeal` food, gear `Blacksmith` `MageSet01`, supplies `Shop` `ECONOMY`.

## 4. Sphere Grid - 7 Main + 4 DLC = 11 discs (FFX Expert 70% stat / 30% skill)
`USphereGridDataAsset : UPrimaryDataAsset` like `USpellVisualDataAsset.h` `TMap<FName,FSphereNode>`. `FFX` `792 vs 860 nodes` ~70% `+HP/TP` stats.

### Center Flips (Coin)
- `CENTER A 14 Life` front `+10 HP x4, +10 TP x3, +5 Inv x3, Carry +8kg x2, Move 3% x2` `= +40HP/+30TP/+15Inv`. Fill 14 -> flip keeps stats -> `ADVENTURER 14` back `Dash/Hunt/Danger Sense`. You remain adventurer (not Guild Master NPC).
- `CENTER B 14 Work` front `Yield/Carry/Build` -> flip -> `VILLAGER 14 Regal` brawler `Jab/Double Kick/Hawk Smash small MealWeaponAura 0.6 / Tool Demon Fang projectile TP12` `CombatMagicAnims AS_FireballCharge` skeleton. Must fill whole 14, not cut-through to MELEE.

### Combat Main 3
- **MELEE Lloyd** 12 `Sword Rain->Sonic Thrust->Beast` `+2 Atk` stats `x8 stat /4 skill`
- **MAGIC Genis** 12 `Fireball/Wind Blade/Stone Blast/Spread Fan 14°` 4 elements only `TP 12/25` `SpellProjectile.cpp:BaseSpeed 1800` `+2 Magic`
- **CLERIC Raine** 10 `Heal 25->40 ApplySelfHeal / Barrier Block 70 OrbitShield / Revive`

### Town Main 3
- **CRAFTING** 10 `Repair 50% faster / Craft wood sword / +Inv`
- **DOMAIN** 10 `Patrol speed / Gate HP +15% / Trust +5` `EarthWallConstruct Lifetime 12->18`
- **ECONOMY+Hospitality merged** 14 `Shop Lv1 Haggle -10%/+10% / Inn Revive -30% / Bathhouse heal tick / Festival +15 Trust / Vault +20 / Bulk Carry` `8 stat /6 skill`

### DLC 4 Endgame Fantasy (like Summons breeding)
- **RANGER** 10 `Bow Spread 14° / Stealth Crouch 60% x1.5 dmg / Trap ASspellMine 90 / Hunt`
- **SUMMONS** 14 `Tales Dawn` monster raise `egg->base->evolve 3 branches` `MonsterFamily DataAsset`
- **DUNGEON MASTER** 12 own circle `6 stat 6 skill` - `Carve Room 3x3 BlockAll / Hallway 1x6 Corridor / Boss Room 5x5 Boss spawn 2xHP / Vault Artifact +5% yield / Share Sigil Export .sav multiplayer teams challenge` `StylizedIsland Wall spline SplineEffect2` replaces weak `Labyrinth`.
- **ARCHITECT** 10 `Tier locks: Village wood free / Large Town stone requires 4 nodes / Kingdom Castle requires 8 nodes DLC` `AdvancedVillagePack/Fantastic_Village_Pack` `Baron->Duke quests Rank A` `Build Speed +10% / Inv+8 / Second Floor +2 beds / Warehouse`

## 5. Magic - Simple Tales TP (Old deleted)
Old `SpellCraftTypes.h:GetFusionType/GetSpellTier` `CalculateFinalManaCost Base*Shape*Env*Charge*Fatigue 5x` `Density 0.4-2.0s` deleted.
New `TP 100 regen 8/s` `4 Artes LMB/RMB/Q/E` `Hold 0.3s arte` `Tap Demon Fang 12TP / Hold Spread 25TP` `if TP<cost stagger 0.4s` `ProceduralMagicCircle.cpp:RebuildGeneratedGeometry` keeps only color `GetElementColor()` rotation `0.45 rad/s`, no tiers. `Fighter` dip 5 nodes `Enchant Fire 15s 20TP` `NS_Sword_Fire` same as `Zelos/Kratos`.

## 6. Town Progression
`Village wood` (start) -> `Large Town stone` `Barons Rank B` core end `Trust 50` -> `Kingdom Castle` `ARCHITECT DLC` `Trust 80` `Duke Rank A`. `Fantastic_Village_Pack` `StylizedIsland` foliage. No `PoE 1325` travel tax.

## 7. Project Setup UE 5.8.1
- Engine `T:\Program Files\UE_5.8` `EngineAssociation 5.8` `IsekaiVillage.uproject:FileVersion 3` `Modules IsekaiVillage Runtime`
- Plugins enabled `EnhancedInput, Niagara, NiagaraFluids, ProceduralMeshComponent, ModelingToolsEditorMode, EditorScriptingUtilities, PythonScriptPlugin, GameplayStateTree` (perf designer)
- Build `& "T:\Program Files\UE_5.8\Engine\Build\BatchFiles\Build.bat" IsekaiVillageEditor Win64 Development -project="F:\DEVELOPMENT\Games\IsekaiVillage\IsekaiVillage.uproject" -WaitMutex` after `Get-Process UnrealEditor,UnrealEditor-Cmd | Stop-Process -Force`
- Content already has `AdvancedVillagePack/Fantastic_Village_Pack/StylizedIsland/SlashTrail_SoftTofu/_SplineVFX` wired `FAB_LINKS.md` `NS_Sword_*` tintable.
- ThirdPerson template base: `TP_ThirdPersonBP` `Characters/Mannequins SKM_Manny_Simple ABP_Unarmed` `Input IMC_Default IA_Move/Look/Jump` already in `Source/IsekaiVillage`.
- Old code to delete vs keep: `Delete GrimoirePage.h/.cpp SpellCraftTypes fusions` `Keep CameraBoom FollowCamera Nier dodge/sprint/slide` `IslandTerrainActor cylinders` placeholder.

## 8. What Not To Do (Scope)
No 13 fusions, no cattle breeding, no LLM NPC (BT 5 barks first), no PoE 1325, no harem. `RANGER/SUMMONS` `DUNGEON MASTER` as DLC saves 3 months.

## 9. Next Steps
1. `USphereGridDataAsset` + `CENTER A 14 Life` stub
2. `UPartyReserve` + `NPC Guild Master` hall
3. `Map_Village` duplicate `Map_GrayboxArena` + `AdvancedVillagePack` modular + forest/mountain waterfall dungeon mouth
4. `WBP_SphereGrid` coin flip `0.35s` + `WBP_Shop` `TP bar`


## World geography — El Ruhn
The existing playable floating island is the Kingdom of El Ruhn, a small neutral sovereign country. Settlement growth describes the player town within this country. Neighboring mainland regions follow the supplied world and biome maps: Yozuan Desert, Divine Empire of Gosain, Kelsin Federation, Rabaric Republic and Vylfod Dominion. See [mapped world specification](WorldDesign/Mapped_World_El_Ruhn_v23.md). Neutrality is established world design; diplomacy gameplay remains future work.


### Regional ecology
The western desert grades south through semi-arid grassland and spring-fed oases into plains. Easterly moisture and an interior divide explain the wetter eastern woodland and sheltered western basin. Northern lowlands are cool scrub/woodland; permanent snow is restricted to high mountains. Low coasts include sandy beaches and highland coasts retain rock. The geography is compressed for scenic use; see [ecology update](WorldDesign/Ecology_Coasts_v24.md).

The desert includes scattered spring-fed oases and a west-facing sandstone escarpment with broad ledges, reserved as a possible nomadic cliff-community setting. See [desert refinement](WorldDesign/Desert_Shoreline_v25.md).

The world scenery is refined in [landscape polish v26](WorldDesign/World_Polish_v26.md): detailed coasts and cliffs, blended water margins, irregular forests and settlement indications, smoothed roads and softer cloud groups.

The desert escarpment is superseded by a deep diagonal canyon with layered opposing walls, tributary ravines and broad ledges that may support the nomad-community concept. See [canyon v27](WorldDesign/Desert_Canyon_v27.md).

Art direction now targets smooth, sculpted stylized realism using Fortnite as the user reference; avoid visibly faceted low-poly terrain. See [content pass v28](WorldDesign/Smooth_Stylized_Content_v28.md).
