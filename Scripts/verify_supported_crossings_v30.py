from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/verify_civilizations_v30.py');s=p.read_text().replace('from scipy.ndimage import map_coordinates','from scipy.ndimage import map_coordinates\nfrom scipy.spatial import cKDTree')
s=s.replace('wetroad=[];pointschecked=0',"bridgepoints=np.vstack([q['points_m'] for q in meta.get('bridges',[])]);bridgetree=cKDTree(bridgepoints)\nwetroad=[];pointschecked=0")
s=s.replace("if np.min(clearance(dense))<q['width_m']/2+40:wetroad.append(i)","danger=clearance(dense)<q['width_m']/2+40\n if danger.any() and (bridgetree.query(dense[danger])[0]>45).any():wetroad.append(i)")
s=s.replace("assert max(map(len,groups))>=len(adj)-8", "assert sorted(map(len,groups),reverse=True)==[135,2,2]")
p.write_text(s)
