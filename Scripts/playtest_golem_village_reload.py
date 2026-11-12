from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/Tower of Elrhun/Scripts/playtest_golem_village_loop.py')
exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__','reload_pass':True})
