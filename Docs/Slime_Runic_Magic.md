# Slime runic magic

## Design authority and retained roster

The current request retains Meadow, Water, Flame, Frost, Poison and Crystal slimes. Skeleton, goblin and ogre/orc procedural art passes are rejected prototypes, retained only as historical files. This delivery creates a separate slime-only map and reusable slime mage Blueprints; it does not delete original models or alter the floating-island world.

Read sources: `IsekaiVillage_GDD.md` (current single source of truth), `magic_circle_system.md`, and `ReferenceAssets/Magic Spell/Spell Logic.txt`. The supplied `SpellRunes-Regular.otf` is used directly. The older eight-element/fusion specification is superseded by the four-element GDD: Fire, Water, Earth, Wind. Frost is a Water specialization; growth, poison and crystal are Earth specializations. No extra player element enum, fusion deck or elemental fatigue is introduced.

## Spell language and visual grammar

The existing canonical sentence is **Effect - Target - Spell Name**, for example **Ignite - Enemy - Cinder Bloom**. The rune band encodes that readable sentence with the project's rune font. It is not randomly generated lettering. Element polygons follow the existing system: Fire triangle, Earth square, Wind pentagon, Water hexagon. Per the user's visual correction, the effect seal occupies the center instead of an X; the target remains encoded in the rune sentence. Twenty-four spokes connect the inward edge of the outer band to the first inner ring. Rune and geometric layers rotate in opposing directions during charging. Circles use additive, unlit, two-sided rendering and no collision.

The short incantations below are newly authored flavor strings, not translations already present in the source documents. `Ignis`, `Aqua`, and `Terra` reuse the existing element names; Nema (bind), Vela (drive), and Aegis (guard) are proposed vocabulary. The canonical machine-readable language remains the English semantic sentence. Incantation text is stored in each spell asset for later subtitles/audio; spoken voice audio is not supplied.

## Six color identities

| Slime | Signature sentence | Behavior | Incantation |
|---|---|---|---|
| Meadow / green | Bind - Enemy - Verdant Bind | 12 damage; 85% movement reduction for 2s; caster recovers 8 HP on release | Terra - Nema - Viridia |
| Water / blue | Repel - Enemy - Azure Pulse | 14 damage; pushes a character away with a small lift | Aqua - Vela - Unda |
| Flame / orange | Ignite - Enemy - Cinder Bloom | 16 damage plus 3 damage/sec for 3s | Ignis - Nema - Cindra |
| Frost / pale cyan | Chill - Enemy - Winter Needle | 12 damage; 50% movement reduction for 3s | Aqua - Nema - Glacia |
| Poison / violet | Poison - Enemy - Violet Miasma | 8 damage plus 4 damage/sec for 5s | Terra - Nema - Venen |
| Crystal / turquoise | Strike - Enemy - Prism Lance | 18 damage; caster gains a 25-point ward for 4s when released | Terra - Aegis - Prisma |

Crystal's protective ward is a secondary self buff, not a shield applied to its enemy. Its hostile circle encodes the lance attack. This first implementation does not give the ward its own second circle.

Cast times are 1.1–1.8 seconds, projectile speeds 700–1100 cm/sec, cooldowns 3.6–6 seconds. These are editable initial balance values, not final combat tuning. TP is capped at 100 and regenerates at 8/sec, matching the current GDD. Costs range from 12 to 20. The caster pays once at charge start; interruption consumes that cost and starts a short recovery. Range and line of sight are checked at start and release.

## Runtime and content

All new content is under `/Game/IsekaiVillage/Magic/Slimes`:

- `DA_<Color>Spell`: editable spell language, timings, color, status, textures and FX.
- `BP_<Name>SlimeMage`: existing approved skeletal mesh/Idle/Attack/Death animations, native casting and health behavior.
- `Map_SlimeMagic`: six independent training lanes; Play runs the spell cycles against damage-receiving targets. Editor rune plates are hidden in play, so runtime circles are not doubled.
- `M_RunicSentence`, `M_RunicStroke`, six rune textures and six preview instances.

Reuses the existing `ProceduralMagicCircle` class and `MagicCircleGeometry` functions. Semantic textures/tints are opt-in, preserving ordinary player circles. Reuses SlashTrail_SoftTofu Nature, Water, Fire, Ice and Dark Niagara families; Dark is a purple visual source for poison, not an additional gameplay element. Crystal currently uses the Ice family recolored turquoise. Original slime meshes/materials/animations are untouched.

Place a slime Blueprint in an encounter: by default it targets player pawn 0 within 1400cm and casts while stationary. Existing overworld encounter avatars and wave spawners are **not automatically replaced**. These mage actors are combat actors, not a replacement for encounter transitions or navigation AI. Disable Auto Cast and call Try Cast for controlled encounters. Interrupt Cast cancels charging. Ailments use the receiver's existing TakeDamage method and attach a reusable RunicAilmentComponent when necessary; the existing player HP implementation therefore receives hits and damage over time.

Burn/poison refresh without stacking their damage rates; bind takes priority over chill; movement speed restores when both expire. Water push uses character movement. Crystal ward absorbs incoming damage before HP. Slime faction actors are excluded from their own projectiles. Projectiles sweep their travel segment, preventing fast-frame tunneling. Death cancels a cast and cleans up the circle. This is a single-player implementation; multiplayer replication is not supplied.

## Verification and continuation

`Scripts/build_slime_runes.py` rebuilds source art and checks font character coverage. `Scripts/setup_slime_magic.py` imports only the new magic content and creates the separate map. `IsekaiVillage.Magic.SlimeRunicRules` automation covers semantic grammar, cost/reentrancy/interrupts, friendly targeting, non-stacking time-based damage, slow precedence/restoration, ward overflow and swept projectile damage.

See `Saved/slime_magic_setup.json`, the automation report, and the final chat message for actual verification results. A successful source build alone is not visual or gameplay approval. Future work can add voiced chants, navigation/chase logic, a second self-ward circle, and encounter-spawner integration without changing the approved slime art or the spell grammar.
