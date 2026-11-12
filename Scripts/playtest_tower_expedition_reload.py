from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/Tower of Elrhun/Scripts/playtest_tower_expedition.py')
exec(compile(p.read_text(),str(p),'exec'),{'reload_pass':True,'__name__':'__main__'})
