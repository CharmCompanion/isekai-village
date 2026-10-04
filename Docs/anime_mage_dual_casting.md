# Anime Mage Dual-Hand Casting, Bullet Time & Ground Placement Specification

Inspired by anime magic systems like *Mushoku Tensei: Jobless Reincarnation* (Rudeus Greyrat's silent dual-casting, stone cannon shaping, and ground displacement magic):

---

## 1. Core Mechanics Overview

### 1. Bullet Time Weaving (`TimeDilation = 0.25x`)
* When opening the Radial Menu or holding `M-CLICK` to weave/craft spells, world time smoothly dilates down to `0.25x` while keeping player camera and aiming fluid.
* Gives the anime "tactical pause" feel to weave complex spell tiers during chaotic combat.

### 2. Dual-Hand Casting (Independent Left & Right Hands)
* **Left Hand (`LMB`)**: Independent `FSpellCircleConfig` & floating palm circle.
* **Right Hand (`RMB`)**: Independent `FSpellCircleConfig` & floating palm circle.
* Cast a defensive Earth Wall with Left Hand while firing a Solar Laser with Right Hand!

### 3. Remote Ground-Targeted Placement (Earth Wall, Mines, Geysers)
* Defensive and environmental shapes (`wall`, `mine`, `singularity`, `aoe`) project a **Targeting Magic Circle on the ground** following mouse raycast.
* On cast activation, the barrier or trap erupts directly at the mouse cursor location in the 3D world.

### 4. Updated Control Scheme
* `WASD`: Movement.
* `Space`: Jump.
* `C`: Slide / Crouch (Capsule half-height squish).
* `Shift` (Hold): Sprint | `Shift` (Tap): Dash.
* `LMB` (Hold/Release): Left Hand Spell (Charge & Cast/Place).
* `RMB` (Hold/Release): Right Hand Spell (Charge & Cast/Place).
* `M-CLICK` (Hold): Activates Bullet Time + Radial Weaving Menu.
* `1` to `6`: Primary Element | `Alt + 1-6`: Secondary Fusion Element.
