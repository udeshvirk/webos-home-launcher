# Copyable prompt: help me modernize my LG webOS TV

Fill in the bracketed fields. Share this with an assistant that can browse primary sources, edit files locally and reach your TV over the local network. Keep passwords, pairing codes and keys out of public chats and repositories.

```text
Help me set up a lightweight home screen on my own LG webOS TV. Work on the real
device step by step, with screenshots and injected remote presses. Use this
repository as a reference, not as proof that my firmware is compatible.

TV model: [exact model]
webOS release: [full value from Settings]
Software/firmware: [full value]
OTA ID, if known: [value or unknown]
Already rooted: [yes/no/unsure]
Computer OS: [macOS/Linux/Windows]
TV root SSH alias/IP: [local value; don't publish it]
Launcher title: [name]
Dock apps, in order: [4–5 apps]
Weather: [no, or yes plus city / coordinates / Celsius or Fahrenheit]
Slideshow idle time: [minutes]
Wallpaper folder on my computer: [local path or none]
Slideshow photo folder: [local path or none]
Daily wallpaper rotation: [yes/no]
Colour shortcuts: [none, or red/green/yellow/blue → app]
Shortcut scope: [launcher only / throughout TV]
Main apps to test: [list]

Ground rules:
- This is webOS, not Android. No ADB or APKs.
- Never update the firmware or downgrade it. Confirm automatic updates are off.
- Never install/reinstall LG Developer Mode after the TV is rooted.
- Never delete LG system apps or edit locale files by hand.
- Back up every setting before changing it. Generate a restore action using
  the actual old value before applying each change. Preserve other keys in maps.
- Ask checklist questions before preference changes or actions that cannot be
  undone. Explain any memory, audio, privacy or app-availability tradeoff.
- Keep secrets, photos, screenshots, private settings and app inventories in an
  ignored local private folder. Never publish them.
- Make one change at a time and verify it on the TV. Do not claim a generic API
  works just because it exists in webOS OSE documentation.

1. Establish compatibility before touching the TV.
   Check CanI.RootMy.TV with my exact identifiers and read the current
   faultmanager-autoroot and dejavuln-autoroot READMEs on GitHub. Report the
   applicable method or patched status, linking sources. If patched, stop root
   work and explain unrooted options. Do not extrapolate from the example model.
   Explain the method and get my OK before rooting.

2. Root only using the chosen upstream procedure, unmodified.
   Use the current official download/release form that README specifies; do not
   invent a release archive if the method distributes a script. Explain which
   steps I must do on the TV and wait for me. Use USB only if that method needs
   it. Handle Developer Mode removal and Quick Start+ exactly as instructed.
   Confirm Homebrew Channel Root status "ok", enable SSH, set up key auth, verify
   persistence and confirm Developer Mode is gone. Restore my original Quick
   Start+ setting if the rooting procedure required a temporary change.

3. Back up locally before customization.
   Save listApps, listLaunchPoints, relevant getSystemSettings categories,
   locale/language, defaultApps.home, original keyFilters if relevant, startup
   hooks, hosts, running app IDs/PIDs and memory. Check every returnValue; record
   unsupported categories instead of treating empty/error JSON as a backup.
   Draft restore scripts, with no hardcoded assumptions about original values.

4. Build and install a small plain HTML/CSS/ES5 launcher.
   Use a cached app list and local icon copies, refresh in the background, and
   keep the favourites dock separate from the scrollable All Apps grid.
   Include clock/date, Inputs, Settings, stock LG Home and a slideshow button.
   Deterministic D-pad rows, last app focus, one moving highlight. No blur,
   shadows, runtime web fonts, video wallpaper or always-running polling service.
   Use root-backed applicationManager only where needed. Review the privilege
   boundary: the reference app uses Homebrew Channel's root exec service.
   Install through the supported Homebrew/root path; never reinstall Developer
   Mode to make an installation tool work on a rooted TV.

5. Wallpapers and local slideshow.
   Resize copies to at most 1920px long edge; preserve originals; skip files that
   cannot be decoded. Back up existing TV photo folders before a replacement.
   Keep persistent photos separately, and copy only required images into this
   app's resource folder if the old web engine cannot read /var/lib paths.
   Use thumbnails in the picker, focus/mark the current wallpaper, and consume
   all repeated OK keydowns until the long press opening the picker is released.
   Daily wallpaper rotation, one decoded background at a time. Slideshow uses
   only two image elements for a slow cross-fade; clear the old image after the
   fade. A normal key returns Home. Explain exceptions for TV-wide colour keys.

6. Optional weather and input improvements.
   Weather only if approved: Open-Meteo, no key, fetch when Home becomes visible
   and its cache is over 30 minutes old. Hide until the first successful fetch.
   Read TV-supported input metadata for HDMI labels. Saved names do not prove a
   device is plugged in. Do not trust eim.connected as cable status: it was true
   on empty ports in the original test. Show an honest fallback when no preview
   is available. Try at most one muted HDMI preview on focus, with a small delay;
   release it on focus change, modal close or app hiding. Test using a real
   connected source before calling live previews verified.

7. Home integration and app residency.
   Inspect general.defaultApps.home and the actual native Home key filter. If
   supported, preserve the whole prior map and set our app as Home. Keep stock
   Home reachable. Add a short-lived Homebrew startup hook with bounded retries.
   Compare app PIDs through stock Home and custom Home. A normal full-screen
   launcher caused Hotstar to exit in the original test; an overlay preserved
   it. Treat overlay as an explicit trial, not a universal fix. Check D-pad
   focus, tile launches, colour launches, Settings, stock Home, audio behind Home,
   slideshow behavior and fallback. Dismiss our overlay on app launch. Do not
   force every streaming app into memory or change global memory policy blindly.

8. Optional privacy and shortcuts: ask first.
   Show LivePlus/viewing collection, home promotions, recommendations and ad
   settings found on this firmware. Disable only approved settings, using actual
   original values in undo payloads. Show proposed domain blocks first and test
   my apps afterward. Avoid blindly disabling background system services.
   Ask whether I want a homebrew YouTube app; don't replace YouTube by default.
   For TV-wide colour keys, inspect the native key-filter chain, add only our
   filter file, preserve LG's entries and generate undo first. Consume releases
   and repeats. Make the overlay dismiss when a shortcut opens another app.
   Do not promise this Qt filter approach works on every webOS generation.

9. Measure and be honest.
   Separate menu/remote lag from buffering. Sample current CPU and swap activity,
   not just lifetime ps CPU or "free" RAM. Compare matched states and distinguish
   service acknowledgement from a usable painted UI. Do not promise root fixes
   a third-party streaming app's own rendering. Do not clear app data/reinstall
   an app or interrupt playback without explaining and getting approval.

10. Deliver a local README, build/install instructions, photo-push script, restore
    scripts and screenshots of Home, picker, slideshow and Inputs. List verified
    behavior, untested features and remaining limits. Undo customizations must
    not remove root/SSH or restore firmware unless separately requested.
    Finish with reminders: no firmware updates; no Developer Mode reinstallation
    while rooted. Leave language, region and voice features unchanged unless I
    explicitly request changes and they are supported on this exact TV.
```

Before executing anything, the assistant should summarize the proposed work, compatibility evidence and preference questions. It must not turn this prompt into a blind batch script.
