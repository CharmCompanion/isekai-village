# Playtest — Tower of Elrhun vertical slice

Engine: **Unreal Engine 5.8**. Setup for another PC is in [Docs/COLLAB.md](Docs/COLLAB.md).

**Project:** `IsekaiVillage.uproject`  
**Map:** `Map_ElRuhnSky`  
**Content path:** `/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky`

Open the project, then Play In Editor on that map.

## 1. Prologue debris and ruin salvaging

- Walk the village outskirts. Ruined piles are scattered on the grass: Charred Timber, Stone Rubble, Scrap Metal, and ruined structures.
- Hit each pile with a basic attack.
- A floating counter should show hits remaining (example: Salvaging Stone Rubble, 2 hits left).
- On the 3rd hit (5th for a large structure) the pile shatters and drops Wood, Stone, or Iron.
- Top-left inventory counts should go up.

## 2. Build mode and HUD

- Press **B**. The character enters build mode.
- Top-right status card should show:
  - Blue header: `BUILD MODE • TIER 1 BLUEPRINTS`
  - Active Mode: `MODULAR STRUCTURES`
  - Equipped piece, wall style (Straight), and material preview
  - Placement: `MAGNETIC SNAP`, scale `1.0x`, rotation `0°`
  - Control cheatsheet along the bottom

## 3. Radial build wheel (Q)

- In build mode, press **Q**. A radial catalog opens in the center, about 8–9 gold-bordered slots.
- Press **Tab** to cycle:
  - **Structures:** Straight Wall, Curved Arc Wall, 45° Diagonal Wall, Doorway, Floor, Foundation, Stairs, Roof, Pillar
  - **Furniture / linchpins:** Anvil, Bed, Counter, Oven, Workbench, Cauldron, Desk, and the rest, with live resource costs and affordable / unaffordable colors
  - **Materials / wallpapers:** Wood Plank, Field Stone, Cut Stone, Brick, White Plaster, Striped Wallpaper, Floral Wallpaper, Wood Wainscot
- Press **1–9** to equip that slot.
- Press **Esc** or **Q** again to close the wheel.

## 4. Walls, scale, and finishes

- Equip a wall. Press **M** to cycle Straight, Curved Arc (smooth round wall), and 45° Diagonal. The ghost and the placed mesh should change shape.
- Press **C** to cycle material sets. Exterior should read as masonry (Field Stone / Brick). Interior should read as wallpaper or wainscot, without stretched textures.
- **Page Up / Page Down** (or **= / -**) changes scale.
- **R** rotates 90°.
- **F** toggles `MAGNETIC SNAP` and `FREEFORM`.
- Equip a floor, place it, press **O** to cut a quadrant (stair or ladder opening).
- **Left click** places. **Right click** removes the targeted piece.

## 5. Linchpin furniture

- In build mode, press **P** (or use the Furniture tab on the **Q** wheel).
- The HUD should switch to Active Mode: `LINCHPIN FURNITURE`.
- Cycle with **P** or the scroll wheel: Anvil, Bed, Stone Hearth Oven, Craftsman Workbench, Cauldron (Tier 2), Arcane Table (Tier 2).
- Build 4 walls and a floor, then place props inside:
  - Anvil → room classifies as a Blacksmith
  - Bed + Counter → Inn
  - Oven → Bakery

## 6. Golem routines and effects

- **Blacksmith:** golem hammers the anvil. Each strike throws orange sparks. Within about 380 units, the bark is: "Strike while the iron glows, traveler! The forge sings today."
- **Baker:** golem works the stone oven. Smoke puffs rise from the oven. Nearby bark: "Crust is golden brown! Fresh bread restores energy in the tower."
- **Night / high fatigue:** golem walks to a placed Bed, lies down, and floating `Zzz` markers rise while fatigue drops.
- **Player rest:** spend TP or take damage, then press **E** on a placed Bed. HP and TP should return to full.

## 7. Tower progression

- Walk to the Tower Entrance Gate at the village edge.
- **Floor 1 clear:** HUD header becomes `BUILD MODE • TIER 2 BLUEPRINTS`. On the Furniture tab, Cauldron and Arcane Table are unlocked.
- **Floor 5 clear:** header becomes `TIER 3 BLUEPRINTS` (Commander Desk, Vaults, advanced masonry).
- **Floor 10:** Sanctum of the Crazed Wizard. Defeat Archmage Elrhun.
  - +15 Crystals
  - Tier 4 Celestial Arcane Forge (Celestial Anvil and Runic Crucible)
  - New Game Plus / Echo Depths (floors -1 through -100)
- Press **B** to leave build mode and return to exploration and combat.

## What to report

- Feel of the build wheel (**Q**), wall curving (**M**), and snapping (**F**).
- Whether the top-right overlay is readable, and whether anvil sparks, oven smoke, and sleep `Zzz` fit the scene.
- How the loop feels: debris → building → golem routines.
- Bugs, quirks, and the next change you want.
