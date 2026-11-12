# Gosain51 — southern royal lake refinement

## Accepted direction
Continue Gosain as a believable two-island kingdom. Left island retains 65% forest/lake allocation and compact castle town. Right island retains an equal town footprint, giant magic tower, knight school, mountain and future mine/port. Do not resume island-wide urban infill. Elhrun is protected.

## This stage
- Move lake toward southern/lower end: center (27000, 36300) world metres, about 2.5 km from previous center.
- Irregular elongated basin, approximately 1.56 km², with coves and projecting banks.
- Keep at least 514 m between basin outline and coastline; grade the banks inside this buffer.
- Restore old basin to rolling forest ground; regenerate private Gosain forest and adjust affected legacy foliage.
- Terminate woodland approach outside the new shoreline, avoiding a cross-lake road.
- Preserve terrain topology, XY coordinates, castle/towns and right island.

## Research translated into design
NPS describes karst landscapes as related caves, springs, sinking streams and dissolved bedrock. Utah Geological Survey's Ricks Spring is a real grotto issuing from a cave aquifer. Use a small rocky spring grotto with a short inlet, forested limestone ridges and mixed shallow/rocky shores. Magical glow, old carved stones and localized mist are proposed art direction, not established game lore.
- https://www.nps.gov/subjects/caves/karst-landscapes.htm/index.htm
- https://geology.utah.gov/map-pub/survey-notes/geosights/geosights-ricks-spring-cache-county/

## Ordered remaining work
1. Apply and visually inspect southern basin, restored old ground, tree clearance and approach path. Status is recorded in ArtSource/World/Gosain51/applied.json; source generation alone does not mean applied.
2. Small spring grotto, inlet, textured shore, forest glades and restrained magical detail. Check at ground level and distant map scale.
3. Right island: layered mountain foothills, wooded valleys, mine entrance and connected countryside paths. Preserve tower and school.
4. Port and royal estates; town/forest transitions and less circular district boundaries.
5. Collision, traversal, water/terrain seams, foliage performance and all-angle visual checks.
6. Regional continuation: desert oasis/cliff towns; waterless Kelsin; coastal resort country; farming/export nation. Separate checkpoints, preserve Elhrun.

Do not call this final/AAA or claim cave, port or mine gameplay is implemented without native evidence.

## 2026-10-23 saved progress
- `applied.json`: terrain, moved lake, restored old basin, approach route and forest saved.
- `refined.json`: corrected detached water patch caught in native view; broadened bank tree clearance and cleared grotto approach; saved.
- `grotto_applied.json`: twelve existing So Stylized rock pieces form a scenic lakeside recess. This is not a finished cave interior, spring simulation or dungeon.
- 30,074 private Gosain forest tree instances after shoreline/grotto clearance. Existing other foliage types were not touched by this pass.
- Source comparison to saved50: 1,277 terrain vertices changed, all within left island. XY and topology unchanged. Other-region/right-island terrain retained.
- Private lake material gives darker blue-green water without changing the shared water asset.
- Backups are under Saved/WorldBackups/BeforeGosain51*.
- Native review captured a first pass and initiated a second after corrections. Check screenshot timestamps and native review report for final inspected state.
- Right-island and wider-world stages remain outstanding. First complete shore/grotto detail, then proceed with right mountain, forested foothills, mine and port.

### Water continuity correction
Third native review follows replacement with SM_Gosain51_RoyalLakeContinuous. Water now extends underneath the banks instead of independently clipping each analytic sample; this avoids triangular missing-water gaps where the continent triangles differ from the sampled height function. Saved application: continuous_water.json. Source generator: build_gosain_v51_continuous_water.py.

Known art work: shore still needs material transitions, reeds and stones; the scenic grotto currently reads as a freestanding rock alcove and needs integration into a larger bank/outcrop. No finished cave gameplay or inlet is claimed. Woodland route is still visually straight and needs a later spline/grade pass.

Superseded for current terrain/shore detail by GOSAIN52_CHECKPOINT.md; keep this file for relocation history.
