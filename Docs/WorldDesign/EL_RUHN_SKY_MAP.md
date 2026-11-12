# El Ruhn — dedicated sky kingdom

31 October 2026. Current user request: copy the existing El Ruhn island to a new map, a permanent sea of clouds beneath it, five large magical stones with horizontal circles at their midpoints, a horizontal island levitation circle below village height, and a fantastical tower with a grand manhwa-inspired entrance.

## Design and references

Retain the existing island landscape, lake, village paths, foliage and rock foundation. Remove the distant mainland only in the new map. Position the cloud deck below the rock tip so the full floating mass remains readable. Five megaliths form a support constellation, with cyan wind seals and an annular island covenant; they are environmental magic, not new combat elements.

The Tower of the Five Winds has ivory masonry, slender buttresses, dark teal vaulted roofs, recessed luminous windows, gold ribs and a suspended crystal crown. Its base stands at the horizontal center of the island and its levitation rings. A stairway faces the fountain square to the south. Streets wrap around the tower, connect the residential parcels and skirt the farm.

Research, interpreted as principles rather than copied models:

- [Mick Jundt — Wizard Tower](https://awfulwaffles.artstation.com/projects/R3m04e): stylized tower and surrounding grounds, with distinct architectural, material and foliage treatment.
- [Emil Tudor Vranceanu — An Evil Tower](https://aemilion.artstation.com/projects/BkLJ8A): supernatural architecture using strong forms, color contrast and atmospheric effects. Our version is welcoming and luminous.
- [Gray Chen — TDF project 03](https://graychen.artstation.com/projects/rzRnX5): suspended architecture and a deliberate arrival sequence; clouds and light should clarify scale.

Rune language follows `Docs/Slime_Runic_Magic.md` and the current GDD. Use the supplied SpellRunes font and Effect - Target - Spell sentence form. Wind has fivefold geometry. Proposed environmental sentences: `Sustain - Island - Heavenly Ascent` and `Sustain - Island - Fivefold Covenant`. These do not change the four-element gameplay system.

## Files and preservation

- Source map: `/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure`.
- Target map: `/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky`.
- Tower and levitation assets are in `/Game/IsekaiVillage/AdventureWorld/ElRuhnSky01`. Village streets, plot surfaces, placement previews and landscape painting are in `/Game/IsekaiVillage/AdventureWorld/ElRuhnSky02`.
- Geometry sources and verification reports are in `ArtSource/World/ElRuhnSky01` and `ArtSource/World/ElRuhnSky02`.
- Native village previews belong in `Docs/WorldDesign/ElRuhnSky02`. The earlier `ElRuhnSky01` images show the previous tower location.
- Build sources: `Scripts/build_elruhn_sky01_assets.py`; native scripts use the `elruhn_sky` prefix.

The previously previewed shared atmosphere correction was separately approved by the user and saved on 31 October 2026. Its record is `ArtSource/World/Gosain58/atmosphere_applied.json`. It predates this copy; no further changes to the original world are needed for the new sky map.

## Completion status

The dedicated map contains five support stones, five animated horizontal wind seals, an island-scale halo and rune band, a 197 m tower exterior with ceremonial stairs, 180 painted cloud accents and a continuous volumetric cloud layer. The tower interior remains to be built.

The shared pivot is the horizontal center of the visible native rim and rock foundation, **(1.0775, 19.84) m**. The tower stands on that axis at 25.11 m elevation. Both island rings use that center. Five stone centers sit 72 degrees apart at a radius of 868 m. Each local circle passes through its stone's midpoint at an elevation of −120 m. The measurements are in `ArtSource/World/ElRuhnSky01/centering_applied.json`.

Scope check: the source world file matches the SHA-256 recorded before isolating the new map. The copied map retains its native Landscape, rock foundation and 105,411 original island foliage instances before local tower-footprint clearance. 186,701 distant instances and 890 outside/archived actors were removed only from the copy. No existing pack meshes or materials were overwritten.

## Building the village in play

The village has 28 parcels of unassigned land. The player chooses both the building and the parcel. A street frontage fixes the center of each building, and the player can rotate its entrance in quarter turns. The farm, fountain gardens, tower approach and roads are reserved. Eight existing buildings form the settled neighborhood, and the farmhouse stays beside the fields.

1. Open `Map_ElRuhnSky` in Unreal and press Play. Press **B** for the building catalogue.
2. Scroll to a building. Aim at an open parcel or walk to its entrance stake. A translucent model previews its footprint. Press **R** to rotate it.
3. **Left click** or press **T** to confirm. The game charges the displayed construction materials and records that building as the use of that parcel. **B** or **right click** cancels a preview.

The **inherited home** is a one-time deed with no material cost. The **Adventurers guild** also has a player-selected site and allows one guild hall. The 18 catalogue choices include three commoner home styles, an inn, a general shop, a blacksmith, a church, a knight school, a warehouse, a bakery, a bank, a bathhouse, a bell house, a magic academy, a noble residence and the lord’s residence, alongside the two founding buildings. The catalogue uses the project’s existing Village, Large Town and Kingdom progression rules. Specialist buildings currently share exterior models from Fantastic Village Pack.

The simulation reads the confirmed building use for beds, services and citizen destinations. A placed shop supports trade at its own entrance. A guild or smithy uses the existing hiring desk or forge interaction. The map-specific construction save `ElRuhnSky_Village02` records each chosen building, parcel, orientation and house loft. Inventory and the rest of the village simulation have their own lifecycles.
