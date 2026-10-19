# Device-specific recipes

All commands below assume root SSH is already verified. They do not root a TV. Inspect supported methods with `ls-monitor -i SERVICE` instead of guessing write endpoints.

`scripts/luna.py` shell-quotes payloads, requests a PTY (needed for reliable Luna stdout on the tested firmware), prints parsed JSON and exits nonzero for `returnValue: false`. It supports `@path/to/payload.json`. It is a generic caller: a write URI really changes the TV. Use read calls and backups first.

## Private inventory

```sh
umask 077
mkdir -p private/before
chmod 700 private private/before
python3 scripts/luna.py luna://com.webos.applicationManager/listApps '{}' > private/before/apps.json
python3 scripts/luna.py luna://com.webos.applicationManager/listLaunchPoints '{}' > private/before/launchpoints.json
python3 scripts/luna.py luna://com.webos.applicationManager/running '{}' > private/before/running.json
python3 scripts/luna.py luna://com.webos.settingsservice/getSystemSettings \
  '{"category":"general"}' > private/before/general.json
python3 scripts/luna.py luna://com.webos.settingsservice/getSystemSettings \
  '{"category":"option"}' > private/before/option.json
python3 scripts/luna.py luna://com.webos.settingsservice/getSystemSettings \
  '{"keys":["localeInfo"]}' > private/before/locale.json
sh scripts/tv-ssh 'cat /etc/hosts' > private/before/hosts
sh scripts/tv-ssh 'free -k; ps -eo pid,ppid,rss,pcpu,comm' > private/before/memory-processes.txt
sh scripts/tv-ssh 'ls -la /var/lib/webosbrew/init.d' > private/before/startup-hooks.txt
```

Read the actual language/region categories your firmware uses and back those up too if you intend to touch them. Failed reads need investigation; do not apply subsequent changes using an empty file as the original state.

## Screenshot and key injection

The tested capture endpoint was:

```text
luna://com.webos.service.tv.capture/executeOneShot
{"path":"/tmp/webos-home-capture.png","method":"DISPLAY","format":"PNG"}
```

Its reported dimensions were zero even though the file was a valid 1920×1080 PNG. Validate the file signature, open the image, and check what it shows. A successful API reply does not prove a meaningful image. Capture only when the owner expects it, and keep screenshots private.

```sh
sh scripts/capture.sh home
sh scripts/key.sh RIGHT
sh scripts/key.sh OK
```

`key.sh` uses `networkinput/test/sendKeyCode` with **`keyCode`**, not `keycode`. Linux codes used on the tested unit: arrows 103/108/105/106, OK 28, Back 412, Home 125, colours 398–401. DOM colour keycodes are a different numbering scheme. Availability is firmware-dependent.

Wait for painting before a final screenshot. For startup timing, distinguish an acknowledged launch, foreground registration, and a visibly usable home screen. A software restart is not a cold-power-on benchmark.

## Home button: preserve the full old map

Read first:

```sh
python3 scripts/luna.py luna://com.webos.settingsservice/getSystemSettings \
  '{"category":"general","keys":["defaultApps"]}' > private/before/default-apps.json
```

If supported, generate both write and undo payloads **locally**:

```sh
python3 - <<'PY'
import json,pathlib
p=pathlib.Path('private')
r=json.loads((p/'before/default-apps.json').read_text())
assert r.get('returnValue') is True
old=r['settings']['defaultApps']
assert isinstance(old,dict) and 'home' in old, 'Unsupported/absent Home setting: investigate first'
new=dict(old);new['home']='org.local.weboshome'
for name,value in [('home-enable',new),('home-restore',old)]:
    (p/(name+'.json')).write_text(json.dumps({'category':'general','settings':{'defaultApps':value}},indent=2))
PY
```

After owner approval:

```sh
python3 scripts/luna.py luna://com.webos.settingsservice/setSystemSettings @private/home-enable.json
```

Undo:

```sh
python3 scripts/luna.py luna://com.webos.settingsservice/setSystemSettings @private/home-restore.json
```

Verify Home with injected and physical remote presses. Do not directly replace LG's Home files. If this setting is absent, inspect native behavior and use manual/boot launch as a fallback until a compatible approach is verified.

## Startup hook

Homebrew startup hooks live under `/var/lib/webosbrew/init.d/` on the tested setup. Use a unique filename without a dot, such as `80-webos-home`; BusyBox run-parts can ignore names containing dots. Check for collisions before writing anything.

Have that hook start a short-lived Node helper from `/var/lib/webos-home/`, with stdout/stderr going to a temporary log. The helper should:

1. Re-create missing `photo-library/` resource copies if a package update removed them.
2. Delay until the app manager is ready (the original test used 12 seconds).
3. Launch `org.local.weboshome` using `execFile('/usr/bin/luna-send', args, ...)`.
4. Retry only on failure, with a finite limit, then exit.

Do not install an endless launcher watchdog: it could interrupt whatever the owner is watching. Back up any existing same-name file and permissions. Undo by restoring that file or removing **only your own** hook if it was originally absent. Do not remove Homebrew's root startup infrastructure.

## TV-wide colours: optional Qt filter

