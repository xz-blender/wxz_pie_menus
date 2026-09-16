import json,pathlib,sys,collections
p=pathlib.Path(__file__).parent
a=json.loads((p/'before.json').read_text(encoding='utf8')); b=json.loads((p/(sys.argv[1] if len(sys.argv)>1 else 'after.json')).read_text(encoding='utf8'))
diffs=[]
def diff(a,b,path=''):
    if type(a)!=type(b): diffs.append((path,a,b))
    elif isinstance(a,dict):
        for k in a.keys()|b.keys():
            if k not in a or k not in b: diffs.append((path+'/'+k,k in a,k in b))
            else: diff(a[k],b[k],path+'/'+k)
    elif isinstance(a,list):
        if len(a)!=len(b): diffs.append((path+'/length',len(a),len(b)))
        else:
            for i,(x,y) in enumerate(zip(a,b)): diff(x,y,path+'/'+str(i))
    elif a!=b: diffs.append((path,a,b))
diff(a,b)
print('TOTAL',len(diffs));print(collections.Counter(d[0].split('/')[-1] for d in diffs))
for d in diffs[:45]: print(d)
