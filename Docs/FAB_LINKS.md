# SpellCraft — Fab Links (running list)

Add new Fab URLs here anytime. Keep the **Name** next to the link so we know what each is for.

**How to add:** paste `Name — https://www.fab.com/listings/...` (or short `fab.com/s/...`) under the right section.

---

## User reference looks (want system to match / beat these)

| Name / note | Link | Role |
|-------------|------|------|
| **Style target (overall)** | https://fab.com/s/c53be02d473f | Visual bar for the magic system |
| **Water reference A** | https://fab.com/s/52596016e19e | Water look target |
| **Water reference B** | https://fab.com/s/86b4f096583b | Water look target |
| **Extra reference** | https://fab.com/s/923a48a02e75 | Additional style ref |

---

## Now in project Content (wired Aug 20–21 2026)

| Content folder | Pack role | Status |
|----------------|-----------|--------|
| `CombatMagicAnims` | SoerGame combat/cast mocap | **In + wired** (`AS_FireballCharge` cast pose) |
| `MageSet01` + `StylizedCharacters` | BodyA mage look (Leader Pose cosmetics) | **In + wired** |
| `CloseCombatAnimSet` / `Attaku` / Motifect / outfits / `StylizedIsland` | Extra imports | **In** (not wired) |
| `_SplineVFX` | Free Spline VFX — Fire / WaterSplash / Electric / Holy / Frost / Wind / Miasma | **In + wired** |
| `SplineEffect2` | Dynamic Spline FX 2 — circle/spline NS | **In** (circles next) |
| `MixedVFX` | Projectiles (FireArrow, LightningBolt, HolyArrow…) + hits + fires | **In + wired** |
| `Mixed_Magic_VFX_Pack` | Magma shot, dark projectile, lightning strike, bubbles, crystal | **In + wired** |
| `SlashTrail_SoftTofu` | Element slash trails + auras + hits (Fire/Water/Ice/Lightning/Wind/Dark…) | **In + wired** |
| `Basic_VFX` | Basic Niagara set | **In** |
| `Vefects/Zap_VFX` | Zap lightning bursts | **In + wired** |
| `Vefects/Tentacles_VFX` | Goo / dark drip FX | **In** (optional dark) |
| `MeleeWeaponAura_VFX` | Weapon auras | **In** (melee later) |
| `AdvancedPortalsSystemVFX` | Portal vortex / sparks | **In** (portals later) |
| `SwordTrailVFX` | Earlier trail pack | **In** (fallback) |
| `SoStylized` | Env water/wind | **In** (fallback) |
| `Realistic_Starter_VFX_Pack_Vol2` | Realistic starter vol 2 | **In** |
| `FXVarietyPack` / `InfinityBladeEffects` / `Particles_Wind_Control_System` | Extra FX | **In** |
| `LightVortexShader` / `StylizedBarrierShader` | Shaders | **In** |

---

## Original planned listings (still useful if any missing)

| Name | Link | What it's for |
|------|------|---------------|
| **Dynamic Spline FX 2** | https://www.fab.com/listings/ea38f9a0-d5f6-4a52-a83b-6f681ed49bcb | Spline runes / circles → `SplineEffect2` |
| **Free Spline VFX** | https://www.fab.com/listings/2b923e61-b02d-4cc9-bd0b-b067c9e6056e | Elemental splines → `_SplineVFX` |
| **Slash Trail FX Elemental** | https://www.fab.com/listings/a4b04697-30c1-4745-ae2f-a706278300bd | Wave/dash ribbons |
| **Toon VFX Pack** | https://www.fab.com/listings/e9ef0d68-02a1-4954-b6c3-d05c931c19bc | Anime impacts / charge |
| **Mixed VFX** | https://www.fab.com/listings/6518971c-c8ca-47d7-8611-1ff068b78dd5 | Cores / shields → `MixedVFX` |
| **Basic VFX Pack** | https://www.fab.com/listings/75698e52-edfc-4f76-a86c-b4f26fcf5a29 | Motes / status → `Basic_VFX` |

---

## Ultimate Spell System (migrate source)

| Path | Notes |
|------|-------|
| `F:\DEVELOPMENT\Games\UltimateSpellSystem` | Separate UE project — SpellSystemV2 pack |
| Copied into SpellCraft | `/Game/UltimateSpellSystem/Niagara/` (EnergyBall, BallCharging, Explosion, Ring, …) |

