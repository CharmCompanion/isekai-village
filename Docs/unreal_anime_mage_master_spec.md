# ANIME MAGE: DYNAMIC SPELL CIRCLE & PARTICLE MORPHOLOGY SYSTEM
## Master Game Design & Technical Specification Document (Unreal Engine 5)

> **ARCHIVE — not the live control scheme.** This is the older 24-symbol radial + Grimoire Z/X/C / keys 1–6 draft. SpellCraft compiles spells in real time (scroll element, LMB/RMB, Q/E/MMB) per `Docs/cursor_migration_context.md`. Keep this file for circle geometry, particle morphology, fusion flavor, and Fab VFX mapping.

---

## 1. Executive Summary & Core Fantasy
* **Genre**: Fast-Paced 3D Stylized Action / Magic Shooter.
* **Aesthetic**: Retro 3D Anime Stylized (Inspiration: *Megaman Legends*, *Adventure Quest 64*, Modern Anime VFX).
* **Core Fantasy**: The player is an agile combat mage who weaves complex geometric magic circles on the fly while sprinting, jumping, sliding, and dashing. Faster building allows faster, more catastrophic casting. Spells morph in real time based on active elements, attached geometric symbols, and multi-core fusions.

---

## 2. Controls & Movement Physics

| Action | Control Key | Mechanical Behavior |
| :--- | :--- | :--- |
| **Move** | `W`, `A`, `S`, `D` | Full 3D omnidirectional character movement. |
| **Jump** | `Space` | Vertical jump physics with air control. |
| **Sprint** | `Shift` (Hold) | Boosts movement speed by 1.5x (`MaxWalkSpeed = 900`). |
| **Dash** | `Shift` (Tap < 0.2s) | Instant burst of impulse velocity in the active input direction. |
| **Slide / Crouch** | `Ctrl` | Halves player capsule collision height (`88 -> 44`), grants high initial slide velocity decay. |
| **Aim** | `Mouse Movement` | Raycasts onto ground plane / camera crosshair for 360° aiming. |
| **Radial Menu** | `Hold M-CLICK` | Centers 8-slice swipe radial wheel on screen. |
| **Flip Radial Pages** | `Scroll Wheel` (while M-CLICK held) | Cycles across 3 symbol pages (Shapes, Behaviors, Enchantments). |
| **Attach Symbol** | `Release M-CLICK` | Equips hovered symbol into the active magic circle. |
| **Primary Core** | `1` to `6` | Sets Primary Core Element (`1`=Fire, `2`=Earth, `3`=Water, `4`=Wind, `5`=Light, `6`=Dark). |
| **Secondary Core** | `Alt + 1` to `6` | Fuses a Secondary Core Element to trigger Dual-Element Hybrid Fusions. |
| **Clear Secondary** | `0` | Returns to Pure Single-Core mode. |
| **Charge / Delay Cast**| `Hold Left Click` | Magic circle levitates from floor to chest height, gathers ambient mana motes, charges bloom. |
| **Release Cast** | `Release Left Click` | Fires multi-cast fan barrage with bonus tier velocity and damage. |
| **Grimoire Swap** | `Z`, `X`, `C` | Instantly swaps active magic circle to saved Grimoire Slot 1, 2, or 3. |
| **Grimoire Save** | `Ctrl + Z`, `Ctrl + X`, `Ctrl + C` | Imprints current magic circle configuration into that Grimoire slot. |
| **Undo Symbol** | `R` | Removes the last attached symbol from the circle. |
| **Clear Circle** | `X` | Clears all attached symbols. |

---

## 3. Elemental Matrix & Dual-Core Hybrid Fusions

### 6 Base Elements
1. **Fire (`IGNIS`)**: Crimson-Orange (`1.0, 0.28, 0.08`). Sawtooth jagged boundary, rough flame sparks.
2. **Earth (`TERRA`)**: Ochre-Gold (`0.82, 0.65, 0.25`). Castellated stone blocks, heavy falling debris chunks.
3. **Water (`AQUA`)**: Azure-Cyan (`0.12, 0.65, 1.0`). Sinusoidal wave rings, laminar fluid droplet ribbons.
4. **Wind (`VENTUS`)**: Emerald-Mint (`0.25, 0.92, 0.65`). Swooping aerodynamic spirals, centrifugal vortex ribbons.
5. **Light (`LUX`)**: Platinum-Gold (`1.0, 0.95, 0.6`). Sacred star halos, ultra-focused piercing laser beams.
6. **Dark (`TENEBRAE`)**: Eldritch Violet (`0.72, 0.18, 0.95`). Occult eye pupils, inward gravitational suction motes.

