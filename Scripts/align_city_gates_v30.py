from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/build_civilizations_v30.py');s=p.read_text()
s=s.replace("def ringwall(x,y,r,n,scale=1,site=None):\n pts=[]", "def ringwall(x,y,r,n,scale=1,site=None):\n n=max(24,int(round(n/4))*4);pts=[]")
s=s.replace("for a in np.linspace(0,2*np.pi,n+1):pts.append", "for a in np.linspace(-np.pi/n,2*np.pi-np.pi/n,n+1):pts.append")
s=s.replace("ribbon([[x+25*np.sin(t/(r*.5)),y+t] for t in np.linspace(-r*.9,r*.9,35)],19 if kind=='city' else 10)","ribbon([[x,y+t] for t in np.linspace(-r*.9,r*.9,35)],19 if kind=='city' else 10)")
p.write_text(s)
