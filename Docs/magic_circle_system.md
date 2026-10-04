# Magic Circle System — Ported from ReferenceAssets

Analysis of the two reference systems in `ReferenceAssets/`, and how they map
onto `BP_ProceduralMagicCircle`.

Sources:
- `ReferenceAssets/Generator/resources/app/renderer.js` — **readable source**
  (4088 lines). This is the one to study.
- `ReferenceAssets/magic-circle-generator-windows-beta/.../dist/renderer.js` —
  newer but **minified** (178 KB, 2 lines). Same app, later build. Use it to
  run/compare output, not to read.
- `ReferenceAssets/Magic Spell/Spell Logic.txt` — the semantic design.
- `ReferenceAssets/Magic Spell/SpellRunes-Regular.otf` — family name
  `SpellRunesRegular`. Glyphr Studio source `.gs2` sits alongside it.

---

## 1. Why this beats the original spec

`unreal_anime_mage_master_spec.md` §6 defines two flat functions —
`GenerateCircleSpline` and `GenerateStarSpline`. The generator collapses both
into **one** parameterised primitive and adds ~10 more. It is a strictly better
foundation, and it is proven — the app ships working output.

Crucially, the generator's circles are **structural**, not decorative: rings
nest, symmetry counts drive geometry, and each feature is an independent
toggle. That composability is what makes circles morph per spell.

---

## 2. Data model

A circle is a **flat list of layer objects**, each optionally parented to
another (`parentID`). `drawSections()` shifts one off the list, draws it, and
recurses. Root node (`id: 0`) holds canvas/global settings; children are rings.

Per-layer fields that matter:

| Field | Meaning |
|---|---|
| `radius` | ring radius |
| `symmetryCount` | N points around the ring — **drives all geometry** |
| `rotation` / `rotationSpeed` | static + animated rotation |
| `sectionSize` | ring band thickness (text/symbols live in this band) |
| `lineWidth` | stroke weight |
| `parentID`, `parentPointIndex` | nest a ring onto a parent's point |
| `originRelativeToParent` | inherit parent origin |

Reference data: `Generator/resources/app/Example Circles/circle_data_1.json`.

---

## 3. Core geometry (exact, from source)

**Point placement** (`getPoint`, renderer.js:2274) — note the `-π/2` so point 0
sits at top, not right:

```
theta = 2π / totalPoints
angle = theta * currentPoint - π/2
x = r * cos(angle)
y = r * sin(angle)
```

**Rotation** (`rotMat`, renderer.js:2313) — clockwise:

```
x' = x*cos(t) + y*sin(t)
y' = x*-sin(t) + y*cos(t)
```

**Chord connection** (`connectPoints`, renderer.js:1938) — the key insight.
Walk the point list stepping by `delta`, wrapping with `mod`:

```
index = mod(index + delta, pointList.length)
```

This single function produces every polygon and star:

| `symmetryCount` | `delta` (skip) | Result |
|---|---|---|
| 6 | 1 | hexagon |
| 6 | 2 | two triangles (Star of David) |
| 5 | 2 | pentagram |
| 8 | 3 | 8-point star |
| N | 1 | regular N-gon |

So spec §6's separate circle/star functions become **one** `ConnectPoints(skip)`.

---

## 4. Feature toggles = one Blueprint function each

From `drawSections` (renderer.js:1364-1488). Each is independent and composable:

| Toggle | Draws |
|---|---|
| `outerRing` / `fill` | plain circle at radius |
| `connectBorder` | arcs along the border between points |
| `connectPoints` + `connectPointsSkip` | chords — polygons and stars |
| `connectMidPoints` | chords between edge midpoints |
| `linesToCenter` | radial spokes |
| `inscribePoints` + `doubleinscribedPoints` | small circles at each point |
| `symbolsAtPoints` + `symbolsSize` | glyph at each point |
| `symbolRing` | glyphs spaced around the band |
| `textRing` + `ringText` | text warped around the ring |
| `drawTextLines` + `lineText` | text along the chords |
| `carveSpace` / `eraseCenter` | erase behind (2D-only, see §7) |
| `centerSymbol` | single glyph at origin |

---

## 5. Semantic layer (Spell Logic.txt)

The generator makes *pretty* circles; `Spell Logic.txt` makes them *mean*
something. Sentence format:

```
[Status Effect] - [Target Type] - [Spell Name]
e.g. "Ignite - Enemy - Fireball"
```

Element → polygon (this is what sets `symmetryCount`):

