from pathlib import Path
p=Path(__file__).parent
s=(p/'package-macos.sh').read_text()
v=(p/'verify-macos-app.sh').read_text()
checks={
 'drag-to-Applications shortcut':'ln -s /Applications' in s,
 'notarization with configured keychain profile':'notarytool submit' in s and '--keychain-profile' in s,
 'stapling and validation':'stapler staple' in s and 'stapler validate' in s,
 'signing required before notarization':'Notarization requires PAS_SIGN_IDENTITY' in s,
 'publish only after notarization':'mv -f "$TMP_DMG" "$OUT"' in s and s.index('stapler validate') < s.index('mv -f "$TMP_DMG" "$OUT"'),
 'app binary verification':'codesign --verify --deep --strict' in v and 'grep -q arm64' in v,
 'full GUI name preserved':"grep -q 'Drucifer Plex Artwork Studio'" in v,
 'DPAS display name preserved':"grep -qx DPAS" in v,
}
for k,ok in checks.items():print(('PASS' if ok else 'FAIL')+': '+k)
assert all(checks.values())
