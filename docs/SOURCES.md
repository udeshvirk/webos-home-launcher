# Sources and credit

The exploit authors and Homebrew maintainers did the underlying platform work. This repository documents an end-user customization and publishes only its own sanitized launcher/helpers, not LG system files or vendored exploit code.

- [CanI.RootMy.TV](https://cani.rootmy.tv/): exact firmware compatibility check.
- [faultmanager-autoroot](https://github.com/throwaway96/faultmanager-autoroot): authoritative applicability, instructions, removal timing and upstream script. Licensed by its authors; not bundled here.
- [dejavuln-autoroot](https://github.com/throwaway96/dejavuln-autoroot): authoritative applicability and USB release procedure. Licensed by its authors; not bundled here.
- [webOS Homebrew Channel](https://github.com/webosbrew/webos-homebrew-channel): root tooling, installer and startup infrastructure. Not bundled here.
- [webOS Homebrew Luna service bus guide](https://www.webosbrew.org/pages/luna-service-bus.html): service inspection and root/private API context.
- [webOS Homebrew appinfo notes](https://www.webosbrew.org/pages/appinfojson): undocumented overlay metadata and caveats.
- [webOS Homebrew web-app guide](https://www.webosbrew.org/develop/guides/web-app/): external-input embedding; hardware-dependent limitations.
- [LG App Lifecycle Management](https://webostv.developer.lge.com/develop/guides/app-lifecycle-management): foreground, background and relaunch behavior.
- [LG appinfo reference](https://webostv.developer.lge.com/develop/references/appinfo-json): application metadata.
- [webOS CLI](https://github.com/webos-tools/cli): packaging tools; consult its current installation instructions.
- [Glasshouse implementation notes](https://github.com/rorygallagher2024/glasshouse/blob/main/docs/IMPLEMENTATION.md#remote-keys-through-the-compositors-filter-chain): native compositor filter-chain mechanism. We used the documented mechanism and inspected the real TV's own files; Glasshouse server code is not bundled.
- [Open-Meteo forecast API](https://open-meteo.com/en/docs): optional weather. Attribution is required if you enable it; see below.

Links were checked while preparing this guide. Upstream instructions and firmware patch status can change. Consult them again at setup time; the working model/firmware example is a historical observation, not an eligibility database.

## Assets and weather attribution

The repository contains reviewed UI screenshots in [the gallery](screenshots/README.md), with [photograph attribution](screenshots/ATTRIBUTION.txt). No family photos, account/profile screens or standalone landscape-photo collection are included. Third-party app logos visible in UI captures remain their owners' marks; no separate streaming-app icon assets are bundled. The local build helper copies icons from each user's own TV into an ignored directory.

Use your own photos, or obtain appropriate permission and retain each asset's attribution/license locally. Do not assume Wikimedia Commons is one blanket license for all images.

The supplied small launcher icon was created for this project. When enabling weather, retain the visible Open-Meteo attribution provided by the reference app and review the service's current terms and [CC BY 4.0 data attribution](https://open-meteo.com/en/terms).

## Classic layout and local fonts

The classic layout takes visual inspiration from [Sony BRAVIA Launcher](https://github.com/udeshvirk/sony-bravia-launcher) and [Lumen](https://github.com/samrenfrew/lumen-webos). Lumen is not installed or bundled. The reference remains a plain HTML/CSS/ES5 app.

Outfit is bundled under the SIL Open Font License in [app/assets/fonts/Outfit-OFL.txt](../app/assets/fonts/Outfit-OFL.txt). The static TrueType instances were generated from the Sony launcher's OFL-licensed Outfit source with HarfBuzz `hb-subset --keep-everything --variations=wght=140` (and 300/400). They are named under the Outfit family; retain the included license when redistributing.
