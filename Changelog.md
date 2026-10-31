# Changelog

All notable changes to **Media Directory Lister** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the versioning
is progressive (`5.0zN`), with an incremental number for each substantial change.

## [Unreleased]

_Nothing pending._

---
## [5.0z13] — 2026-10-31   →   ## [5.1] — 2026-10-31
## [5.0z13] — 2026-10-31

### Changed
- One-time `config.json` cleanup: on first launch of this version, obsolete or unused fields are
  removed (`includi_immagini` from profiles, `migrazione_3_9g`, `migrazione_3_9t`,
  `cartella_scansione`, `colonne`). The configuration file stays cleaner and consistent with
  the current behavior.

---

## [5.0z12] — 2026-10-31

### Fixed
- Removed the duplicated "folder" block in the **New profile** dialog (two "Use current folder"
  checkboxes, two folder fields, two "Browse..." buttons).
- Removed the duplicated `nuovo_usa_corrente` key in Italian and English text files.
- Removed dead code in `_cambia_lingua_menu`.
- Fixed the `VERSIONE` constant (it was still `5.0z4` despite the file name).

### Changed
- `includi_immagini` is no longer written to `config.json` by `avvia()`.
- `_versione_cache()` now includes `ESTENSIONI_IMMAGINE`: if image behavior changes, the scan cache
  is invalidated automatically.

---

## [5.0z11] — 2026-10-31

### Added
- Bitrate formatting in the HTML report for video and audio:
  - below **10,000 kbps** → `kbps` with thousand separator (e.g. `9,122 kbps` in English,
    `9.122 kbps` in Italian);
  - above **10,000 kbps** → `Mb/s` with two decimals (e.g. `16.50 Mb/s`).
- `SOGLIA_MBPS` constant to easily change the threshold.

---

## [5.0z10] — 2026-10-31

### Changed
- **"Include images"** is now a **session option**: it applies to the current scan only and is no
  longer remembered in the profile. On next launch it starts unchecked.
- The flag no longer modifies the profile's `estensioni_escluse`: image inclusion is handled at
  scan time via `_esclusioni_attive`, without touching the saved configuration.

---

## [5.0z9] — 2026-10-31

### Changed
- Checkbox label renamed from **"Includi le immagini nel report"** to **"Includi immagini"**
  (Italian) and from **"Include images in the report"** to **"Include images"** (English).

---

## [5.0z8] — 2026-10-31

### Changed
- **Profile** menu order: **New profile...** first, then **Edit profile...**, then **Delete profile**.

---

## [5.0z7] — 2026-10-31

### Added
- In the **New profile** dialog you can now choose the new profile's folder:
  - **"Use current folder"** checkbox (checked by default if a folder is already selected);
  - folder field + **"Browse..."** button to pick a different one.
- The main folder field is no longer cleared when creating a profile: it shows the folder chosen
  for the new profile.

---

## [5.0z6] — 2026-10-31

### Added
- **"Open configuration folder"** entry in the **Settings** menu: opens File Explorer (or the file
  manager) on `%APPDATA%\MediaDirLister\` where `config.json`, cache and logs live.

### Fixed
- `VERSIONE` constant aligned with the file name (`5.0z6`), which was lagging behind.

---

## [5.0z5] — 2026-10-31

### Fixed
- All image extensions are now excluded by default: added `gif`, `bmp`, `tif`, `tiff`, `webp`,
  `svg`, `heic`, `ico`, `raw`, `cr2`, `nef`, `arw`, `psd` to `ESTENSIONI_ESCLUSE`.
  Previously only `jpg`, `jpeg`, `png`, `avif` were excluded, while the others still appeared in
  the report.
- Updated `includi_immagini_nota` (Italian and English) to reflect the new behavior: without the
  option all images are excluded, with the option all are included.

---

## [5.0z4] and earlier

Earlier versions are documented in the project's historical repository. Main features from
previous versions include: profiles with separate exclusions and columns, SQLite scan cache,
light/dark/color themes, vertical and horizontal layouts, HTML report with filters and summary,
Italian/English languages.

---

## Legend

- **Added** — new features.
- **Changed** — changes in existing functionality.
- **Deprecated** — features that will be removed in future.
- **Removed** — removed features.
- **Fixed** — bug fixes.
- **Security** — vulnerability fixes.

---

## Updating

1. Download the new `media_directory_lister_v5.0zN.py`.
2. Replace the previous file (you can keep a copy of the old one).
3. **Do not delete** `config.json`: it is read and updated automatically. The first launch of a new
   version creates a backup `config.json.bak_<previous version>`.
4. If you use FFmpeg, keep `ffprobe` in the program folder or in `PATH`.

---

## Reporting issues

- Email: roby77dopa@gmail.com
- GitHub: https://github.com/Roby77ita/Media-Directory-Lister
