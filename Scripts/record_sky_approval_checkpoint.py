"""Record the resolved atmosphere decision; no Unreal edits."""
from pathlib import Path
import json
B=Path('D:/DEVELOPMENT/Games/IsekaiVillage');D=B/'Docs/WorldDesign'
p=D/'GOSAIN59_CHECKPOINT.md';s=p.read_text(encoding='utf-8');start=s.index('## Shared atmosphere');end=s.index('## Remaining work',start)
s=s[:start]+'''## Shared atmosphere — approved and saved

On 31 October 2026 the user selected **Apply tested sky correction (Recommended)**. The shared SkyAtmosphere height is now -20,600 m, matching continent sea level. Only its location changed. The before-map backup and exact transforms are recorded in `ArtSource/World/Gosain58/atmosphere_applied.json`.

Native saved-scene captures are in `Docs/WorldDesign/Gosain58_ApprovedSky`: `Gosain_Saved.png` and `ElRuhn_Saved.png`. Both were inspected: the Gosain blue cutoff is gone; El Ruhn retains its geometry with the approved darker sky/contrast. The earlier comparison folder remains historical preview evidence. No decision is pending.

The user then requested a separate copy of El Ruhn above a sea of clouds with five levitation stones and a grand magical tower. Track that work in `EL_RUHN_SKY_MAP.md`. It does not replace Gosain's unfinished regional work.

'''+s[end:]
s=s.replace('2. Resolve the pending shared sky decision. The corrected preview is substantially clearer, but it changes the protected island\'s atmosphere.','2. Shared sky decision resolved, applied and visually checked on 31 October 2026; see above.')
p.write_text(s,encoding='utf-8')
for name in ['GOSAIN58_CHECKPOINT.md','WORLD_REBUILD_CHECKLIST.md']:
 p=D/name;s=p.read_text(encoding='utf-8');note='''> 31 October 2026 update: the user explicitly approved the tested shared sky correction. It is saved and native Gosain/El Ruhn views were checked in `Gosain58_ApprovedSky`. Any pending-approval wording below is historical. Current new-map work: `EL_RUHN_SKY_MAP.md`.

''';p.write_text(note+s,encoding='utf-8')
(D/'Gosain58_ApprovedSky/review.json').write_text(json.dumps({'status':'native_views_inspected','approved':True,'gosain_blue_cutoff_removed':True,'elruhn_appearance_matches_approved_change':True,'remaining_limits':['Gosain terrain/architecture polish remains unfinished.','Existing broad slopes and repetitive trees are not fixed by atmosphere.']},indent=2))
