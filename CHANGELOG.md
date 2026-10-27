# Changelog

## 2.0.0 — 2026-10-27

KivyMD 2.0 migration, from the 1.x demo shipped in the initial commit.

- Migrated to KivyMD 2.0.0 with Kivy 2.3.1, both pinned in `pyproject.toml`.
- Rebuilt the interface on the 2.0 composition APIs: `MDTopAppBar` with
  leading/trailing button containers and a title, `MDTextField` with
  `MDTextFieldHintText`/`MDTextFieldHelperText` children, `MDButton` with
  `MDButtonText`, `MDListItem` with headline/supporting text, and
  `MDNavigationDrawer` inside `MDNavigationLayout` with a
  `MDNavigationDrawerMenu`.
- Fixed the original toolbar (an `MDTooltip` carrying `left_action_items`),
  the drawer (previously a plain `BoxLayout` child), and the list (now
  inside a scroll view).
- Added validation: usernames and emails are stripped, checked, and
  unique case-insensitively; invalid fields show the field error state
  and a status message.
- Added delete: tap a row to select a user, then Delete selected.
- Hardened storage: the database now lives in the app's user-data
  directory instead of wherever the program was launched from, the
  connection closes on exit, and `UserDB` is a context manager.
- Added packaging (`pyproject.toml`, `user-management` console script),
  headless tests for the model and database, an opt-in GUI smoke test,
  lint/type gates, GitHub Actions CI, MIT LICENSE, and this changelog.
- Normalised line endings to LF.

## 1.0.0 — 2026-07-19

Initial KivyMD user-management demo: a form, a SQLite-backed list, and a
navigation drawer. Unversioned at the time; recorded here as the baseline
the 2.0.0 migration started from.
