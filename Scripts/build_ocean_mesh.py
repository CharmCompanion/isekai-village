from pathlib import Path
import numpy as np
S=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Saved/AdventureWorldSource')
axis=sorted(set([-100000,-50000,-20000,-10000,-6000]+list(np.arange(-4000,-800,100))+list(np.arange(-800,801,10))+list(np.arange(900,4001,100))+[6000,10000,20000,50000,100000]));n=len(axis)
with (S/'SM_Coastal_Ocean_Surface.obj').open('w') as f:
    f.write('# Dense coastal ocean with sparse horizon rings; centimetres\n')
    for y in axis:
        for x in axis:f.write(f'v {x*100:.2f} {-y*100:.2f} 0\n')
    for y in axis:
        for x in axis:f.write(f'vt {x/100:.5f} {y/100:.5f}\n')
    for j in range(n-1):
        for i in range(n-1):
            a=j*n+i+1;b=a+1;c=b+n;d=a+n
            f.write(f'f {a}/{a} {b}/{b} {c}/{c}\nf {a}/{a} {c}/{c} {d}/{d}\n')
print(n*n,'ocean vertices')
