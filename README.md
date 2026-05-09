# Hades II Modding Base

This repository serves as a modding base and script dump for Hades II. It contains the game's Lua script files for exploration and mod creation, as well as a Python-based desktop application for managing, patching, and applying mods.

## Repository Structure

- `Content/`: Extracted files from Hades II, primarily containing the `Scripts` directory which acts as the reference and modding base.
- `src/`: Source code for the Hades II Mod UI, a Python desktop application for building and managing mods.
- `build_exe.ps1`: Build script to compile the Python desktop application into a standalone executable.
- `*.md` files: Various documentation and guides on game mechanics, boons, rewards, multipliers, and modding heuristics.

## Desktop Mod Tool (`HadesIIModUI`)

The repository includes a Windows desktop helper application (`src/main.py`) designed to safely manage Lua script patching and replacement.

### Features
- Uses deterministic Lua text transforms and anchors to generate patched script files.
- Operates primarily on the local `Content/Scripts` folder as the effective Hades parent folder.
- Creates patched copies first, allowing you to preview changes before applying them.
- Features backup and restoration functionality to safely rollback modifications.

### Building
You can package the tool into a standalone Windows executable by running:
```powershell
.\build_exe.ps1
```
The compiled tool will be output to `dist/HadesIIModUI.exe`.

### Runtime Workspace
When run, the application creates a `.hades2_mod/` directory to manage its state and file operations:
- `.hades2_mod/generated/`: Contains the generated patched copies of the Lua scripts.
- `.hades2_mod/originals/`: Contains original backups of any modified files.
- `.hades2_mod/state.json`: Maintains application state and configuration.

## Modding Resources

For deep dives into the game's logic and specific guides on modding traits, enemies, and UI, refer to:
- `AGENTS.md`
- `CLAUDE.md`
- Various `.md` resources (`BOON_RARITY.md`, `Rarity.md`, `keepsake.md`, etc.) which map out specific game systems.
