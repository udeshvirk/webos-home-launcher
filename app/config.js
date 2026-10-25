// Copy to config.local.js for local overrides; the builder uses that file.
window.HOME_CONFIG = {
    title: 'webOS Home',
    dock: ['netflix', 'amazon', 'hotstar', 'youtube.leanback.v4'],
    hiddenApps: [],
    // Optional local wide artwork, e.g. {'netflix': 'assets/banners/netflix.png'}.
    banners: {},
    idleMs: 300000,
    weather: {enabled: false, latitude: null, longitude: null, label: '', caFile: null}
};
