// Local TV-wide shortcuts. LG's filter files remain unchanged.
// Launch once on press; consume repeats and release for these four keys.
function handleCommunityColours(key, pressed, autoRepeat) {
    var id = '';
    if (key === WebOS.Key_webOS_Red) id = 'youtube.leanback.v4';
    else if (key === WebOS.Key_webOS_Green) id = 'hotstar';
    else if (key === WebOS.Key_webOS_Yellow) id = 'com.apple.appletv';
    else if (key === WebOS.Key_webOS_Blue) id = 'com.webos.app.photovideo';
    else return KeyPolicy.NextPolicy;
    if (pressed && !autoRepeat) {
        // Dismiss only our overlay; leave LG's other overlays to their policies.
        if (overlayView.appId === 'org.local.weboshome') overlayView.close();
        applicationManager.launch(id, '{}');
    }
    return KeyPolicy.Accepted;
}