Use this as charge/projectile/impact body library while Fab elemental packs handle element flavor.

The folder was renamed on copy, so its assets still import `/Game/SpellSystemV2/SpellSystem/...`.
`Config/DefaultEngine.ini` has a `[CoreRedirects]` package redirect to `/Game/UltimateSpellSystem` — needs an editor restart to apply.

Cast poses read `AS_EnergyBall_LeftHand` / `AS_EnergyBall_RightHand` / `AS_BigEnergyBall_BothHands`,
falling back to `CombatMagicAnims` if those don't resolve.

---

## Element → body system (spear form)

Only the `SlashTrail_SoftTofu` **`NS_Sword_*`** family exposes `User.Color`, `User.SwordLength` and
`User.EndParticle_Position`, so it is the one set whose shape and tint can be driven from C++.
`FSpellElementVFX::ApplyBodyParams` sets those every time a body is assigned.

| Element | Spear body | Notes |
|---------|-----------|-------|
| Fire | `NS_Sword_Fire` | was `NS_FlameThrower` (no user params, baked cone) |
| Water | `NS_Sword_Water` | has `Cone`/`ConeAngle` instead of `EndParticle_Position` |
| Earth | `NS_Sword_Sand` | shortest lance, chunky |
| Wind | `NS_Sword_Wind` | unchanged — this was already the best-reading element |
| Lightning | `NS_Sword_Lightning` | was `NS_LightningBolt` (no user params) |
| Light | `NS_SlashTrail_LightSaber_Loop` | was `NS_HolyArrow`; `NS_Sword_Mystic` is the fallback |
| Dark | `NS_Sword_Dark` | was `NS_Dark_Solo_Projectile` (no user params) |

Dark's **homing** form uses USS `NS_EnergyBall` — USS exposes no user params so it can't be tinted,
but its baked violet is correct for Dark specifically. Do **not** layer USS under the other elements;
that is what made every spell read purple previously.

Lance length comes from `GetBodyLength` (cm along +X) rather than component scale. Scaling the
component stretched local Z, which is the projectile's *up*, so lances rendered as vertical smears.

## Held orb (charge-up)

`LoadOrbFX` uses the **`NS_AuraFX_*`** family, which swirls around a point instead of along an axis,
so a charging spell reads as a held ball rather than a lance. `ApplyOrbParams` grows it via
`User.Radius` / `User.Size` plus component scale as charge builds.

The orbs live on `LeftHandOrbVFX` / `RightHandOrbVFX`, parented to the `hand_l` / `hand_r` bones by
`AttachOrbVFXToHands`. The old single `ManaGatheringVFX` hung off `FollowCamera` at +140cm, which in
this third-person rig floated it over the torso — and being one shared component, dual-cast made it
hop between hands. It is now left deactivated.

## Walls

Earth is the only element that erupts as solid geometry (`WallUsesSolidMesh`). Every other element
hides the cube and runs a **`NS_Spline_*`** curtain, sized through `User.Extent` and revealed with
`User.Progress` over ~0.35s rather than sliding a slab up through the floor.

| Element | Wall |
|---------|------|
| Earth | solid cube, erupts from underground |
| Fire | `NS_Spline_Fire` |
| Water | `NS_Spline_WaterSplash` |
| Wind | `NS_Spline_Wind` |
| Lightning | `NS_Spline_ElectricLightning` |
| Light | `NS_Spline_Holy` |
| Dark | `NS_Spline_MiasmaBoil` |

---

## Inbox (paste new Fab links here)

| Name | Link | Role |
|------|------|------|
| **Combat Magic Animations** (SoerGame) — USE THIS | https://www.fab.com/listings/05d90ca6-d294-4b93-a1b7-232214057850 | Palm-out cast / fireball / combat mage mocap for UE mannequin |
| **Motifect Fantasy & Magic Motion Pack** | https://www.fab.com/listings/b775c780-309f-4cd9-a3f1-e50f7c912b37 | Free FBX fantasy casts (needs IK retarget; secondary) |

<!-- Example:
Cool Water Pack — https://fab.com/s/xxxxxxxx
-->

---

*Last updated: 2026-08-21 — remapped element bodies to the tintable NS_Sword_* family.*
