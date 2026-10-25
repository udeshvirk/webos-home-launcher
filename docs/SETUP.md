# Setup guide

Use [PROMPT.md](../PROMPT.md) for an assisted setup. These steps are checkpoints, not a script to run unattended.

## 1. Identify the TV and root eligibility

Write down the full model, software version and webOS release from Settings. Obtain the OTA ID if the compatibility checker needs it. Marketing year, firmware number, SDK version and webOS release are different values.

Check [CanI.RootMy.TV](https://cani.rootmy.tv/). Then read both the [faultmanager-autoroot README](https://github.com/throwaway96/faultmanager-autoroot) and [DejaVuln README](https://github.com/throwaway96/dejavuln-autoroot). Use the applicable method's current instructions and official download form. Never run both just to see what sticks.

The original unit used faultmanager through Developer Mode SSH, without a USB drive. DejaVuln's published procedure uses USB. **The no-USB path is conditional on compatibility, not a general workaround.**

If patched, stop. Do not update or downgrade firmware hoping to make it rootable. Stock app arrangement, privacy settings and local media remain possible; root-only hooks do not.

## 2. Root with the owner's approval

Confirm automatic firmware updates are off. Explain the applicable method and get approval before running it. Follow upstream unmodified, including on-TV steps and the timing of removing Developer Mode. Do not replace upstream instructions with this guide's summary.

Afterward verify Homebrew Channel Root status **ok**, enable its SSH server and set up a dedicated key. Keep keys on the computer. Confirm root SSH and root persistence after the method's required restart. Confirm Developer Mode is removed. If Quick Start+ was temporarily changed by the procedure, return it to the agreed original value after rooting.

**Do not install Developer Mode on an already-rooted TV. Do not install a firmware update.**

## 3. Configure root SSH

Example computer-side `~/.ssh/config` entry; replace placeholders locally:

```sshconfig
Host tv-root
    HostName TV_LAN_ADDRESS
    User root
    Port 22
    IdentityFile ~/.ssh/YOUR_DEDICATED_TV_KEY
    IdentitiesOnly yes
```

Inspect the TV's host key before trusting it. Never disable host-key checking just to suppress an error. Use a local trusted network; do not expose this root SSH server to the Internet.

```sh
sh scripts/tv-ssh 'id'
```

Expected after rooting: `uid=0`. Developer Mode's pre-root user/port is not this root SSH connection. Set `TV_SSH_ALIAS` if you chose a different alias.

## 4. Inventory and save undo data

Create a local ignored `private/` folder with mode 700. Save the results of:

- `applicationManager/listApps`, `listLaunchPoints`, `running` and foreground app.
- `settingsservice/getSystemSettings` for every category you plan to change, including general/option and the actual locale/language settings used by the TV.
- The entire existing `general.defaultApps` map, not only the Home string.
- `config/getConfigs` for `com.webos.surfacemanager.keyFilters` if remapping keys.
- `/etc/hosts`, existing Homebrew startup-hook names, memory and process measurements.

See the exact calls in [RECIPES.md](RECIPES.md). Save raw replies privately and check `returnValue`. Unsupported categories are expected on some models; an error is not a successful backup.

For each future mutation, prepare its inverse from the values you just saved. Record the change, timestamp, original file/payload and restore command in a local change journal. Full settings dumps can contain account or network information: never post them to issues or upload them here.

## 5. Customize and build the reference app

Install the current [webOS CLI](https://github.com/webos-tools/cli) on your computer. The reference code uses ES5 so it can run on the older engine; the computer's Node version need not match the TV's Node 0.12.

```sh
cp app/config.js app/config.local.js
# Edit title, dock IDs, idleMs and optional weather configuration.
python3 scripts/prepare-apps.py
sh scripts/build.sh
```

Discover IDs from your TV instead of assuming every region has the example apps. The reference dock has four entries; replacing IDs keeps the layout intact. `prepare-apps.py` caches launch points and icon copies privately, excluding deep-link params. It does not publish streaming-app icons. Generated assets enter only your ignored local build.

The package is `dist/org.local.weboshome_0.2.0_all.ipk` initially. Keep your versioned source and IPK locally for rollback. Increase the app version on updates; an older package may not be accepted as a downgrade.

The default manifest uses normal **card** mode. The original TV's overlay trial preserved Hotstar's process, but later dismissed Home after roughly two idle minutes; normal card mode stayed visible and reached the five-minute slideshow. Card mode may reload streaming apps. Treat an overlay as a separate, explicit experiment on your firmware; compare PIDs and actual screen visibility.

## 6. Install through Homebrew's root path

Do not make root installation work by reinstalling Developer Mode. The original setup used Homebrew Channel's private installer, which accepts a URL and SHA-256. This is not an assertion that a custom app is listed in the official Homebrew repository.

One reproducible pattern is:

1. Verify the Homebrew installer endpoint exists on your TV.
2. Save any previous installation's source/package and photo/local-state backup before updating.
3. Copy the built IPK to `/tmp/webos-home.ipk` over root SSH.
4. Run a temporary HTTP server **on the TV**, bound only to `127.0.0.1`, serving only that IPK with `Content-Length`.
5. Call `org.webosbrew.hbchannel.service/install` with the app ID, local URL, computed `ipkHash` and subscription enabled.
6. Wait for `finished: true` and `returnValue: true`, then stop the temporary server.

Example installer payload shape:

```json
{
  "id": "org.local.weboshome",
  "ipkUrl": "http://127.0.0.1:18765/home.ipk",
  "ipkHash": "REPLACE_WITH_ACTUAL_SHA256",
  "subscribe": true
}
```

The server is a deployment aid, never a permanent network service. Do not send this example with the placeholder hash. The [Homebrew source](https://github.com/webosbrew/webos-homebrew-channel) is the authority for its installer interface.

The root execution bridge is intentionally powerful. The reference does not ship a separately elevated custom service: Homebrew handles root commands. Use only your reviewed local app/configuration, with no remotely injected HTML or arbitrary command inputs.

## 7. Add local photos

First prepare locally and inspect the output:

```sh
python3 scripts/push-photos.py /path/to/wallpapers --target wallpapers \
  --prepare-only private/prepared-wallpapers
python3 scripts/push-photos.py /path/to/family-photos --target screensaver \
  --prepare-only private/prepared-slideshow
```

This helper requires macOS `sips`. On another OS, use a reviewed local ImageMagick/Pillow equivalent that preserves originals, skips unreadable files and limits the output size. Never upload photos to a conversion service without the owner's consent.

Then run the same commands without `--prepare-only`, adding `--report private/photo-push.json` to record the backup location. Do one target at a time. Use `--replace` only when replacement is wanted; otherwise files merge.

The helper backs up current wallpaper/screensaver folders on the TV before importing. Data goes to `/var/lib/webos-home/{wallpapers,screensaver}`. App-readable copies go under the installed app's `photo-library/`. Re-create those copies after every package update: the installer may replace the app resource directory.

Open Home again to refresh the lists. Verify full-size images, thumbnails, conversion of any HEIC/HEIF files, slideshow fade and normal-key exit. Do not just count files and call them decoded.

## 8. Verify before making it Home

```sh
sh scripts/key.sh HOME
sh scripts/capture.sh baseline
```

On a new setup HOME still opens LG Home until you explicitly configure the default. Launch the custom app manually through `applicationManager/launch`, then test:

- Four dock tiles, Down into the four-column grid, lower-row scrolling, Up back to Home and remote focus.
- Settings short press; long OK opens the picker but cannot select while held.
- Current wallpaper marker, daily rotation and slideshow preview from the picker.
- Each actual streaming app, preserving the owner's profile/login.
- Inputs: saved names, empty fallback, preview release and real connected video if available.
- No photo/weather timers doing work when Home is hidden.
- Home remains visible beyond two idle minutes and the slideshow starts after five minutes; check app return/reload behavior.

Take screenshots after the UI has painted. Launch acknowledgement is not launch time to usable UI.

## 9. Integrate Home and optional colour keys

Inspect native support, preserve original values and use the recipes. Do not assume your model uses the same Home setting or Qt key-filter chain. Test Home from a streaming app, confirm stock Home is reachable, and test after a real restart if the owner approves one.

For colours ask for scope first: launcher-only versus TV-wide. TV-wide mappings override app-specific colour actions. Keep the four mappings optional. A startup hook should be short-lived, bounded and removable; it should not relaunch Home over playback periodically.

## 10. Optional privacy and performance work

List supported ad/recommendation/viewing-information settings first and ask which to change. Settings that existed on the original TV included `option.watchedListCollection`, `general.adCookie`, `general.aiNudge`, `general.homeEffect`; other features were already off. These names are discovery hints, not a universal disable script.

Domain blocking was **not enabled** in the original setup. If requested, show a maintained proposed list, back up hosts/DNS changes, generate undo and test the owner's apps. Do not call that task completed simply because privacy switches are off.

Measure RAM/CPU/swap and app retention in matched states. Do not turn off core AV services or pin every streaming app just to make a free-RAM number look better. Hotstar menu lag persisted even with healthy short-sample CPU/memory values and improved Home retention. Keep that limitation explicit.

Leave voice, language and region settings alone unless requested. Availability changes over time and differs by model: verify current official support before promising Google Assistant. Do not edit locale files by hand.

## 11. Finish and undo

Deliver the local change journal, original payloads, source, build/deploy instructions and a restore script. Restore must undo custom Home mapping and keys **before** removing the launcher, then remove only your startup hook and optionally restore backed-up photo sets. Keep root SSH unless the owner specifically wants it removed.

Review [RECIPES.md](RECIPES.md#restore-order) for the order and [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for known limits.

**Never install a firmware update, and never reinstall LG Developer Mode while rooted.**
