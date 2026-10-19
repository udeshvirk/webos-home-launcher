#!/usr/bin/env python3
"""Call one Luna method over the configured root SSH alias; print validated JSON."""
import json,pathlib,shlex,subprocess,sys
if len(sys.argv)!=3:
    raise SystemExit('Usage: python3 scripts/luna.py luna://SERVICE/METHOD JSON_OR_@FILE')
uri,payload=sys.argv[1:]
if not uri.startswith('luna://') or any(c in uri for c in '\n\r\x00'):
    raise SystemExit('Expected a Luna URI')
data=json.loads(pathlib.Path(payload[1:]).read_text() if payload.startswith('@') else payload)
args=['luna-send','-w','5000','-n','1','-f',uri,json.dumps(data,separators=(',',':'))]
wrapper=pathlib.Path(__file__).resolve().parent/'tv-ssh'
r=subprocess.run([str(wrapper),'--tty',' '.join(shlex.quote(x) for x in args)],capture_output=True,text=True)
if r.returncode:
    raise SystemExit('SSH/Luna call failed; inspect the local connection (no payload printed).')
start=r.stdout.find('{')
if start<0: raise SystemExit('No JSON response. Check TTY behavior and service availability.')
result,_=json.JSONDecoder().raw_decode(r.stdout[start:])
print(json.dumps(result,indent=2))
if result.get('returnValue') is False: sys.exit(1)
