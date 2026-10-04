# Smooth stylized content pass — v28

Art direction: cleaner sculpted forms and smoother shading, using the user's Fortnite reference as the direction. This is a refinement of the existing game assets and terrain, not a claim of equivalent production quality.

## Geometry and surfaces
- The paired island foundation is subdivided and relaxed: 132,481 vertices and 262,912 triangles. All 8,192 terrain-join vertices remain fixed, with a maximum internal relaxation of about 5.2 m. Its new inverse is used for the mainland opening.
- Three visibly coarse native rock meshes have smoother copied replacements with four times their source triangle counts, welded smooth normals, preserved UVs/materials and original placement envelopes. Applied across 1,247 rock instances and 37 actor references, including archived actors. Original pack assets remain available.
- Mainland terrain uses cubic height interpolation over a softened source field, with normals derived from that continuous surface. This removes much of the visible triangulation pattern instead of merely adding polygons.
- Distant slope shading samples a continuous world-space normal field rather than interpolated triangle normals, reducing sawtooth lighting along canyon walls and snowy ridges. This does not change the terrain silhouette.
- The mainland contains 1,057,377 vertices and 2,114,240 triangles. Steep surfaces have projected painted-rock texture detail. The island foundation has a separate material copy with less aggressive small normal detail and a controlled roughness/specular response.
- The playable Landscape, town layout, map geography, canyon, beaches and scattered oases are retained. Scene screenshots are captured at 1920 by 1080, including a closer playable-island view.

## Checks
The inverse fit has maximum error 2.3e-12 m, with no internal open edges or nonmanifold edges. Smoothed native rock bounds match their originals within 0.001 cm. The nearby river passes 1,201 exported-mesh samples with minimum clearance 2.23 m. All 768 native terrain-join traces and 96 underside collision traces passed, recorded in Saved/paired_join_validation_v28.json.
Added geometry has not been gameplay-performance benchmarked. Mainland detail remains scenic rather than a complete close-range playable continent.

## Continue work
Project: D:/DEVELOPMENT/Games/IsekaiVillage
Map: /Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure
Current scripts: Scripts/*_v28.py
New paired source: Saved/AdventureWorldSource/SM_IV_JoinedMountain_v28.obj
World source: Saved/AdventureWorldSource/world_design_v28.json
Rock asset source/audit: Saved/rock_sources_v28.json and Saved/smooth_rock_assets_applied_v28.json
Backup: Saved/WorldBackups/BeforeStylized_v28/Map_AnimeAdventure.umap
Editor rock application: request 183. Terrain and paired foundation application: request 184. Native join verification: request 185. Continuous scenic surface shading and final captures: request 186.
