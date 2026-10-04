> Superseded by [Rock_Rim_v10.md](Rock_Rim_v10.md).

# Organic underside revision v09

Map: `/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure`.

Replaced the five regular rings of 306 rock pieces with a continuous, asymmetrical bedrock shell. The terrain seam follows the existing island outline. Irregular fracture planes, diagonal recesses, variable taper and an offset lowest point replace the evenly stacked courses. 104 SoStylized rock pieces are embedded at varying angles and depths, including the upper sides. The material has less uniform fill light and subdued tilted colour strata.

The upper native Landscape, lake, village, farm, forests, roads, dock and build reservations were not edited in this revision.

Previous underside actors and core remain in the map under `Archived/Regular Underside v08`, hidden at component level with collision disabled. The new actors are under `Floating Island/Organic Bedrock` and tagged `IVOrganic09`. Pre-change map: `Saved/WorldBackups/BeforeOrganicUnderside_v09/Map_AnimeAdventure.umap`.

Source mesh: `Saved/AdventureWorldSource/SM_IV_OrganicUnderside_v09.obj`. Authoring: `Scripts/build_organic_underside_v09.py` and `Scripts/apply_organic_underside_v09.py`. The application only replaces actors tagged for this underside revision; it archives the older underside.

The core has 16,385 vertices and 32,512 triangles. Topology validation found no non-manifold edges or interior holes; the only open boundary is the 256-edge terrain rim. The 16 native Landscape collision samples were rechecked. Images `Organic_Underside_Overview.png`, `Organic_Underside_Close.png`, and `Organic_Underside_Reverse.png` are actual Unreal renders.

This revision addresses the rock silhouette and surface structure. Packaged performance and full player traversal remain outside this visual revision.

