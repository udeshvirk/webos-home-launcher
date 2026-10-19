"""Offline helper checks. No real SSH connections or TV changes."""
import json
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class HelperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        fake = self.folder / 'ssh'
        fake.write_text('''#!/usr/bin/env python3
import json,os,shlex,sys
from pathlib import Path
args=shlex.split(sys.argv[-1])
if args[0]=='luna-send':
    payload=json.loads(args[-1])
    Path(os.environ['CALL_RECORD']).write_text(json.dumps({'argv':args,'payload':payload}))
    print(json.dumps({'returnValue':True}))
elif args==['cat','/tmp/webos-home-capture.png']:
    sys.stdout.buffer.write(b'\\x89PNG\\r\\n\\x1a\\n'+b'offline-fixture')
else:
    raise SystemExit('Unexpected remote command')
''')
        fake.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.folder)+os.pathsep+os.environ['PATH'],
                        TV_SSH_ALIAS='test-tv', CALL_RECORD=str(self.folder/'call.json'))

    def run_helper(self, name, *args):
        return subprocess.run([str(ROOT/'scripts'/name), *args], env=self.env,
                              capture_output=True, text=True)

    def test_payload_is_shell_quoted(self):
        marker = self.folder/'must-not-exist'
        data = {'text': "quote ' and $(touch "+str(marker)+') and `false`'}
        r = self.run_helper('luna.py', 'luna://example.service/read', json.dumps(data))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads((self.folder/'call.json').read_text())['payload'], data)
        self.assertFalse(marker.exists())

    def test_keycode_spelling_and_value(self):
        r = self.run_helper('key.sh', 'GREEN')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads((self.folder/'call.json').read_text())['payload'], {'keyCode':399})

    def test_invalid_key_never_calls_ssh(self):
        r = self.run_helper('key.sh', 'INVALID')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.folder/'call.json').exists())

    def test_capture_rejects_path_traversal(self):
        r = self.run_helper('capture.sh', '../outside')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.folder/'call.json').exists())

    def test_capture_payload_and_binary_copy(self):
        scripts = self.folder/'sandbox/scripts'
        scripts.mkdir(parents=True)
        for name in ('capture.sh', 'tv-ssh'):
            shutil.copy2(ROOT/'scripts'/name, scripts/name)
        r = subprocess.run([str(scripts/'capture.sh'), 'offline'], env=self.env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        call = json.loads((self.folder/'call.json').read_text())
        self.assertEqual(call['payload']['method'], 'DISPLAY')
        data = (scripts.parent/'private/screenshots/offline.png').read_bytes()
        self.assertTrue(data.startswith(b'\x89PNG\r\n\x1a\n'))

    def test_invalid_alias_never_calls_ssh(self):
        self.env['TV_SSH_ALIAS'] = '-oProxyCommand=anything'
        r = self.run_helper('key.sh', 'OK')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.folder/'call.json').exists())


if __name__ == '__main__':
    unittest.main()