| Element | Shape | Sides |
|---|---|---|
| Fire | Triangle | 3 |
| Earth | Square/Diamond | 4 |
| Water | Hexagon | 6 |
| Darkness | Octagon | 8 |
| Arcane | Nonagon | 9 |
| Light | Decagon | 10 |
| Lightning | Bolt (not a polygon) | — |

Draw order, outside → in:
1. **Outer ring** — spell sentence in `SpellRunesRegular`
2. **Elemental shape** — polygon from the table above
3. **Status glyphs** — 1-3, spaced inside/along the shape
4. **Target glyph** — centered
5. **Accents** — secondary rings, filigree

---

## 6. Free win: the charge-up animation

`drawSections` already implements progressive "drawing on" via canvas line-dash
(renderer.js:1431-1437):

```
drawLength   = 2π * radius
lineDashOffset = drawLength - (drawLength * drawPercent/100)
```

Each layer has `drawStartTime` / `drawEndTime`, so rings appear in sequence.
This maps directly onto the spec's charge mechanic (§8 of the walkthrough):
drive `drawPercent` from `ChargeRatio` and the circle literally draws itself as
the player charges. In UE this is a spline-material dissolve/erosion param, not
line-dash — but the timing model ports as-is.

Determinism: the app uses `sfc32` seeded PRNG (renderer.js:453), matching the
project-wide seeded approach.

---

## 7. Known porting gaps

These do **not** port 1:1 and need decisions:

- **Text on a curve.** `ctxtextpath.js` warps glyphs along a canvas path.
  UE has no direct equivalent for splines. Options: bake rune rings to
  textures, use a Canvas Render Target, or a font-atlas material.
- **`carveSpace` / `eraseCenter`.** These rely on 2D canvas destination-out
  compositing. In 3D there is nothing to erase — either omit, or fake with
  material masks.
- **Lightning's "bolt"** is not a polygon, so it breaks the
  `symmetryCount`-drives-everything rule and needs a bespoke path.

---

## 8. Element set — DECIDED: merge to 8

The spec's six and Spell Logic's seven were merged. Final set adds **Lightning**
and **Arcane** to the existing six.

This produces a clean result: the eight elements map to **eight consecutive
polygons, 3 through 10**. Every element gets a unique, memorable shape and
`symmetryCount` alone identifies the element.

| Element | Shape | `symmetryCount` | Notes |
|---|---|---|---|
| Fire | Triangle | 3 | jagged edges, aggressive flare |
| Earth | Square / Diamond | 4 | hefty, rigid, layered |
| Wind | Pentagon | 5 | light, open, 5-fold |
| Water | Hexagon | 6 | smooth, flowing angles |
| Lightning | Heptagram | 7 | draw with **skip 3** — the 7/3 star is all sharp zigzag, matching Spell Logic's "bolt" without breaking the polygon rule |
| Dark | Octagon | 8 | thorny, void-segmented |
| Arcane | Nonagon | 9 | floating, spiral-inspired |
| Light | Decagon | 10 | radiating, divine symmetry |

Lightning was the one element Spell Logic called a non-polygon (§7). Rendering
it as a 7/3 heptagram keeps it inside the `connectPoints(skip)` system, so no
bespoke path code is needed.

### Fusions

The existing six stay valid — no rework. Six new pairings cover the added
elements:

| Fusion | Pair | Effect direction |
|---|---|---|
| Volcanic | Fire + Earth | lingering lava pools |
| Blizzard | Water + Wind | freeze solid |
| Eclipse | Light + Dark | gravity + radiant burst |
| Steam | Fire + Water | scalding mist |
| Sandstorm | Earth + Wind | razor dust, deflects |
| SolarPlasma | Light + Fire | piercing beam |
| **Storm** | Wind + Lightning | chain tempest, wide arcs |
| **Conduit** | Water + Lightning | electrocution, spreads through wet |
| **Magnetar** | Earth + Lightning | pulls metal, staggers |
| **Void** | Dark + Arcane | singularity, erases projectiles |
| **Astral** | Light + Arcane | homing runic bolts |
| **Chaos** | Fire + Arcane | unstable, random secondary |

---

## 9. Render approach — DECIDED: hybrid

- **Runtime splines** for everything that must morph per spell: rings,
  polygons, stars, spokes, inscribed points. This is the `connectPoints` family
  from §4, driven by `symmetryCount` from the element.
- **Pre-baked textures** for rune text and glyphs, rendered in
  `SpellRunesRegular`. This sidesteps the text-on-curve gap in §7 entirely.

Consequence: `carveSpace` / `eraseCenter` are dropped (2D-only compositing,
nothing to erase in 3D). If a cut-out look is wanted later, do it with a
material mask rather than geometry.
