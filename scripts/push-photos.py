#!/usr/bin/env python3
"""Resize local photos and copy over SSH. Requires macOS sips; originals stay untouched."""
import argparse,hashlib,json,pathlib,re,shlex,shutil,subprocess,sys,tarfile,tempfile,unicodedata
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('source',type=pathlib.Path)
p.add_argument('--target',choices=['wallpapers','screensaver','both'],default='screensaver')
p.add_argument('--replace',action='store_true',help='Replace selected active photo sets after making backups')
p.add_argument('--prepare-only',type=pathlib.Path,help='Save converted copies locally without touching the TV')
p.add_argument('--report',type=pathlib.Path)
a=p.parse_args();base=pathlib.Path(__file__).resolve().parent.parent
targets=['wallpapers','screensaver'] if a.target=='both' else [a.target]
extensions={'.jpg','.jpeg','.png','.heic','.heif','.avif','.webp','.bmp','.tif','.tiff'}
files=sorted(x for x in a.source.iterdir() if x.is_file() and not x.name.startswith('.'))
report={'source':str(a.source.resolve()),'target':a.target,'replace':a.replace,'converted':[],'skipped':[]}
with tempfile.TemporaryDirectory(prefix='lg-photos-') as temp:
 stage=pathlib.Path(temp);out=stage/'payload';out.mkdir()
 for i,f in enumerate(files):
  if f.suffix.lower() not in extensions:
   report['skipped'].append({'file':f.name,'reason':'Unsupported image extension'});continue
  slug=unicodedata.normalize('NFKD',f.stem).encode('ascii','ignore').decode()
  slug=re.sub(r'^\d+[-_ ]*','',slug)
  slug=re.sub(r'[^A-Za-z0-9]+','-',slug).strip('-')[:56]
  name=f'{i+1:02d}-{slug or hashlib.sha256(f.name.encode()).hexdigest()[:10]}.jpg'
  converted=stage/name
  r=subprocess.run(['sips','-s','format','jpeg','-s','formatOptions','78','-Z','1920',str(f),'--out',str(converted)],capture_output=True,text=True)
  if r.returncode or not converted.exists() or converted.read_bytes()[:2]!=b'\xff\xd8':
   report['skipped'].append({'file':f.name,'reason':(r.stderr or r.stdout or 'JPEG conversion failed').strip()[:500]});continue
  dimensions=subprocess.run(['sips','-g','pixelWidth','-g','pixelHeight',str(converted)],capture_output=True,text=True,check=True).stdout
  width=int(re.search(r'pixelWidth:\s+(\d+)',dimensions).group(1));height=int(re.search(r'pixelHeight:\s+(\d+)',dimensions).group(1))
  if max(width,height)>1920 or min(width,height)<1:raise SystemExit('Unexpected output dimensions; TV has not been touched')
  for target in targets:
   d=out/target;d.mkdir(exist_ok=True);shutil.copy2(converted,d/name)
   if target=='wallpapers':
    thumbs=d/'thumbs';thumbs.mkdir(exist_ok=True)
    subprocess.run(['sips','-s','format','jpeg','-s','formatOptions','70','-Z','320',str(converted),'--out',str(thumbs/name)],check=True,stdout=subprocess.DEVNULL)
  report['converted'].append({'source':f.name,'file':name,'sourceExtension':f.suffix.lower(),'width':width,'height':height,'bytes':converted.stat().st_size})
 if not report['converted']:raise SystemExit('No images converted successfully; TV unchanged')
 if a.prepare_only:
  a.prepare_only.mkdir(parents=True,exist_ok=True)
  for target in targets:shutil.copytree(out/target,a.prepare_only/target,dirs_exist_ok=True)
  report['preparedOnly']=str(a.prepare_only.resolve())
 else:
  archive=stage/'photos.tgz'
  with tarfile.open(archive,'w:gz') as t:
   for target in targets:t.add(out/target,arcname=target)
  command='''set -eu
DATA=/var/lib/webos-home
APP=/media/developer/apps/usr/palm/applications/org.local.weboshome
mkdir -p "$DATA/wallpapers" "$DATA/screensaver" "$DATA/photo-backups"
STAMP=$(date +%Y%m%dT%H%M%S)-$$
BACKUP="$DATA/photo-backups/photos-$STAMP.tgz"
tar -czf "$BACKUP" -C "$DATA" wallpapers screensaver
STAGE=$(mktemp -d "$DATA/.photo-import.XXXXXX")
trap 'rm -rf "$STAGE"' EXIT
tar -xzf - -C "$STAGE"
echo "BACKUP=$BACKUP"
'''
  for target in targets:
   command+='TARGET='+shlex.quote(target)+'\n'
   if a.replace:
    command+='''mv "$DATA/$TARGET" "$DATA/photo-backups/replaced-$STAMP-$TARGET"
mv "$STAGE/$TARGET" "$DATA/$TARGET"
'''
   else:command+='cp -a "$STAGE/$TARGET/." "$DATA/$TARGET/"\n'
   command+='''if test -d "$APP"; then
 mkdir -p "$APP/photo-library"
'''
   if a.replace:command+=' if test -d "$APP/photo-library/$TARGET"; then mv "$APP/photo-library/$TARGET" "$DATA/photo-backups/replaced-app-$STAMP-$TARGET"; fi\n'
   command+=' cp -a "$DATA/$TARGET" "$APP/photo-library/"\nfi\n'
  with archive.open('rb') as src:
   r=subprocess.run([str(base/'scripts/tv-ssh'),command],stdin=src,capture_output=True,text=False,check=True,timeout=120)
  result=r.stdout.decode();print(result.strip());report['backupOnTv']=re.search(r'^BACKUP=(.+)$',result,re.M).group(1)
 if a.report:
  a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
 print(f"Converted {len(report['converted'])} images; skipped {len(report['skipped'])}.")
 for skipped in report['skipped']:print('Skipped '+skipped['file']+': '+skipped['reason'])
 if not a.prepare_only:print('Copied to '+a.target+'. Reopen Home to refresh the photo list.')
