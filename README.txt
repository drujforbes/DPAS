PLEX ARTWORK STUDIO — macOS-friendly local editor

GET STARTED
1. Unzip PlexArtworkStudio.zip.
2. Open PlexArtworkStudio/index.html in Chrome, Edge, or Safari on your Mac.
3. Upload an image, or obtain a free TMDB API read-access token from themoviedb.org and use Search.
4. Choose Poster (1000 x 1500) or Background (1920 x 1080).
5. Select a production company to retrieve its TMDB logo where available, or import a transparent PNG.
6. Use awards reference links to verify award results; add WINNER and NOMINEE labels, including RAZZIE (Golden Raspberry).
7. Paint over original lettering and use Repair. This is a simple local pixel-repair tool, not AI inpainting.
8. Export PNG. Save project JSON for backup.

LIMITATIONS
- This is an offline-capable browser app, NOT a compiled macOS .app installer.
- TMDB title/production-company discovery needs an internet connection and your TMDB token.
- TMDB and Fanart.tv provide direct artwork galleries with their API credentials. TPDb, MoviePosterDB, IMDb, IMP Awards, CineMaterial and Plex remain external links; login credentials alone do not enable authorized API access.
- Awards are manually verified/entered; automatic Emmy/Oscar/SAG/Golden Globe/Razzie result lookup is not implemented.
- Original-composition button opens a public image search; it does not generate new artwork.
- Company logos are retrieved from TMDB when available; otherwise import a logo. Image provider permissions and browser cross-origin restrictions may affect imports.
- Local image repair is a basic nearest-pixel fill; large text regions can look smeared.
- Browser storage has capacity limits. Export a project JSON as a backup.
- Publicly available images may still be copyrighted; check usage rights.

AWARD DISPLAY COLORS
- OSCAR / EMMY / SAG / GOLDEN GLOBE WINNER: gold.
- RAZZIE WINNER: muted pink (#D77A9A).
- All NOMINEE labels (including RAZZIE): white.
- Award names and outcomes are uppercase and centered at the bottom. Mixed colors use separate lines.

ARTWORK DISCOVERY UPDATE
- After TMDB title selection, a gallery lists poster or backdrop alternatives from TMDB's images endpoint.
- Filter by English, textless/no language, or all returned languages; select an image to use it in the editor.
- Gallery currently displays up to 120 artworks; results are sorted by vote count then resolution.
- Additional search shortcuts: The Poster Database, MoviePosterDB, Fanart.tv, IMDb, IMP Awards, CineMaterial, TMDB, and general Plex poster search.
- External sites open separately. They are NOT integrated APIs or automatically downloaded, and may require login. Save permitted artwork locally, then use Upload.
- TMDB API access requires your own read-access token and network connectivity.
- Browser image security/CORS policies may prevent loading images from some providers; downloading and uploading is the fallback.

LOCAL REPOSITORY (NEW)
In Chrome or Edge on macOS, click "Create / choose repository folder" and select a parent folder. The application creates "Plex Artwork Studio" beneath it with Posters, Backgrounds, Logos, Source Artwork, and Projects subfolders. Use "Save PNG to repository", "Store selected logo", or "Save project to repository" to write files directly. Your browser asks permission to access the folder. Safari and browsers without the File System Access API should use the existing export/download buttons. The folder selection must be repeated after reopening the application; the app does not silently retain file-system permissions. Source Artwork is reserved for future direct source caching; selecting artwork does not yet automatically save a copy there.
