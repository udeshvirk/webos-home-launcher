#!/usr/bin/env python3
"""Read this TV's launch points and cache its icons into ignored local build data."""
import json,pathlib,re,shlex,subprocess
base=pathlib.Path(__file__).resolve().parent.parent
ssh=str(base/'scripts/tv-ssh')
remote='/tmp/webos-home-launchpoints.json'
subprocess.run([ssh,'--tty',"luna-send -w 5000 -n 1 -f luna://com.webos.applicationManager/listLaunchPoints '{}' > "+remote],check=True)
r=subprocess.run([ssh,'cat '+remote],check=True,capture_output=True,text=True)
payload=json.loads(r.stdout)
if not payload.get('returnValue'): raise SystemExit('listLaunchPoints failed; no app list generated')
dest=base/'private/generated';(dest/'assets').mkdir(parents=True,exist_ok=True)
dest.parent.chmod(0o700);dest.chmod(0o700)
out=[];seen=set()
for app in payload.get('launchPoints',[]):
    appid=app.get('id','')
    if not re.fullmatch(r'[A-Za-z0-9._-]+',appid) or appid in seen: continue
    seen.add(appid)
    item={'id':appid,'title':app.get('title',appid),'params':{}}
    icon=app.get('icon','')
    if icon.startswith('file://'): icon=icon[7:]
    if icon.startswith('/') and not any(c in icon for c in '\r\n\x00'):
        data=subprocess.run([ssh,'cat -- '+shlex.quote(icon)],capture_output=True,check=False)
        ext=pathlib.Path(icon).suffix.lower()
        if data.returncode==0 and data.stdout and ext in {'.png','.jpg','.jpeg','.webp','.gif'}:
            name='assets/app-'+str(len(out))+ext
            (dest/name).write_bytes(data.stdout);item['packagedIcon']=name
    out.append(item)
(dest/'seed.js').write_text('window.SEED_APPS='+json.dumps(out)+';\n')
print('Cached',len(out),'launch points under private/generated; do not publish this directory.')
