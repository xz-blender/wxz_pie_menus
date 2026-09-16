import bpy,json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'Blender 5.0 Higgsas Geo Node Groups v13.blend'))
strings=set()
for g in bpy.data.node_groups:
    for n in g.nodes:
        for attr in ('enum_items','index_switch_items'):
            for i in getattr(n,attr,[]):
                if getattr(i,'name',''): strings.add(i.name)
                if getattr(i,'description',''): strings.add(i.description)
(root/'_translation'/'menus.json').write_text(json.dumps(sorted(strings),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(sorted(strings),ensure_ascii=False))
