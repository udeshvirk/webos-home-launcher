# Troubleshooting and lessons from the real TV

These observations came from one webOS 4.x unit. Verify behavior on yours.

## Root eligibility is not a model-year guess

An older TV is not automatically rootable. Consult the exact identifiers in CanI.RootMy.TV and the applicable upstream README. Newer patched firmware cannot be made compatible by substituting the other exploit's commands. Never update or downgrade firmware as an experiment.

The original setup did not need USB because its applicable method used Developer Mode SSH. That does not remove USB from a different method's requirements. Developer Mode is a pre-root route in that procedure, not an app to reinstall after root.

## Home is blank immediately after installation

Check these separately:

- Did the launcher finish painting, or did you capture its splash screen?
- Did the root bridge return a real launch-point list?
- Is there a cached local seed and are icon resources readable?
- Does the configured wallpaper actually decode from inside the app's resource folder?
- Did the installer replace the app folder and remove its photo-resource copies?

The source starts with a cached list when generated locally. Without it, the first list waits for the root API response. `prepare-apps.py` generates a private seed/icons bundle for the local build; never publish it.

## Wallpapers disappear after holding Settings

We found a real input bug: long OK opened the picker, then repeated OK keydowns selected its first option, Dark background. A screenshot of a dark Home alone initially hid the cause.

The handler now ignores Enter repeats while the original hold is active; keyup releases the guard. The picker also focuses the current image and marks it Currently selected. Test with repeat events that **lack** an `e.repeat` property, because old engines may not report it reliably.

Inspect the saved `preferences` value before assuming files disappeared. If it says `wallpaper: dark, rotate: false`, back up that exact preference and deliberately restore the owner's desired selection. Do not silently clear all localStorage: it also contains app focus and weather/cache preferences.

## Photos exist on disk, but show black

The tested old engine could not directly read private `/var/lib` image paths. We kept persistent photos there but copied the selected image folders into the installed app's own `photo-library/`. The app uses relative URLs into those copies.

After a package update, copy the photo resources back before checking images. Validate dimensions and successful decoding, not just a file listing. Convert a readable HEIC/HEIF to JPEG locally; skip it if decoding fails. The original HEIC/HEIF samples converted successfully, but that is not a guarantee for every image variant or computer codec.

## Favourite app tiles are clipped when browsing lower rows

The dock originally shared the scroll container with All Apps. Focusing the last app scrolled the dock partly off-screen. It now sits in a separate fixed section, and focus scrolling applies only to the other-app rows. Verify the entire rectangle of every dock tile is within the visible region while the last app is selected.

## Home disappears after about two idle minutes

The original TV later dismissed the overlay after approximately 120 seconds without remote input. A successful launch reply did not prove the overlay remained visible. The owner returned to normal card mode; Home then stayed visible and the five-minute slideshow worked. Do not modify the compositor idle settings to solve this by default. Card mode can reload streaming apps, as observed earlier.

## Text looks soft or card labels overlap icons

The classic layout uses static Outfit TrueType instances at weights 140, 300 and 400, avoiding a variable-font CSS declaration on the older browser. Clock, title and first app share the same left edge. Text shadows are omitted. App cards contain artwork only; the selected name appears above the rows. Keep native icon proportions, and use wide local artwork rather than stretching a small square icon to fill a banner.

## All empty HDMI ports say Connected

Do not label ports from `eim/getAllInputStatus`'s `connected` field alone. On the tested unit it returned true on all three unplugged HDMI ports while `hdmiPlugIn` was false.

Saved labels such as a console or set-top-box name are preferences, not evidence of an active device. The reference marks customized labels as Saved device name. For absent/unknown preview availability it shows an explicit placeholder, with OK still available to switch.

The reference attempts a focused preview only for an explicit positive `hdmiPlugIn` flag. Positive detection still needs a controlled real plug/unplug test on your firmware. Do not reinterpret missing/unknown data as proven disconnection, and do not call a black rectangle a verified live preview.

## HDMI preview says Playing but the image is black

Metadata/canplay/playing events were observed even when no useful source picture appeared in the capture. They do not prove a live HDMI image. Check with a powered connected device, actual on-TV viewing and a capture method that can capture the relevant video plane. Protected content can complicate captures.

Keep one preview at most. Release it on focus change, leaving Inputs or app hiding. With the current empty inputs the reference allocates zero video elements. No HDMI decoder runs behind ordinary Home.

## Every return to an app feels like a cold launch

Measure PIDs. Our full-screen card launcher caused Hotstar's process to disappear when Home opened. Stock LG Home kept that same Hotstar process. This showed that the custom Home path contributed to reloads even though our code never called an app killer.

The user-approved overlay trial preserved the Hotstar PID through opening Home and returning through either the Hotstar tile or the green shortcut. It also required explicit dismissal: otherwise the overlay remained visible over the resumed app. Successful tile launch now closes our window; the colour filter closes only our overlay before launching its target.

This is not a guarantee that all streaming apps stay cached. Overlay mode can leave playback/audio active underneath it. Check that during a real programme before considering the behavior finished. The original completed tests were at the profile chooser; audio during playback remained unverified.

## Hotstar menus are still sluggish

The original TV had roughly 1 GiB visible RAM. A short sample while Hotstar was active showed around 239 MiB available and about 12% aggregate CPU, with negligible swap activity; that sample did not capture a specific menu-lag event. Menu lag persisted, so neither that sample nor root established a system bottleneck we could safely fix.

The overlay addressed a demonstrated reload issue; it did not establish faster Hotstar menu rendering. Keep those outcomes distinct. Ask whether the complaint is menu navigation, playback buffering or both before changing network settings.

Avoid drop-caches loops, blanket service disabling, overclocking or forcing every streaming app resident. A larger free-RAM number can mean you have simply evicted the apps the owner wanted to resume quickly. Keep original preload policy unless a measured and approved change helps.

## Luna command succeeds but stdout is empty

On the tested firmware, root SSH without a TTY sometimes produced no Luna JSON. Use `scripts/luna.py`/the `--tty` wrapper for those calls, and validate the reply. The app's root bridge uses a short-lived Node `execFile` wrapper to capture `luna-send` stdout reliably.

Do not use a TTY when copying binary PNG/JPEG bytes back to the computer: use the wrapper's non-TTY mode. Otherwise line-ending conversion can corrupt files.

## A colour shortcut opens an app but Home stays over it

That was an overlay dismissal bug, not proof the app failed to launch. Inspect both foreground app and the actual TV screenshot. The root filter should close only the custom Home overlay before launching. Tile launch should close its own window only after successful launch acknowledgement.

Changing a filter file may not reload an unchanged config list. Preserve the original chain, reload deliberately and verify the effective file/handler entries. Do not modify LG's filter files to get around caching.

## Google Photos or Assistant expectations

This implementation uses local photos, not a live Google Photos album. Do not invent an OAuth/scaping workaround or upload personal images to make a slideshow work.

Voice-assistant availability and language support are model-, region- and time-dependent. Nothing in the reference source enables Google Assistant. Check current official support and the actual TV menus; leave language/region unchanged unless the owner approves a supported change. A menu-language option is not proof an assistant accepts that speech locale.

## Reporting an issue

Include model, firmware, webOS release, app source version, window type, observed behavior and a redacted error or PID comparison. Do not attach whole settings dumps, keys, private photos, account-bearing URLs, Wi-Fi credentials or a conversation transcript containing pairing codes. Review screenshots for personal profiles and content before posting them.
