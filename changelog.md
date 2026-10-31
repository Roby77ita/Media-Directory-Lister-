# Changelog

All notable changes to **Media Directory Lister** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the versioning
is progressive (`major.minor`), with an incremental number for each substantial change.

## [Unreleased]

_Nothing pending._

---

## [5.24] — 2026-10-31

### Fixed
- The subtitle in the main window ("v5.24 · Report with metadata") no longer wraps onto a second
  line. The window minimum width in vertical layout has been increased to 780px to accommodate
  the title, subtitle, and action buttons on a single line.

### Changed
- Restored the original subtitle text (removed the forced line break).

---

## [5.23] — 2026-10-31

### Changed
- Shortened the subtitle text (from "HTML report with metadata" to "Report with metadata") to
  reduce the chance of line wrapping in the window header.

---

## [5.22] — 2026-10-31

### Fixed
- Fixed a crash (`AttributeError: 'App' object has no attribute 'pie'`) introduced in the 5.21
  update check. The update notification is now correctly created inside `costruisci()` and
  persists across window redraws (language or layout changes).

---

## [5.21] — 2026-10-31

### Added
- Automatic update check: on startup, the program queries the GitHub Releases API to see if a
  newer version is available. If yes, a discreet clickable link appears at the bottom of the
  window: "⬆ Version 5.21 is available! Click here to download it." The check runs silently
  in the background and is ignored if there is no internet connection or the repository has
  no releases yet.

---

## [5.20] — 2026-10-31

### Fixed
- Added a fallback to calculate the video bitrate when ffprobe does not provide it directly.
  The value is now estimated by subtracting the total audio bitrate from the overall file
  bitrate (total - audio). This fixes empty video bitrate columns for files where the
  container does not store the video track bitrate.

### Changed
- Cache format bumped to version 2 to force a re-scan of all files and populate the new
  bitrate values.

---

## [5.19] — 2026-10-31

### Added
- **Help button** next to the search bar in the HTML report (the `?` button). Clicking it opens
  a modal window listing all advanced search operators with examples (`ext:`, `size:`, `year:`,
  `res:`, `hdr:`, `durata:`).

---

## [5.18] — 2026-10-31

### Fixed
- Advanced search in the HTML report now works correctly. Two bugs were fixed:
  - A double backslash (`\\s+` instead of `\s+`) prevented the query from being split into tokens.
  - The `input` event handler was not calling `parseAvanzato()`, so advanced operators were
    ignored.

---

## [5.17] — 2026-10-31

### Fixed
- Made the `checkAdv` function much more robust for size filters. It now accepts spaces
  (`10 GB`), case variations (`10gb`), and both decimal separators (`10,5` or `10.5`).

---

## [5.16] — 2026-10-31

### Fixed
- Fixed the empty table issue on report open (introduced in 5.15). The search parsing now handles
  an empty query correctly and does not hide all files.
- Added a safety check in `checkAdv` to return `true` if the advanced filter object is empty.

---

## [5.15] — 2026-10-31

### Added
- **Advanced search** in the HTML report: the search bar now supports operators to filter
  results precisely:
  - `ext:` (e.g. `ext:mkv`, `ext:flac,mp3`) — filter by file extension
  - `size:` (e.g. `size:>10GB`, `size:<500MB`) — filter by file size
  - `year:` (e.g. `year:2020`, `year:>2015`) — filter by tag year
  - `res:` (e.g. `res:4k`, `res:1080`) — filter by video resolution
  - `hdr:` (e.g. `hdr:sì`, `hdr:no`) — filter by HDR presence
  - `durata:` (e.g. `durata:>60`) — filter by duration in minutes
  Operators can be combined with plain text (e.g. `Dragon res:4k`).

---

## [5.14] — 2026-10-31

### Changed
- The "Copy path" option in the report HTML now copies the full absolute file path (e.g.
  `C:\Users\Name\Desktop\Folder\CD1\file.flac`), making it much easier to paste directly
  into File Explorer or a terminal. The base folder path is embedded once into the HTML with
  zero impact on performance or report size.

