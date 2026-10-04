# SPELLCRAFT MAGIC SYSTEM: COMPREHENSIVE AI CONTEXT

**To the AI reading this (Cursor):** This document contains the absolute "Golden Rulebook" for a custom Unreal Engine 5 magic system. It outlines the mechanics, controls, advanced mathematical formulas, and the current state of the C++ codebase. Treat these rules as strict architectural pillars.

`Docs/unreal_anime_mage_master_spec.md` is an **archived** earlier draft (radial menu, 1–6 keys, Grimoire Z/X/C deck). Keep it for circle/VFX/symbol geometry notes. Do **not** reintroduce a spell deck.

---

## 1. CORE PHILOSOPHY
- **No Deck-building, No 1-5 keys:** Spells are not pre-slotted. They are compiled in real-time during combat using modifier keys.
- **Visual Incantations:** Spells are cast by forming physical Magic Circles on the character's hands. The core symbol is the Element; surrounding symbols are Modifiers.
- **Nier: Automata Movement:** Fast-paced, responsive combat. Aerial dashes, perfect dodges (which trigger "Focus Mode" / bullet time for silent casts). Magic must not interrupt flow.
- **Physics-Based:** Magic is physics. Elements have weight, gravity, momentum, and react to the environment.

---

## 2. THE CONTROL SCHEME
The player compiles spells dynamically using the following inputs bound in `ASpellCraftCharacter::SetupPlayerInputComponent`:

*   **Mouse Scroll Wheel:** Cycles the `ActiveElement` (Earth, Fire, Water, Wind, Lightning, Light, Dark).
*   **LMB (Left Mouse):** Offensive Casting Hand.
*   **RMB (Right Mouse):** Defensive / Utility Casting Hand.
*   **Q (Modifier 1):** Utility / Homing / Self.
*   **E (Modifier 2):** Area / AoE / Ground Trap.
*   **Middle Mouse (Modifier 3):** Dual Cast / Fusion Link (Combines Left and Right elements).

### The Spell Compiler (How it works)
When the player presses `LMB`, the game checks the modifier booleans to shape the spell:
*   `LMB` (No Modifiers) = Base Offense (e.g., Spear / Pierce).
*   `Q + LMB` = Utility Offense (e.g., Homing Ball).
*   `E + LMB` = Area Offense (e.g., Nova / Wave).
*   `RMB` (No Modifiers) = Base Defense (e.g., Wall).
*   `Q + RMB` = Utility Defense (e.g., Orbit Shield / Heal).
*   `E + RMB` = Area Defense (e.g., Ground Trap / Mine).

---

## 3. ADVANCED TARGETING (CHARGE-TO-DISTANCE)
To keep combat fluid, there are no UI ground-targeting reticles that require mouse-dragging.
Instead, aiming is determined by **Charge Time**:
*   Holding `LMB` or `RMB` pushes the ground-target coordinates forward in the direction the camera is facing.
*   A quick tap casts at 400 units away. A full hold casts at 2500 units away.
*   *Exceptions:* God-Tier magic overrides this and casts at a massive fixed distance (e.g., 3500 units).

---

## 4. THE DEEP MAGIC MATH (MASTER EQUATIONS)
The system uses an intense mathematical backend to calculate Mana costs, speed, and physics.

### A. The Master Mana Equation
`Final Cost = BaseElement * ShapeMult * TerrainAffinity * ChargeDistanceMult * FatigueTier`
*   If the player doesn't have enough mana for the `Final Cost` upon releasing the cast, the spell fizzles.

### B. Element Fatigue (Anti-Spam)
If you cast Fire, Fire's fatigue tier goes up (+1). If you cast Water, Water goes up (+1), but ALL other elements instantly cool down (-1).
*   Tier 0 = 1x Mana Cost.
*   Tier 3 = 4x Mana Cost.

### B2. Grimoire Pages (Prepared Spells — Not a Deck)
*   Live casting (scroll + Q/E + LMB/RMB) stays the flexible, full-power verb.
*   Saved pages are **named `FSpellCircleConfig` recipes** — same grammar, no illegal element/state combos.
*   Book casts are **slightly weaker** (`BookPowerMultiplier` ≈ 0.88), use the **same mana equation + element fatigue**, and have a **separate page-heat cooldown**.
*   **Page heat:** each cast of that page +1 heat (capped). `Cooldown = CooldownSeconds × HeatTier`. Heat drops **by time only** while the page is off cooldown (`PageHeatDecaySeconds` per tier) — casting other pages/elements does **not** cool page heat.
*   **PvP:** each page also has `PvpCastLimit` casts per battle.

### C. Element Density (Charge Speed)
Elements have physical density, affecting how fast the `ChargeTime` fills up.
*   **Wind (Density 0.4):** Fills instantly. Very fast to cast.
*   **Earth (Density 2.0):** Heavy. Takes 2 full seconds to reach maximum power/distance.

### D. Environmental Raycasting (Terrain Affinities)
Upon casting, a raycast shoots 150 units down from the player to read the Physical Material (`PhysMat`).
*   Standing on `Water`/`Mud`: Water spells cost 0.5x. Fire spells cost 2.0x.
*   Standing on `Rock`/`Stone`: Earth spells cost 0.5x.

### E. Projectile Physics & Momentum
Implemented in `ASpellProjectile::ApplyElementalPhysics()`:
*   **Momentum Inheritance:** Projectiles inherit 50% of the player's physical velocity (e.g., throwing a fireball while sliding makes it fly faster).
*   **Gravity Scaling:**
    *   Earth = `2.0 Gravity` (Requires lobbing like a cannonball).
    *   Fire = `0.8 Gravity` (Heavy arc).
    *   Water = `0.2 Gravity` (Shoots straight but drops at extreme range).
    *   Lightning = `0.0 Gravity` (Laser straight).

---

## 5. CURRENT C++ IMPLEMENTATION STATE
We have successfully gutted the old 1-5 UI deck-builder code and implemented **Phase 1 (Inputs/Fatigue)** and **Phase 2 (Compiler & Physics)**.

**Files Edited:**
1.  **`SpellCraftCharacter.h / .cpp`**
    *   Added Modifier Key Bindings (`Q`, `E`, `MMB`).
    *   Added `CycleActiveElement()` and removed Grimoire slot arrays.
    *   Added `CalculateFinalManaCost()`, `GetElementDensity()`, `CheckEnvironmentalAffinity()`.
    *   Updated `GetGroundAimLocation()` to scale distance based on `ChargeRatio`.
    *   Updated `StartLeftCast()` / `StartRightCast()` to read modifiers and build the `FSpellCircleConfig`.
    *   Updated `ReleaseLeftCast()` to calculate mana and Fizzle on failure.
    *   Updated `Tick()` to use Element Density for charge speed.

2.  **`SpellProjectile.h / .cpp`**
    *   Updated `InitProjectile()` to apply caster velocity inheritance (Momentum).
    *   Updated `ApplyElementalPhysics()` to apply specific Gravity, Speed, and Pierce logic based on the incoming `FSpellCircleConfig`.

**Pending Next Steps (after Phase 3):**
*   Author Niagara systems that read `User.Shape` / `User.ElementType` / `User.Color` (ball, spear, wave, lightning bolt). Mesh cores already morph per element until those assets exist.
*   Rune text rings (SpellRunes font) — still baked-texture / CRT later.
*   Glyph mines as their own actor (currently wall actor).