### 6 Hybrid Fusion Archetypes (Dual-Core Slotting)
* **Volcanic Magma (`FIRE + EARTH`)**: Projectiles leave lingering bubbling lava pools on the floor dealing continuous burn AoE.
* **Blizzard Tempest (`WATER + WIND`)**: Unlocks *Frostbite*, summoning sub-zero freezing vortexes that freeze enemies solid.
* **Eclipse Void (`LIGHT + DARK`)**: Unlocks *Event Horizon*, creating twin gravitational singularities that implode with radiant holy bursts.
* **Thermal Steam (`FIRE + WATER`)**: Creates expansive scalding mist clouds that obscure vision and tick heat damage.
* **Sandstorm Cyclone (`EARTH + WIND`)**: Deflecting razor dust clouds that shred defenses and deflect projectiles.
* **Solar Plasma (`LIGHT + FIRE`)**: Hyper-charged piercing laser beams traveling at 2.2x speed.

---

## 4. Dynamic 24-Symbol Database across 3 Radial Pages

### Page 1: SHAPES
1. `ball` (Sphere / *SPHAERA*): Solid spherical projectile.
2. `spear` (Lance / *HASTA*): High-velocity linear lance.
3. `wall` (Barrier / *MURUS*): Stationary protective stone/energy wall (Req: `EARTH` or `WATER`).
4. `drill` (Vortex Drill / *TEREBRA*): High-RPM spinning multi-hit drill.
5. `wave` (Crescent Wave / *UNDA*): Sweeping wide cleave arc (Req: `WATER` or `WIND`).
6. `mine` (Glyph Trap / *LAQUEUS*): Proximity detonation floor rune (Req: `EARTH` or `DARK`).
7. `orbit_shield` (Orbit Shield / *ORBIS*): Orbiting defensive satellite barrier.
8. `prism_star` (Prism Star / *STELLA*): Faceted multi-directional star burst (Req: `LIGHT`).

### Page 2: BEHAVIORS
1. `split` (Fork Split / *FRACTURA*): Splits in mid-air into child projectiles.
2. `homing` (Hunter Track / *VENATOR*): Curves trajectory toward nearest target.
3. `spin` (Cyclone Spin / *VOLUTUS*): High-speed orbital spin.
4. `pierce` (Penetrate / *PENETRATIO*): Pierces through multiple enemies.
5. `bounce` (Ricochet / *RESILIENS*): Bounces off obstacles and targets.
6. `accelerate` (Mach Surge / *VELOCITAS*): Accelerates exponentially over flight (Req: `WIND` or `LIGHT`).
7. `chain` (Chain Link / *CATENA*): Arcs lightning to nearby enemies (Req: `WIND` or `LIGHT`).
8. `overcharge` (Overcharge / *INTENSIO*): Scales projectile size, particle volume, and damage by 2x.

### Page 3: ENCHANTMENTS
1. `aoe` (Cataclysm AoE / *CATACLYSMUS*): Expands impact into massive area explosion.
2. `burn` (Ignite / *INCENDIUM*): Deals lingering burning fire damage (Req: `FIRE`).
3. `freeze` (Frostbite / *GLACIES*): Freezes enemies solid on contact (Req: `BLIZZARD` Fusion).
4. `lifesteal` (Sanguine Drain / *HAUSTUS*): Heals caster for 20% of damage dealt (Req: `DARK`).
5. `singularity` (Event Horizon / *VORAGO*): Gravitational suction vortex (Req: `ECLIPSE` Fusion / `DARK`).
6. `smite` (Radiant Smite / *IUDICIUM*): Calls down a vertical divine light pillar (Req: `LIGHT`).
7. `curse` (Shadow Curse / *MALEDICTIO*): Corrupts targets, reducing defense (Req: `DARK`).
8. `shock` (Tempest Shock / *TONITRUS*): Stuns enemies for 1.5s (Req: `WIND`).

