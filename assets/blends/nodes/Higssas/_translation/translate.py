import bpy, json, pathlib, hashlib, uuid, math

root=pathlib.Path(__file__).resolve().parents[1]
work=root/'_translation'
out=root/'v13_中文版'
out.mkdir(exist_ok=True)
source=root/'Blender 5.0 Higgsas Geo Node Groups v13.blend'
destination=out/'Higgsas Nodes v13 中文版.blend'
names=dict(line.split('\t',1) for line in (work/'names.tsv').read_text(encoding='utf8').splitlines() if line)
dictionary=json.loads((work/'dictionary.json').read_text(encoding='utf8'))
reverse={'HIG_'+v:k for k,v in names.items()}
assert len(reverse)==len(names), 'Duplicate translated group names'
def tr(s):
    if not s: return s
    if s in dictionary.values(): return s
    assert s in dictionary, repr(s)
    return dictionary[s]
def canonical(value):
    if isinstance(value,bpy.types.ID): return [value.bl_rna.identifier,reverse.get(value.name,value.name)]
    if isinstance(value,(bool,int,str)) or value is None: return value
    if isinstance(value,float): return value if math.isfinite(value) else str(value)
    try: return [canonical(v) for v in value]
    except TypeError: return str(value)
def properties(obj,skip=()):
    data={}
    for p in obj.bl_rna.properties:
        if p.identifier in {'rna_type','name','label','description'} | set(skip) or p.type=='COLLECTION': continue
        if p.type=='POINTER':
            v=getattr(obj,p.identifier,None)
            if isinstance(v,bpy.types.ID): data[p.identifier]=canonical(v)
        else:
            try:
                value=getattr(obj,p.identifier)
                if p.identifier=='default_value' and 'Menu' in obj.bl_rna.identifier and isinstance(value,str):
                    value=dictionary.get(value,value)
                data[p.identifier]=canonical(value)
            except (AttributeError,TypeError): pass
    return data
def snapshot():
    result={}
    for g in bpy.data.node_groups:
        nodes=[]
        for n in g.nodes:
            nodes.append(dict(name=n.name,props=properties(n,('dimensions','warning_propagation')), inputs=[properties(s,('is_linked',)) for s in n.inputs],outputs=[properties(s,('is_linked',)) for s in n.outputs], enums=[properties(e) for e in getattr(n,'enum_items',[])]))
        links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier,l.is_muted) for l in g.links)
        result[reverse.get(g.name,g.name)]=dict(type=g.bl_idname,nodes=nodes,links=links,interface=[properties(i) for i in g.interface.items_tree],asset=bool(g.asset_data))
    return result

bpy.ops.wm.open_mainfile(filepath=str(source))
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
before=snapshot()
catalog_map={}
catalog_lines=['# Higgsas v13 中文资产分类；独立UUID可与英文版、v8并存。','VERSION 1','']
cat_terms={'Higgsas Nodes':'Higgsas Nodes v13 中文','Camera':'相机','Curve':'曲线','Curve Primitives':'基础曲线','Deformers':'形变','Distribution':'分布','Falloffs':'衰减','Generate':'生成器','Geometry Measure':'几何测量','Image':'图像','Instance':'实例','Linear Algebra':'线性代数','Mesh Primitives':'基础形状','SDF Nodes':'SDF节点','Selection':'选择','Simulation':'模拟','UV':'UV','Utilities':'实用工具','Vector Fields':'矢量场'}
for line in (root/'blender_assets.cats-new.txt').read_text(encoding='utf8').splitlines():
    if not line or line.startswith('#') or line.startswith('VERSION'): continue
    cid,path,simple=line.split(':',2)
    translated_path='/'.join(cat_terms[p] for p in path.split('/'))
    new_id=str(uuid.uuid5(uuid.NAMESPACE_URL,'higgsas-v13-zh-CN/'+cid))
    catalog_map[cid]=new_id
    catalog_lines.append(':'.join([new_id,translated_path,translated_path.replace('/','-')]))

stats={'groups':len(bpy.data.node_groups),'assets':0,'interfaces':0,'menu_items':0,'labels':0,'descriptions':0}
asset_records=[]
for g in list(bpy.data.node_groups):
    original=g.name
    if original in names: g.name='HIG_'+names[original]
    if g.description:
        g.description=tr(g.description); stats['descriptions']+=1
    if g.asset_data:
        stats['assets']+=1
        a=g.asset_data
        old_desc=a.description
        a.description=(tr(old_desc)+'\n' if old_desc else '')+'原名：'+original
        assert a.catalog_id in catalog_map,(original,a.catalog_id)
        a.catalog_id=catalog_map[a.catalog_id]
        # Keep author's existing tags, and allow searching by the original name.
        a.tags.new(original,skip_if_exists=True)
        asset_records.append({'original':original,'translated':g.name,'catalog_id':a.catalog_id})
    for i in g.interface.items_tree:
        old=i.name
        i.name=tr(old)
        stats['interfaces']+=int(i.name!=old)
        if getattr(i,'description',''):
            i.description=tr(i.description); stats['descriptions']+=1
    for n in g.nodes:
        if n.label:
            n.label=tr(n.label); stats['labels']+=1
        for e in getattr(n,'enum_items',[]):
            old=e.name
            e.name=tr(old)
            stats['menu_items']+=int(e.name!=old)
            if e.description: e.description=tr(e.description)

after=snapshot()
if before!=after:
    (work/'before.json').write_text(json.dumps(before,ensure_ascii=False,indent=2),encoding='utf8')
    (work/'after.json').write_text(json.dumps(after,ensure_ascii=False,indent=2),encoding='utf8')
    raise AssertionError('Node structure changed; inspect before.json/after.json')
bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(destination))
reopened=snapshot()
if before!=reopened:
    (work/'before.json').write_text(json.dumps(before,ensure_ascii=False,indent=2),encoding='utf8')
    (work/'reopened.json').write_text(json.dumps(reopened,ensure_ascii=False,indent=2),encoding='utf8')
    raise AssertionError('Reopened structure differs')
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
assert all(g.name.startswith('HIG_') for g in bpy.data.node_groups if g.asset_data)
assert all(g.asset_data.catalog_id in catalog_map.values() for g in bpy.data.node_groups if g.asset_data)
(out/'blender_assets.cats.txt').write_text('\n'.join(catalog_lines)+'\n',encoding='utf8')
(out/'节点名称中英对照.tsv').write_text('原名\t中文名称\n'+'\n'.join(r['original']+'\t'+r['translated'] for r in sorted(asset_records,key=lambda r:r['original'])),encoding='utf-8-sig')
report=dict(stats=stats,blender_version=bpy.app.version_string,source_sha256=source_hash,output_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),structure_unchanged=True,reopen_verified=True,catalogs=len(catalog_map),assets=asset_records)
(out/'translation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('TRANSLATION_VERIFIED',json.dumps(stats),str(destination))