---

## [5.13] — 2026-10-31

### Fixed
- Fixed an issue where "Copy path" in the report HTML would copy only the file name if the
  "Group by subfolder" option was disabled. The relative path is now always calculated and
  included in the report data.

---

## [5.12] — 2026-10-31

### Added
- **Context menu** in the HTML report: right-click on a file name to copy the file name or
  the full path directly to the clipboard. The context menu also shows a small confirmation
  ("Copied!") for a few seconds.

---

## [5.11] — 2026-10-31

### Fixed
- The program no longer prompts "unsaved changes" on close if the user has not actually
  modified anything. The `modifiche_non_salvate` flag is now set only by real user actions
  (column changes, "All"/"None" buttons, etc.) and not by automatic interface redraws.

---

## [5.10] — 2026-10-31

### Fixed
- Fixed a crash (`KeyError: 'sistema'`) when the "System theme" was selected. The logo
  loading in `costruisci()` now correctly uses `self.tema_effettivo` instead of `self.tema`.

---

## [5.9] — 2026-10-31

### Added
- **System theme**: a new "System theme" option in the Settings menu that follows the Windows
  light/dark mode setting.
- **Default columns button**: in the "Report columns" section, a new "Default" button restores
  the default columns for the active profile type (General, Music or Movie).

---

## [5.8] — 2026-10-31

### Fixed
- Fixed a crash (`KeyError: 'profilo_generale_nome'`) that occurred when opening the profile menu
  after the 5.7 update. The missing translation keys have been correctly added for both Italian
  and English.

---

## [5.7] — 2026-10-31

### Added
- The default "Generale" profile is now displayed as "General" when the interface language is
  set to English. The underlying profile name in `config.json` remains unchanged for compatibility.

---

## [5.6] — 2026-10-31

### Fixed
- Saving a profile from the "Edit profile" or "Exclusions" dialogs now also commits any pending
  column selections, so the "unsaved changes" prompt no longer appears unnecessarily when
  closing the program afterwards.

---

## [5.5] — 2026-10-31

### Changed
- The program now prompts for confirmation before closing if there are unsaved changes
  (including column selections). "Yes" saves, "No" discards, "Cancel" keeps the program open.
- Background silent saves have been removed: modifications are only written to `config.json`
  when the user confirms on exit, or when generating a report (which inherently uses the
  current settings).
- Column selections and the "All"/"None" buttons mark the profile as modified, so the
  confirmation dialog appears when needed.

---

## [5.4] — 2026-10-31

### Fixed
- Profile column selections and options are now saved automatically when closing the program,
  even if no other action (like generating a report or switching profile) was performed.
- Added a one-time informational dialog for users upgrading from older versions, explaining
  that "Include images" is now a session-only option and no longer saved in the profile.

### Changed
- Removed the unused `includi_immagini` field from new profiles.
- Removed the unused `profilo_etichetta` ("Profile:") translation key.

---

## [5.3] — 2026-10-31

### Changed
- The active profile name in the profile combobox is now displayed in **bold**.
- The source folder combobox now uses the same larger font (Segoe UI 12) both when closed and
  when open, improving readability.

---

## [5.2] — 2026-10-31

### Changed
- The profile combo box no longer repeats the word "Profile:" — it shows only the profile name,
  since the section header already says "PROFILE".

---

## [5.1] — 2026-10-31

### Changed
- Versioning scheme updated from `5.0zN` to `5.1`. The program version and filename are now
  aligned. This is a structural change only; no functional differences from `5.0z13`.

---

## [5.0z13] and earlier

Earlier versions are documented in the project's historical repository. Main features from
previous versions include: profiles with separate exclusions and columns, SQLite scan cache,
light/dark/color themes, vertical and horizontal layouts, HTML report with filters and summary,
Italian/English languages.