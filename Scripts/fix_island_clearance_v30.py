from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/prepare_civilized_world_v30.py');s=p.read_text().replace("place(q,wanted,comp)","if q['culture']=='citadel':q['radius_m']=850\n place(q,wanted,comp)")
s=s.replace("# A hierarchy of regional", "print({'existing_sites_placed':len(sites)},flush=True)\n# A hierarchy of regional")
s=s.replace("# Smooth inland foundation", "print({'expanded_sites':len(sites)},flush=True)\n# Smooth inland foundation")
s=s.replace("# Connected farm-lane", "print({'gridded_farms':len(farms)},flush=True)\n# Connected farm-lane")
p.write_text(s)
