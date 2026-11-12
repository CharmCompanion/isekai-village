from pathlib import Path
p=Path('D:/DEVELOPMENT/Games/Tower of Elrhun/Scripts/import_corrected_equipment.py')
exec(compile(p.read_text(),str(p),'exec'),{'__name__':'__main__','roles_to_import':['Tank']})
