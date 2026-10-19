# webOS Home Launcher

A practical guide and copyable AI prompt for giving an older **LG webOS TV** a lightweight home screen: app tiles, a fixed favourites dock, local wallpapers and a photo slideshow.

![The original TV's home screen with a landscape wallpaper, fixed favourites dock and app grid](docs/screenshots/home.png)

**[View the screenshot gallery: Home, wallpaper picker and Inputs](docs/screenshots/README.md).** These are real captures of the original configured TV, whose title and weather label differ from the generic reference app. Photograph credits are included in the gallery.

Start with **[PROMPT.md](PROMPT.md)** if you want an assistant to walk you through it. Follow **[SETUP.md](docs/SETUP.md)** if you prefer the manual route.

This is a documented recipe with reference code, **not a universal rooting tool or a one-click installer**. Firmware compatibility and private Luna APIs vary by TV. The generic source was adapted from a real-device setup; its generalized package has not been installed across other TVs.

## What you get

- Plain HTML/CSS/ES5 JavaScript; no framework, blur, video background or web fonts.
- Clock/date, app tiles, a fixed five-app dock and D-pad navigation.
- Cached launch points and locally copied app icons for a fast first render.
- Local wallpapers, daily rotation and a picker that marks the current image.
- A photo slideshow, started manually or after five idle minutes by default.
- Input labels with honest empty-preview placeholders; optional single HDMI preview.
- Optional Open-Meteo weather, disabled until you supply a location.
- An overlay mode that preserved Hotstar across a Home round trip in our test.
- Recipes for root SSH, screenshot capture, injected remote keys, backups, Home mapping and undo.

## Read these first

1. This is **webOS, not Android**: no ADB, APKs or Android launchers.
2. Check your **exact firmware/OTA ID** at [CanI.RootMy.TV](https://cani.rootmy.tv/) and read the current upstream instructions. Stop if patched; do not try random firmware downgrades.
3. Disable firmware auto-updates and **never install a firmware update as part of this guide**.
4. **Never install or reinstall LG Developer Mode while rooted.** Follow the chosen rooting method's removal timing exactly.
5. Back up actual settings before changing them. Do not copy somebody else's restore values or delete LG system apps.
6. Use a trusted local network and SSH key authentication. This launcher uses Homebrew Channel's root execution service; review any code you install.

Root eligibility is a moving target. The [faultmanager README](https://github.com/throwaway96/faultmanager-autoroot) and [DejaVuln README](https://github.com/throwaway96/dejavuln-autoroot) are authoritative for their respective methods. Rooting itself carries risk and is not made universally reversible by this project's restore instructions.

## Tested setup and limits

| Item | Observation from the original setup |
| --- | --- |
| TV | LG 55UM7300PTA, 2019 model |
| webOS release | 4.10.2-29 |
| Software | 05.40.97 |
| Root | faultmanager-autoroot succeeded on that unit; not a promise for another firmware |
| Access | Root SSH; Developer Mode removed after rooting |
| Screenshots | `tv.capture/executeOneShot`, PNG, DISPLAY mode |
| Home button | `general.defaultApps.home` supported on that firmware |
| Stock Home | Kept accessible through a launcher button |
| Overlay trial | Hotstar kept the same process through Home → Hotstar via tile and green shortcut |
| Hotstar menu lag | Still noticeable; no claim that this launcher fixes the app's rendering |
| HDMI | Saved names worked; an unplugged port could still report `connected: true` |
| Live preview | Playing events observed, but visible video from a connected source still needs validation |
| Audio behind overlay | Not yet validated during programme playback |

The most important lessons are in **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**. Overlay mode is experimental: do not equate one successful process-retention test with every app remaining resident.

## Repository map

| File | Purpose |
| --- | --- |
| [PROMPT.md](PROMPT.md) | Copy, fill in the blanks, give to your coding assistant |
| [docs/SETUP.md](docs/SETUP.md) | Setup sequence, root checkpoints and verification |
| [docs/RECIPES.md](docs/RECIPES.md) | Luna commands, Home mapping, boot hook, colour buttons and restore strategy |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Real failures and how to diagnose them |
| [app/](app/) | Sanitized reference launcher; no photos or copied streaming-app assets |
| [scripts/](scripts/) | SSH wrapper, capture/keys, local build, icon-cache preparation and macOS photo push |
| [docs/SOURCES.md](docs/SOURCES.md) | Primary sources and upstream credit |

## Build the reference app

After following the root and backup checkpoints in the guide, configure a root SSH alias named `tv-root` (or set `TV_SSH_ALIAS`). Install the current [webOS CLI](https://github.com/webos-tools/cli), with `ares-package` on your PATH.

```sh
cp app/config.js app/config.local.js
# Edit config.local.js: title, dock order, idle time, optional weather location.
python3 scripts/prepare-apps.py
sh scripts/build.sh
```

`prepare-apps.py` contacts **your configured TV** to read launch points and icons. `build.sh` builds locally and does not install or remap Home. Review the installation procedure in [SETUP.md](docs/SETUP.md) before deploying the IPK.

Use the app ID `org.local.weboshome` and data root `/var/lib/webos-home` consistently. If you change either, update the source, metadata, boot/photo paths, mappings and undo records together.

The app loads local preferences ahead of config defaults. Changing `idleMs` or weather defaults in the config does not overwrite an already-saved preference: back up and deliberately update the saved value on an existing installation.

The reference Inputs layout is configured for the tested TV's three HDMI ports. Adapt it before deployment if your TV has a different port count. The photo helper currently targets the tested Homebrew app-resource installation layout; discover your actual installed app path first.

If weather HTTPS fails on an old TV, inspect its trusted CA certificates. `weather.caFile` can point to a verified CA bundle already on that TV. Do not disable TLS verification. Weather stays hidden until a fetch succeeds.

## Photos and privacy

Use your own local photos. On macOS, `push-photos.py` uses `sips` to make JPEG copies with a maximum 1920px long edge and to generate small wallpaper thumbnails. Readable HEIC/HEIF files can be converted; unreadable formats are skipped. Originals are preserved.

```sh
# Local conversion only, with no TV changes:
python3 scripts/push-photos.py /path/to/photos --target screensaver \
  --prepare-only private/prepared --report private/photo-report.json

# Copy after reviewing the prepared output and choosing the correct TV alias:
python3 scripts/push-photos.py /path/to/photos --target screensaver \
  --report private/photo-push.json
```

Do not use `--replace` until you understand it: it backs up the current photo sets and moves the selected active folders aside before replacement. The backup path is reported locally. See [RECIPES.md](docs/RECIPES.md) for undo. A separate app-resource copy is needed on the tested webOS engine; merely putting files under `/var/lib` was insufficient.

Google Photos sync is not implemented. No Google account, album sharing or scraping is required.

Never commit `private/`, SSH keys, real settings dumps, personal photos, unreviewed screenshots or generated app inventories. `.gitignore` covers the expected local paths; review staged files before pushing anyway. Only the explicitly reviewed UI captures under `docs/screenshots/` are included here.

## What this project intentionally does not automate

- Root selection or exploit execution.
- Firmware updates, factory resets, system app removal or developer-app reinstallation.
- Ad/telemetry domain blocking, changing privacy settings or disabling services without an explicit user choice.
- Google Assistant language/region changes.
- Guaranteed background residency or overclocking.

Those decisions belong to the owner of each TV. The prompt and guide include the checks and approval points.

## Validation

Run `python3 -m unittest discover -s tests -v` for offline helper checks. They use a fake SSH executable and do not contact a TV. The generic launcher passes ES5 parsing and local IPK packaging. Its roots are a real-TV setup, but this sanitized package is not represented as separately device-tested. Follow the real-device verification checklist before integration.

If your firmware is patched, you can still use LG settings for privacy, arrange stock app tiles and use local media. A Developer Mode app may be an option on an **unrooted** TV, subject to LG's limits. Root-only startup, key filters and private services are not available through this recipe without root.

**Keep firmware updates off, and never reinstall Developer Mode while rooted.**
