from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/IsekaiVillage/Scripts/prepare_civilized_world_v30.py');s=p.read_text();s=s.replace("stride=4;step=M*stride;walk=(clear>step*.8)&(slope<.38)&(D['cliff']<.10)&(np.hypot(X,Y)>18500)","""# Water keeps absolute priority. Land passes use a terrain cost rather than
# disconnecting whole provinces behind an arbitrary slope threshold.
localenv={};exec(compile((P/'build_puzzle_continent_v30.py').read_text().split('# Remaining branches')[0],'local water','exec'),localenv)
rd,lk,ww,wl,wa=localenv['hydro'](X,Y)
localwater=(np.hypot(X,Y)<15000)&(np.abs(Y)<12000)&((rd<ww+60)|(lk<1.12))
water=water|localwater;dry=~water;clear=distance_transform_edt(dry)*M
stride=4;step=M*stride;walk=(clear>step*.8)&(slope<1.20)&(np.hypot(X,Y)>9500)""")
s=s.replace("cost=(1+np.minimum(slope,1)*20+D['mountain']*5)","cost=(1+np.minimum(slope,2)*50+D['mountain']*6+D['cliff']*110)")
p.write_text(s)
