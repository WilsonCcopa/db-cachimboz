"""Import reviewed exam packages, validate their contents, and publish in order."""
import base64,concurrent.futures,hashlib,json,os,subprocess,tempfile,time,urllib.request,zipfile
from pathlib import Path,PurePosixPath

REPO='WilsonCcopa/db-cachimboz'
assert os.environ['GITHUB_REPOSITORY']==REPO
TOKEN=os.environ['GH_TOKEN']
API='https://api.github.com/repos/'+REPO
SOURCE='https://raw.githubusercontent.com/'+REPO+'/'+os.environ['GITHUB_SHA']

def get(url,raw=False):
    headers={'Authorization':'Bearer '+TOKEN,'Accept':'application/vnd.github.raw+json' if raw else 'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=120) as r:
                b=r.read();typ=r.headers.get('content-type','')
            if raw and 'json' in typ:
                v=json.loads(b)
                if v.get('encoding')=='base64':return base64.b64decode(v['content'])
            return b
        except Exception:
            if attempt==3:raise
            time.sleep(2**attempt)

request=json.loads(get(SOURCE+'/.github/exam-import/request.json'))
assert request['repository']==REPO
assert isinstance(request.get('dryRun'),bool),'request must explicitly choose dryRun'
assert [x['university'] for x in request['packages']] in [['UNMSM','UNI','UNSA'],['UNMSM','UNI','UNSA','CATALOG']]
tmp=Path(tempfile.mkdtemp(prefix='exam-import-'));checkout=tmp/'repo'

def git(*args,check=True,auth=False):
    env=os.environ.copy()
    if auth:
        env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',GIT_CONFIG_VALUE_0='AUTHORIZATION: basic '+base64.b64encode(('x-access-token:'+TOKEN).encode()).decode())
    return subprocess.run(['git',*args],cwd=checkout if checkout.exists() else tmp,env=env,check=check,capture_output=True,text=True).stdout.strip()

git('clone','--quiet','--single-branch','--branch','main','https://github.com/'+REPO+'.git',str(checkout))
assert git('rev-parse','HEAD')==request['expectedMain'],'main changed; prepare a fresh request after review'
git('config','user.name','github-actions[bot]');git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
git('config','core.autocrlf','false')
commits=[]
for package in request['packages']:
    archive=tmp/(package['university']+'.zip')
    def download(part):
        data=get(API+'/git/blobs/'+part['sha'],raw=True)
        assert len(data)==part['bytes']
        assert hashlib.sha256(data).hexdigest()==part['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==part['sha']
        out=tmp/(package['university']+str(part['index'])+'.part');out.write_bytes(data)
        return part['index'],out
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:parts=sorted(pool.map(download,package['parts']))
    with archive.open('wb') as out:
        for _,p in parts:out.write(p.read_bytes());p.unlink()
    assert archive.stat().st_size==package['archiveBytes']
    with archive.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==package['archiveSha256']
    allowed={entry['path']:entry for entry in package['entries']}
    assert len(allowed)==package['files']
    with zipfile.ZipFile(archive) as z:
        assert len(z.infolist())==len(allowed)
        assert set(z.namelist())==set(allowed)
        for info in z.infolist():
            rel=PurePosixPath(info.filename)
            assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in info.filename
            assert info.filename.startswith(('assets/exams/','admission/v1/','exams/')) or (len(rel.parts)==1 and (info.filename.endswith('.json') or info.filename=='README.md'))
            data=z.read(info)
            assert len(data)==allowed[info.filename]['bytes']
            assert hashlib.sha256(data).hexdigest()==allowed[info.filename]['sha256']
            target=checkout.joinpath(*rel.parts);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Add only the reviewed package paths; no unrelated work can enter the commit.
    for start in range(0,len(allowed),200):git('add','--',*list(allowed)[start:start+200])
    assert set(git('diff','--cached','--name-only').splitlines())<=set(allowed)
    # Verify the staged bytes, including any repository attribute filters.
    staged=git('ls-files','--stage').splitlines()
    staged_hashes={line.split('\t',1)[1]:line.split()[1] for line in staged}
    for name in allowed:
        data=(checkout/name).read_bytes()
        expected_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert staged_hashes[name]==expected_blob,('staged bytes changed',name)
    git('commit','--quiet','-m',package['message'])
    commits.append({'university':package['university'],'sha':git('rev-parse','HEAD')})
    print(package['university']+': '+str(package['files'])+' verified files prepared',flush=True)
    archive.unlink()

# One normal fast-forward push publishes the three ordered university commits.
if not request.get('dryRun',False):git('push','origin','HEAD:main',auth=True)
print(json.dumps({'status':'dry-run-passed' if request.get('dryRun',False) else 'published','commits':commits}),flush=True)
with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf8') as f:
    for c in commits:f.write('- '+c['university']+': https://github.com/'+REPO+'/commit/'+c['sha']+'\n')
