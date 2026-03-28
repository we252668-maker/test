# Windows EXE Packaging Guide

This project currently uses `PyQt6`, so the packaging examples below are based on `PyQt6` and `PyInstaller`.

## 1. Install dependencies

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
```

## 2. Quick build command

Use this when you want to package directly from the command line without the `.spec` file:

```powershell
pyinstaller --noconfirm --clean --windowed --name BrainForge --add-data "data;data" --collect-all PyQt6 main.py
```

Notes:

- `--windowed` prevents the console window from appearing.
- `--add-data "data;data"` bundles the project `data` folder into the executable package.
- `--collect-all PyQt6` helps include Qt plugins and related package data.

## 3. Recommended build command

Use the included spec file for repeatable builds:

```powershell
pyinstaller --noconfirm --clean BrainForge.spec
```

Output:

- One-folder build: `dist\BrainForge\BrainForge.exe`

## 4. Resource path handling

The project now separates:

- `APP_DIR`: writable location
  - Source mode: project root
  - EXE mode: folder containing `BrainForge.exe`
- `BUNDLE_DIR`: bundled resource location
  - Source mode: project root
  - EXE mode: PyInstaller temporary extraction folder

Rules:

- Writable files such as the SQLite database should go under `APP_DIR\data`
- Bundled read-only resources should be resolved from `BUNDLE_DIR`

Use `utils.paths.resource_path(...)` for images, icons, and JSON files when you add or update resource loading code later.

Example:

```python
from utils.paths import resource_path

icon_path = resource_path("assets", "app.ico")
```

## 5. Database behavior after packaging

When the EXE runs:

- The app writes the runtime database to `data\engineer_hub.db` next to the EXE
- If a bundled `data\engineer_hub.db` exists and no runtime database exists yet, it is copied out automatically on first launch
- The schema initialization still runs as before

This keeps the database writable in packaged mode and avoids trying to write into PyInstaller's temporary bundle directory.

## 6. PyQt plugin handling

If Qt platform plugins are missing, the app may fail with messages such as:

- `Could not find the Qt platform plugin "windows"`
- `This application failed to start because no Qt platform plugin could be initialized`

Current mitigation:

- The provided `BrainForge.spec` uses `collect_data_files("PyQt6")`
- The provided `BrainForge.spec` uses `collect_submodules("PyQt6")`
- The quick command uses `--collect-all PyQt6`

If you still hit plugin issues, rebuild with:

```powershell
pyinstaller --noconfirm --clean --windowed --name BrainForge --add-data "data;data" --collect-all PyQt6 --hidden-import PyQt6.sip main.py
```

## 7. Common errors and fixes

### Error: GUI starts in source mode but not in EXE mode

Cause:

- Resource paths are still based on relative paths or `__file__` only

Fix:

- Resolve packaged resources with `resource_path(...)`
- Keep writable output under `APP_DIR`

### Error: Database is read-only or cannot be created

Cause:

- The app is trying to write inside `_MEIPASS` or a protected folder

Fix:

- Store the runtime database next to the EXE in `data\`
- Avoid reading and writing the same DB file inside the bundled temp directory

### Error: Console window appears

Cause:

- Built without GUI mode

Fix:

- Use `--windowed`
- Or set `console=False` in the spec file

### Error: Missing icons, images, or JSON files

Cause:

- Files were not added to the bundle

Fix:

- Add them with `--add-data`
- Or append them to `datas` in `BrainForge.spec`

Example:

```python
datas.append((str(project_dir / "assets"), "assets"))
```

### Error: Anti-virus or Windows SmartScreen flags the EXE

Cause:

- Unsigned newly built executables can trigger warnings

Fix:

- Test locally first
- Package in one-folder mode during development
- Code-sign the EXE for distribution if needed

## 8. If you later switch to PyQt5

This project is currently `PyQt6`, not `PyQt5`.

If you intentionally migrate to `PyQt5`, update:

- `requirements.txt`
- source imports
- PyInstaller command from `PyQt6` to `PyQt5`
- spec hooks from `collect_data_files("PyQt6")` to `collect_data_files("PyQt5")`
