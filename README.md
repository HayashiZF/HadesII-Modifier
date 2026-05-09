# Hades II Mod UI

A comprehensive desktop application to safely create and manage mods for Hades II. This tool generates patched Lua scripts locally, allowing you to fine-tune game mechanics without permanently breaking the base game.

## Overview

The `HadesIIModUI` uses deterministic Lua text transforms to insert patches into the `Content/Scripts` folder. The application always ensures backups are made before applying changes and maintains state in a local `.hades2_mod` workspace.

## Getting Started

### Building the Tool
If you haven't already, you can compile the Python tool into a standalone Windows executable by running:
```powershell
.\build_exe.ps1
```
*(Wait for the build to finish. The executable will be created at `dist/HadesIIModUI.exe`.)*

### Running the Tool
Double-click `dist/HadesIIModUI.exe` to launch the application.

## How to Use the Mod UI

The user interface is split into **Tabs (Modes)** for configuration, and an **Actions** panel for execution. 

### 1. Configure Patches
Select a tab at the top to switch between different modding modes. In each mode, you can toggle `Enable patch` to activate specific modifications:

- **Rarity Editor**: Adjust the spawn chances for Normal Gods, Hermes, Chaos, Artemis, and more. You can change the probabilities for Rare, Epic, Duo, and Legendary boons, as well as customize the roll order.
- **Boon Multipliers**: Fine-tune the stat multipliers (damage, speed, etc.) provided by specific boons from each god. Advanced fields are hidden by default but can be revealed for deeper customization.
- **Weapon Damage**: Add flat base-damage bonuses to entire weapon families.
- **Reward Amounts**: Edit the global post-combat room-clear payout values (e.g., Money, Health, Mana).
- **Keepsake**: Configure the per-keepsake buffs applied in `TraitData_Keepsake.lua`.

### 2. The Modding Workflow
Once your patches are configured, use the **Actions** buttons in the following order:

1. **Generate Copies**: Click this first. It reads your current configurations and creates preview copies of the patched Lua files in the `.hades2_mod/generated/` folder. *This does not affect your live game yet.* You can verify the targeted files in the "Target Files" list.
2. **Backup Originals**: Safely creates backups of the original, unmodded Lua scripts in the `.hades2_mod/originals/` folder. Always do this before applying your first patch!
3. **Apply Replacement**: Copies the generated patched files over to your live `Content/Scripts/` folder. Your game is now modded!

### 3. Restoring the Game
If you want to revert your changes and return to the vanilla game:
- **Restore Backups**: Replaces the modded files in `Content/Scripts/` with the original files safely kept in `.hades2_mod/originals/`.

## Developer Notes

- The tool stores your UI settings and application state locally in `.hades2_mod/state.json`.
- Advanced Lua script modding guides and rules can be found in `AGENTS.md` and `CLAUDE.md`.
