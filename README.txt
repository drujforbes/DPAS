DRUCIFER PLEX ARTWORK STUDIO (DPAS)
===================================
macOS Apple Silicon artwork editor for Plex posters and backgrounds.

RELEASE STATUS (November 2026)
------------------------------
The repository contains the native SwiftUI/WebKit wrapper, bundled editor,
Hellboy AppIcon.png, macOS build/DMG scripts, and automated browser/source tests.
It is NOT a completed, notarized macOS release until the GitHub macOS build
job compiles and its installation smoke test passes. There is no need to buy an
Apple Developer Program membership to make an ad-hoc signed personal test DMG.

WHERE THE DMG WILL APPEAR
-------------------------
1. Open https://github.com/drujforbes/DPAS/actions
2. Select "DPAS Apple Silicon build verification" and a successful build run.
3. Under Artifacts, download "DPAS-Apple-Silicon-unsigned-test-DMG".
4. Unzip the artifact to obtain Drucifer_Plex_Artwork_Studio_Apple_Silicon.dmg
   and its .sha256 checksum file.
5. Mount the DMG, then drag DPAS.app into Applications. The GUI heading reads
   Drucifer Plex Artwork Studio, while the installed app is DPAS.app.

An ad-hoc signed, non-notarized app may show macOS Gatekeeper warnings. For
personal testing, open it through Finder's contextual Open action where
permitted by your macOS version, or use System Settings > Privacy & Security
> Open Anyway if offered. Do not broadly disable Gatekeeper.

SOURCE AND BUILD
----------------
- index.html: complete standalone browser-mode editor; can also be opened
  directly in a browser without installing the native application.
- PASMacApp.swift: SwiftUI application and secure native WebKit bridge.
- AppIcon.png: Hellboy app icon artwork.
- build-macos.sh: compile DPAS.app for arm64 and ad-hoc sign it on macOS.
- verify-macos-app.sh: validate bundle, arm64 binary and signing.
- package-macos.sh: create a drag-to-Applications DMG and SHA-256 checksum.
- test-macos-install.sh: mount DMG and verify a copied installation.
- .github/workflows/macos-build.yml: GitHub automation.

To build locally on an Apple Silicon Mac with Apple's command-line developer
tools available, from this directory run:
  bash package-macos.sh

The workflow runs independent Ubuntu source checks and browser regression
tests. Apple Silicon compilation requires a hosted macOS runner; if the macOS
job remains QUEUED with no steps started, this is a runner provisioning issue,
not proof of a Swift compilation failure. The Linux test results can still
pass while the Mac job awaits a runner.

FUNCTIONALITY AND CAVEATS
-------------------------
- Poster and background artwork editing, local repair, cloud image-editing
  integration, preview/apply/revert, PNG export, and configurable repositories.
- TMDB and Fanart.tv integrations need internet and credentials from the user.
- OpenAI editing uses a separately billed API key stored locally in macOS
  Keychain by the native app. Do not store API credentials in this public repo.
- Awards lookup and external evidence links assist research; verifying winners
  and nominees against authoritative sources remains necessary.
- Third-party artwork and logos may be copyright-protected; check rights.
- A browser-only launch does not provide the native Keychain/DMG integration.

TESTS
-----
  python3 test-release-preflight.py
  python3 test-browser-suite.py    (requires Playwright + Chromium)

Until a macOS run succeeds, no completed installer has been verified.

LOCAL MAC BUILD IF GITHUB macOS RUNNERS DO NOT START
----------------------------------------------------
On an Apple Silicon Mac:
1. Download the repository via GitHub > Code > Download ZIP, then extract.
2. Open Terminal and change into the extracted DPAS directory:
      cd ~/Downloads/DPAS-main
   (Adjust if you extracted somewhere else.)
3. Run:
      bash build-on-my-mac.sh
   The script checks for Apple's command-line developer tools, runs source
   preflight checks when Python 3 and Node.js are present, builds DPAS.app,
   packages a drag-to-Applications DMG and verifies its copied installation.
   It does NOT require an Apple Developer account or any API keys.
4. The DMG and SHA-256 file will be in the repository directory.
If command-line developer tools are missing, run:
      xcode-select --install
Then repeat step 3. Apple SDK compilation still requires macOS; a Linux
or Windows runner cannot build a native SwiftUI/WebKit application.
