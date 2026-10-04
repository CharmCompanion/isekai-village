# BP_ProceduralMagicCircle — Node Build Steps

Graph bodies must be built in-editor (UE 5.8 exposes no node-spawn API to
Python). Everything else — variables, defaults, lookup tables, empty graphs —
is already in place.

Build in this order. The first two are the de-risking pair: once they work,
you have a real element-shaped circle on screen.

---

## 1. `BuildPointList`

Ports `getPoint` + `rotMat` (renderer.js:2274, 2313). Produces the N points
every other primitive consumes.

**Signature**
- Inputs: `Radius` (double), `Count` (int), `Rotation` (double)
- Output: `Points` (Array of Vector)

**Nodes**
1. **For Loop** — First Index `0`, Last Index = `Count - 1`
2. In the body, compute the angle — note the `-π/2` so point 0 sits at **top**,
   not right. Skip it and every polygon renders rotated:
   ```
   Angle = (Index / Count) * 6.283185 - 1.570796
   ```
   `Index` → **Conv Int to Double** → **Divide** by `Count` →
   **Multiply** by `6.283185` → **Subtract** `1.570796`
3. `X = Cos(Angle) * Radius`  — use **Cos**, the radians node, not Cos Degrees
4. `Y = Sin(Angle) * Radius`
5. Apply rotation (`rotMat`, clockwise):
   ```
   X' = X*Cos(Rotation) + Y*Sin(Rotation)
   Y' = X*-Sin(Rotation) + Y*Cos(Rotation)
   ```
6. **Make Vector** (X', Y', 0) → **Add** to `Points`

---

## 2. `ConnectPoints`

Ports `connectPoints` (renderer.js:1938). **This one function draws every
polygon and star** — the modulo step is the whole trick.

**Signature**
- Inputs: `Points` (Array of Vector), `Skip` (int)
- No output — writes into `MagicCircleSpline`

**Nodes**
1. `MagicCircleSpline` → **Clear Spline Points**
2. Set a local int `Index = 0`
3. **For Loop** — `0` to `Points.Length - 1`
4. Body:
   - `Index = (Index + Skip) % Points.Length` — use **Percent (int)**;
     with non-negative `Skip` this matches the reference `mod`
   - **Get** `Points[Index]`
   - **Add Spline Point** — Target `MagicCircleSpline`, Coordinate Space
     **Local**, `bUpdateSpline` **false**
5. On **Completed**: **Set Closed Loop** (`true`) → **Update Spline**

Keep `bUpdateSpline` false in the loop and update once at the end — otherwise
the spline rebuilds on every point.

**Why this replaces two spec functions**

| Count | Skip | Result |
|---|---|---|
| 6 | 1 | hexagon |
| 6 | 2 | Star of David |
| 5 | 2 | pentagram |
| 7 | 3 | heptagram — **Lightning** |
| N | 1 | regular N-gon |

---

## 3. `GetShapeForElement`

Pure array lookup — the tables are already populated, so this is three nodes.

**Signature**
- Input: `InElement` (EElement)
- Outputs: `Count` (int), `Skip` (int)

**Nodes**
1. `InElement` → **Enum to Byte** → **Conv Byte to Integer**
2. **Get** `ElementSymmetry[index]` → `Count`
3. **Get** `ElementSkip[index]` → `Skip`

Mark it **Pure** (Details → Pure). Defaults already loaded:
```
ElementSymmetry = [3, 4, 6, 5, 10, 8, 7, 9]
ElementSkip     = [1, 1, 1, 1, 1, 1, 3, 1]
                   Fire Earth Water Wind Light Dark Lightning Arcane
```

---

## 4. `RebuildCircle`

Orchestrator. Call this from the **Construction Script** so the circle previews
live in the viewport.

**Nodes**
1. `GetShapeForElement(Element)` → `Count`, `Skip`
2. `BuildPointList(Radius, Count, Rotation)` → `Points`
3. **Branch** on `bConnectPoints` → `ConnectPoints(Points, Skip)`
4. **Branch** on each remaining toggle → its primitive
   (`bLinesToCenter` → `LinesToCenter`, etc.)
5. `UpdateNiagaraBindings`

---

## First test

After steps 1-4, drag `BP_ProceduralMagicCircle` into the level and change
`Element` in the Details panel. The shape should change per the table above —
Fire a triangle, Water a hexagon, Lightning a 7/3 heptagram.

That single test validates the point math, the modulo chord walk, and the
element lookup together.

---

## 5. `UpdateNiagaraBindings` — the real integration risk

Everything above is self-contained maths. This is the step that depends on
third-party behaviour neither of us has verified: whether **Dynamic Spline
FX 2** actually accepts a spline through a `User.Spline` parameter, as the
spec's §6 assumes.

**Nodes** (per walkthrough.md §3)
1. **Set Niagara Variable (Object)** — `User.Spline` = `MagicCircleSpline`
2. **Set Niagara Variable (Linear Color)** — `User.Color` = element colour
3. **Set Niagara Variable (Float)** — `User.EmissivePower` = `EmissivePower`
4. **Set Niagara Variable (Float)** — `User.ParticleSpeed` =
   `ParticleSpeed * SpinRateMultiplier`

Before wiring: open the Dynamic Spline FX 2 Niagara system and confirm a
user-exposed parameter of type Spline actually exists, and check its real name.
If it differs, the spec's parameter names are wrong and this is where it will
show up. Report what you find rather than forcing the spec's names.

---

## Not yet built

- Rune text ring — deferred to the pre-baked texture half of the hybrid
  approach (Docs/magic_circle_system.md §9)
- `ConnectBorder`, `ConnectMidPoints`, `InscribePoints` — graphs exist, bodies
  empty; add once the core loop renders
- Layer nesting (`ParentPointIndex`, child rings) — single-ring first
