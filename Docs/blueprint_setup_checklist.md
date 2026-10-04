# Blueprint & C++ Setup Checklist (UE 5.8)

## 1. Architecture Overview (Option A: C++ Hybrid)
All game logic, movement physics, spline trigonometry, charge levitation, projectile morphology, and Grimoire slots are written in **clean, high-performance C++ classes**:
* `ASpellCraftCharacter` (Base for `BP_MageCharacter`)
* `AProceduralMagicCircle` (Base for `BP_ProceduralMagicCircle`)
* `ASpellProjectile` (Base for `BP_SpellProjectile`)
* `ASpellCraftGameMode`

---

## 2. Merged Elements & Full Light Fusions
* **Dark & Arcane Merged**: `DarkArcane` (`TENEBRAE` / `ARCANUM`) is an 8-sided Octagon with void suction and chaos sparks.
* **Full Suite of Light (`LUX`) Fusions**:
  * **Solar Plasma (`Light + Fire`)**: Hyper-charged piercing laser beam.
  * **Eclipse Void (`Light + Dark`)**: Black hole gravity suction + radiant supernova burst.
  * **Prismatic Aurora (`Light + Water`)**: Refractive rainbow prism lasers splitting into 7 multi-hit beams.
  * **Dawn Tempest (`Light + Wind`)**: Slicing photon blades and flash-teleport dash.
  * **Sacred Crystal (`Light + Earth`)**: Spawns reflective crystal spires on the ground amplifying all spells.
  * **Divine Smite (`Light + Lightning`)**: Vertical celestial lightning pillars striking from above.

---

## 3. How to Launch & Reparent in Unreal Editor 5.8

1. **Open the Project**:
   * Double-click `SpellCraft.uproject`.
   * When prompted: *"The following modules are missing or built with a different engine version: SpellCraft. Would you like to rebuild them now?"* -> Click **Yes**.
2. **Reparent the Existing Blueprints**:
   * Open `Content/SpellCraft/Blueprints/Character/BP_MageCharacter` -> Click **File > Reparent Blueprint** -> Select `SpellCraftCharacter`.
   * Open `Content/SpellCraft/Blueprints/MagicCircle/BP_ProceduralMagicCircle` -> Click **File > Reparent Blueprint** -> Select `ProceduralMagicCircle`.
   * Open `Content/SpellCraft/Blueprints/Projectile/BP_SpellProjectile` -> Click **File > Reparent Blueprint** -> Select `SpellProjectile`.
3. **Assign Your Fab Visual Assets**:
   * In `BP_ProceduralMagicCircle`: Select the `CircleVFX` Niagara component and assign your favorite system from **Dynamic Spline FX 2** or **Free Spline VFX**.
   * In `BP_SpellProjectile`: Select the `ProjectileVFX` Niagara component and assign your projectile effect from **Mixed VFX** or **Toon VFX Pack**.
4. **Press Play (PIE)**:
   * Test WASD movement, Sprint (`Shift`), Dash (`Tap Shift`), Slide (`Ctrl`), and Left-Click hold charging with multi-cast fan barrages!
