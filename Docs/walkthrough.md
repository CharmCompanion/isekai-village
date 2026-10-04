# Unreal Engine 5.8 C++ & Niagara Architecture Walkthrough

We have implemented the full **Anime Mage Dual-Wielding Magic System** with authentic concentric sacred geometry, neon highlighter line rendering (fat color + white-hot center core), dynamic runic incantation text, and a natural spell lifecycle.

---

## 1. Concentric Sacred Geometry & Neon Line Rendering

```
[ OUTER RUNIC DOUBLE RING ]  (Radius = R & R * 0.90)
    ├── [ ROTATING RUNIC TEXT RIBBON ] (e.g. "• IGNIS • TERRA • FUSIO • TIER III •")
    └── [ INSCRIBED PRIMARY SACRED POLYGON ] (Radius = R * 0.88 - Vertices touch inner text band)
          ├── [ ORBITAL SATELLITE NODES ] (Mini-circles at every vertex)
          ├── [ RADIAL SACRED SPOKES ] (Lines connecting center to each vertex)
          └── [ CONCENTRIC MID-ORBITAL RING ] (Radius = R * 0.55)
                └── [ INSCRIBED SECONDARY FUSION POLYGON ] (Phase-rotated for nested stars)
                      └── [ INNER CORE RING & CENTRAL GLYPH ] (Radius = R * 0.28)
```

### Neon Highlighter Double-Pass:
* **Outer Glow Layer**: Fat saturated elemental color (9px–16px).
* **Inner Laser Core**: Pure white-hot electric core (3px–5.5px) in the exact center of every line, vertex satellite, and ring.

---

## 2. Magic Circle Lifecycle & Activation Flow

1. **Idle State**:
   * No magic circles visible (`Hidden = true`, Scale = 0). You run and jump freely with clean hands.
2. **Building / Charging (`Hold LMB` or `Hold RMB`)**:
   * Mana motes gather inward toward hands, shifting to the active element color.
   * Palm magic circle smoothly expands (`Scale: 0.0 -> 1.0`) while starting a smooth harmonic counter-rotation.
   * Runic font text illuminates and writes out the spell recipe.
   * Emissive white-hot laser core intensifies as charge approaches 100%.
3. **Activation / Release (`Release LMB` or `Release RMB`)**:
   * Activation flash erupts.
   * **Projectiles**: Fires the multi-cast projectile barrage; hand circle fades out over 0.4s.
   * **Sustained Constructs (Earth Wall, Traps)**: Circle stays placed in the world on the ground until duration ends or detonated with `R`.

---

## 3. Controls & Combat Scheme

| Action | Key / Input | Combat Mechanics & Animation |
| :--- | :--- | :--- |
| **Move** | `W`, `A`, `S`, `D` | Full Enhanced Input fluid movement with Mannequin animations. |
| **Jump** | `Space` | Vertical jump physics with air control. |
| **Slide / Crouch** | **`C`** | Squishes collision capsule (`88 -> 44`) with high-speed slide impulse. |
| **Sprint / Dash** | **`Shift`** | Hold for Sprint (`MaxWalkSpeed = 900`), Tap (<0.2s) for instant Dash. |
| **Left Hand Spell** | **`Left Click (LMB)`** | Hold to charge floating left palm circle / Release to fire or place. |
| **Right Hand Spell**| **`Right Click (RMB)`**| Hold to charge floating right palm circle / Release to fire or place. |
| **Cancel Casting** | **`Tab`** | Safely aborts charging on active hand without mana waste. |
| **Dual Fusion Link**| **`Q`** | **Chant Synthesis**: Fuses Left Hand with Right Hand into a Grand Two-Handed Spell. |
| **Spell Overcharge**| **`E`** | **Empower Burst**: Instantly grants +1 Tier & Kinetic Overcharge Burst to active spell. |
| **Remote Detonate** | **`R`** | **Trigger Detonation**: Remotely detonates all placed traps, walls, and mines in arena. |
| **Mana Melee Strike**| **`F`** | **Mana Blade / Palm Thrust**: Close-quarters strike dealing 40 damage + 1200 knockback. |
| **Bullet Time + Radial** | **`Hold M-CLICK`** | Slows world time down to **`0.25x`** + opens 8-slot symbol wheel. |
| **Primary Element** | `1` to `7` | Sets Core Element for active hand. |
| **Secondary Fusion** | `Alt + 1` to `7` | Fuses a Secondary Element to activate hybrid fusions. |
