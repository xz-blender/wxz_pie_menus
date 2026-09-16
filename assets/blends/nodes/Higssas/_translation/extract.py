import bpy, json, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
for label, filename in [('v8','Higgsas Nodes v8.blend'), ('v13','Blender 5.0 Higgsas Geo Node Groups v13.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(root / filename))
    groups = []
    for g in bpy.data.node_groups:
        groups.append(dict(name=g.name, description=g.description, asset_description=g.asset_data.description if g.asset_data else '', asset=bool(g.asset_data), catalog=g.asset_data.catalog_id if g.asset_data else '', interface=[dict(name=i.name, description=getattr(i,'description',''), identifier=getattr(i,'identifier',''), kind=i.item_type) for i in g.interface.items_tree], nodes=[dict(name=n.name,label=n.label,type=n.bl_idname) for n in g.nodes]))
    (root / '_translation' / (label+'.json')).write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf-8')
    print(label, len(groups), 'groups', sum(g['asset'] for g in groups), 'assets')