---

## 5. Dynamic Spell Tiers & Multi-Casting
Spell Tier is computed automatically based on the complexity of the circle:
* **Tier 1 (Novice, 1-2 symbols)**: 1 projectile, standard power.
* **Tier 2 (Adept, 3-4 symbols)**: **2-Shot Fan Multi-Cast**, +30% damage, 4 satellite crown nodes.
* **Tier 3 (Master, 5-6 symbols)**: **3-Shot Arc Barrage**, +60% damage, 8-pointed star crown boundary.
* **Tier 4 (Apex, 7+ symbols)**: **5-Shot Grand Volley**, +100% damage, radiant sunburst rays.
* *Dual-Element Fusion grants a +1 Tier level bonus!*

---

## 6. Procedural Spline Magic Circles (`BP_ProceduralMagicCircle`)
Using **Dynamic Spline FX 2** and **Free Spline VFX**:
* **Ring Generation**: Trigonometric spline points (`cos(theta) * R`, `sin(theta) * R`) closed in a loop.
* **Star Polygons**: Alternating outer and inner radius spline points.
* **Interlocking Dual-Cores**: Two offset, counter-rotating circle splines connected by a central energy bridge.
* **Niagara Parameters**: Passes `User.Spline`, `User.Color`, `User.EmissivePower`, and `User.ParticleSpeed`.

---

## 7. Particle-Morphology Projectiles (`BP_SpellProjectile`)
* **Layer A (Geometric Shape Construct)**: Emitter shape configured to match `Sphere`, `Lance`, `Drill Spiral`, `Barrier Wall`, or `Crescent Wave`.
* **Layer B (Elemental Flow)**:
  * *Fire*: Upward convection plume and flickering flame embers.
  * *Earth*: Downward gravity and heavy bouncing rock chunks.
  * *Water*: Smooth fluid droplet ribbons and laminar trails.
  * *Wind*: Swirling vortex ribbons and high centrifugal velocity.
  * *Light*: Straight beam laser flares with sparkle dust.
  * *Dark*: Inward-collapsing dark matter motes.
* **Kinetic Impact Dispersal**: Shatters into explosive fragments (lava pools, frost spikes, singularity shockwaves).

---

## 8. Grimoire Memory Deck (`[Z]`, `[X]`, `[C]`)
* 3 memory slots holding full `FSpellCircleConfig` structs.
* Tap `Z`, `X`, `C` to hot-swap loadout. Hold `Ctrl + Z/X/C` to imprint the active circle.
* Pre-loaded loadouts:
  * `[Z]`: *Volcanic Magma Drill* (`FIRE + EARTH`, Drill, Burn, AoE, Homing)
  * `[X]`: *Blizzard Frost Lance* (`WATER + WIND`, Spear, Freeze, Pierce, Split)
  * `[C]`: *Eclipse Void Singularity* (`LIGHT + DARK`, Sphere, Singularity, Homing, Overcharge, AoE)

---

## 9. Fab Asset Integration Mapping
1. **Dynamic Spline FX 2** (`ea38f9a0-d5f6-4a52-a83b-6f681ed49bcb`): Core procedural spline runes & magic circle paths.
2. **Free Spline VFX** (`2b923e61-b02d-4cc9-bd0b-b067c9e6056e`): Elemental spline materials (Fire, Holy, Electric, Miasma).
3. **Slash Trail FX Elemental** (`a4b04697-30c1-4745-ae2f-a706278300bd`): Crescent Wave projectile ribbons & Dash/Slide trails.
4. **Toon VFX Pack** (`e9ef0d68-02a1-4954-b6c3-d05c931c19bc`): Stylized anime impact bursts, hit-sparks, and charge gathering orbs.
5. **Mixed VFX** (`6518971c-c8ca-47d7-8611-1ff068b78dd5`): Sphere cores, Orbit Shields, and Glyph Mine runes.
6. **Basic VFX Pack** (`75698e52-edfc-4f76-a86c-b4f26fcf5a29`): Ambient mana motes and enemy status effects (Freeze, Burn).
