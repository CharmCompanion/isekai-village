from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/refine_scenic_mesh_v30.py');s=p.read_text();s=s.replace("chosen=(np.linalg.norm", "urban=map_coordinates(data['urban'].astype(float),coords,order=0,mode='constant')\n  chosen=(np.linalg.norm").replace("((mountain>.3)&(lengths>380)))","((mountain>.3)&(lengths>380))|((urban>.5)&(lengths>110)))")
p.write_text(s)
