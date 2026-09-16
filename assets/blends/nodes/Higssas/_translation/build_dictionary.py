import json, pathlib, re
root=pathlib.Path(__file__).resolve().parent
names=dict(line.split('\t',1) for line in (root/'names.tsv').read_text(encoding='utf8').splitlines() if line)
terms=dict(line.split('=',1) for line in (root/'terms.txt').read_text(encoding='utf8').splitlines() if line)
terms.update(names)
pattern=re.compile(r'(?<![A-Za-z])(?:'+ '|'.join(re.escape(x) for x in sorted(terms,key=len,reverse=True))+r')(?![A-Za-z])')
groups=json.loads((root/'v13.json').read_text(encoding='utf8'))
strings=set(json.loads((root/'menus.json').read_text(encoding='utf8')))
for g in groups:
    strings.update([g['description'],g['asset_description']])
    for i in g['interface']: strings.update([i['name'],i['description']])
    strings.update(n['label'] for n in g['nodes'])
strings.discard('')
result={}
for s in sorted(strings):
    stripped=s.strip()
    if stripped in terms: t=terms[stripped]
    else:
        t=pattern.sub(lambda m: terms[m.group()],stripped)
        t=re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])','',t)
        t=re.sub(r'^最小值(?=.)','最小',t)
        t=re.sub(r'^最大值(?=.)','最大',t)
    result[s]=t
(root/'dictionary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
(root/'dictionary_review.tsv').write_text('\n'.join(s+'\t'+t for s,t in result.items()),encoding='utf8')
allowed={'X','Y','Z','A','B','P','Q','W','U','V','T','N','M','F','K','Da','Db','ID','UV','AO','SDF','VDM','XYZ','ASCII','IWP','Sobel','Aizawa','Dadras','Halvorsen','Lorenz','Sprott','Wang','Sun','Floyd','Steinberg','Sierra','Hilbert','NURBS','Phi','Theta','Beta','Gamma','Catmull','Rom','Moore','Voronoi','Kruskal'}
print('UNTRANSLATED:')
for s,t in result.items():
    remaining=set(re.findall('[A-Za-z]+',t))-allowed
    if remaining and 'www.' not in t: print(s+' => '+t)
print('MISSING GROUPS:',[g['name'] for g in groups if g['name'] not in names and not g['name'].startswith('NodeGroup')])
print('Dictionary entries:',len(result))