Inspect the TV's own `/usr/lib/qt5/qml/KeyFilters/` and the current list:

```sh
python3 scripts/luna.py luna://com.webos.service.config/getConfigs \
  '{"configNames":["com.webos.surfacemanager.keyFilters"]}' > private/before/keyfilters.json
```

The sample [colour-keys.js](../scripts/colour-keys.js) maps red→YouTube, green→Hotstar, yellow→Apple TV and blue→LG Photo & Video. It consumes repeats/releases and closes only our overlay before launching. Get the owner's desired mapping and scope first.

For a compatible Qt firmware, create these private payloads:

```sh
python3 - <<'PY'
import json,pathlib
p=pathlib.Path('private');r=json.loads((p/'before/keyfilters.json').read_text())
assert r.get('returnValue') is True
key='com.webos.surfacemanager.keyFilters';old=r['configs'][key]
assert isinstance(old,list) and old, 'No supported Qt chain found'
entry={'file':'/var/lib/webos-home/colour-keys.js','handler':'handleCommunityColours'}
assert not any(x.get('file')==entry['file'] for x in old), 'Existing custom filter: preserve and investigate'
(p/'keys-enable.json').write_text(json.dumps({'configs':{key:[entry]+old}},indent=2))
(p/'keys-restore.json').write_text(json.dumps({'configs':{key:old}},indent=2))
PY
```

Inspect the generated payload and filter. Copy the filter to the declared TV path, checking for an existing file first. Apply `config/setConfigs` only after the restore payload exists. Keep every LG entry intact. To undo, apply `keys-restore.json`, verify the chain and then remove only your filter.

A changed source file may not reload when the config value is unchanged. On the tested implementation, switching to the saved original chain and then back reloaded it. Chain reload also reruns native initializers, so do it only when necessary. Newer webOS generations may not use these Qt filters at all. See the [upstream compositor notes](https://github.com/rorygallagher2024/glasshouse/blob/main/docs/IMPLEMENTATION.md#remote-keys-through-the-compositors-filter-chain).

## Optional privacy settings

Never make a universal "disable everything" payload from another person's TV. Read the relevant category, select the approved keys, save their exact old values/types, then generate matching enable/restore JSON. Do not rewrite unrelated settings from an old full-category dump.

Examples discovered on the original unit: viewing-information collection, ad-cookie consent, recommendations and home effects. Some features were already disabled. Home promotions, personal recommendations and LivePlus may have different names or live only in the UI on another firmware.

Domain blocking is separate from toggles. If requested, back up hosts/resolver state and review the proposed maintained list. Allow-list or roll back if the owner's apps break. Neither a root shell nor this repository automatically removes ads from streaming services.

## Photos: backup and undo

The photo helper saves a tar archive of the old persistent sets and reports `backupOnTv` in the optional local JSON report. A replace import also preserves moved-aside original folders. These paths and names belong in the local change journal.

To undo a particular import:

1. Identify the exact backup and the target set that import changed.
2. Back up the current active target again, so later photos are not lost.
3. Extract the selected target into a staging directory and inspect its contents.
4. Move the current selected target aside and move the staged old target into place.
5. Rebuild only that target's app-resource copy and reopen Home.

Do not blindly restore both sets if only the screensaver should change: the archive contains wallpapers too, which may have been updated since. Do not delete original computer-side photos or restore somebody else's archive.

## Performance and app-retention check

```sh
python3 scripts/luna.py luna://com.webos.applicationManager/running '{}' > private/before-switch.json
# Open Home, wait for painting, then read running again.
python3 scripts/luna.py luna://com.webos.applicationManager/running '{}' > private/at-home.json
# Return using the app tile/shortcut, then read running again.
python3 scripts/luna.py luna://com.webos.applicationManager/running '{}' > private/after-switch.json
```

Compare IDs and PIDs. The old process disappearing and a new PID appearing is stronger evidence of a full restart than seeing a splash animation. A retained process still does not guarantee unchanged page state or instant network responses.

`sample-tv-performance.js` can be copied to a temporary TV file and run under the TV's Node. It reads a five-second CPU/memory/swap sample and exits. It does not change governors, priorities or memory policy. Existing swap usage alone is not proof of current thrashing. Match the app screen/activity before drawing a before/after conclusion.

If restarting a streaming app, get approval for interrupting playback. On the tested firmware, `applicationManager/closeByAppId` accepted `{"id":"hotstar"}`; the generic `close` endpoint did not accept that app-ID form. Verify absence before relaunching. This does not clear login data.

## Restore order

Your restore script must use your private backups, not example defaults:

1. Restore the original Home map; verify stock Home can open.
2. Restore the original key-filter chain; verify keys before removing your filter.
3. Restore approved privacy settings from their saved key values.
4. Restore hosts/DNS only if you actually changed them.
5. Restore or remove only your startup hook.
6. Uninstall the custom app through the supported Homebrew path, after Home no longer points to it.
7. Optionally restore selected photo sets; keep backups and root SSH.

Do not use a factory reset as a shortcut. Undoing customization is distinct from unrooting and cannot reverse a firmware update. A partial rollback should preserve unrelated later changes.

**No firmware updates; no Developer Mode reinstallation while rooted.**
