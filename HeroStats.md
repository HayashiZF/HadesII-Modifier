# Hero Initial Stats Guide

This guide explains how to adjust the hero's initial status (starting Health, Mana, and Money) and how each `Actions` button maps to the underlying code.

## 1) Where initial hero status is defined

### Health and Mana at run start

- Base values are in `Content/Scripts/HeroData.lua`:
  - `MaxHealth = 30`
  - `MaxMana = 50`
- Run-start assignment is in `Content/Scripts/RunLogic.lua`:
  - `newHero.Health = newHero.MaxHealth`
  - `newHero.Mana = newHero.MaxMana`

What this means:

- Starting Health always equals current `MaxHealth`.
- Starting Mana always equals current `MaxMana`.
- To change starting Health/Mana for new runs, change `MaxHealth` / `MaxMana` in `HeroData.lua`.

### Starting Money at run start

- Money is granted in `Content/Scripts/RunLogic.lua`:
  - `AddResource( "Money", CalculateStartingMoney(), "RunStart" )`
- The amount comes from:
  - `function CalculateStartingMoney()`
  - default return: `GetTotalHeroTraitValue( "BonusMoney" )`

What this means:

- Starting money is trait-driven by default.
- If you want a fixed amount, replace the function body with a constant return, for example:
  - `return 100`

## 2) Recommended edit points

Use these exact files/functions:

- `Content/Scripts/HeroData.lua`
  - Edit `MaxHealth`
  - Edit `MaxMana`
- `Content/Scripts/RunLogic.lua`
  - `CreateNewHero(...)` for Health/Mana initialization behavior
  - `CalculateStartingMoney()` for starting money logic
  - `AddResource( "Money", CalculateStartingMoney(), "RunStart" )` call site

## 3) Actions panel -> code mapping

UI button definitions (order and labels):

- `src/hades_mod_ui/app.py`
  - `1. Backup Originals` -> `_on_backup`
  - `2. Generate Copies` -> `_on_generate`
  - `3. Apply Replacement` -> `_on_apply`
  - `4. Restore Backups` -> `_on_restore`

Detailed flow:

1. `1. Backup Originals`
   - `app.py:_on_backup()`
   - Calls `self.service.get_target_files(profile, profile_state)`
   - Calls `self.service.backup_originals(targets, self.state)`
   - Writes backups to:
     - `.hades2_mod/originals/Content/Scripts/*.lua`
   - Updates state:
     - `.hades2_mod/state.json` (`known_backups`)

2. `2. Generate Copies`
   - `app.py:_on_generate()`
   - Calls `self.service.generate_copies(profile, profile_state, self.state)`
   - Reads originals from:
     - `Content/Scripts/*.lua`
   - Applies transform generators in `operations.py` / `patches.py`
   - Writes generated files to:
     - `.hades2_mod/generated/Content/Scripts/*.lua`
   - Updates state:
     - `.hades2_mod/state.json` (`generated_files`)

3. `3. Apply Replacement`
   - `app.py:_on_apply()`
   - Internally does generate first:
     - `generate_copies(...)`
   - Then applies:
     - `apply_generated_files(generated, state, profile)`
   - `apply_generated_files` also enforces backup-first:
     - calls `backup_originals(...)` before replacing
   - Replaces destination files in:
     - `Content/Scripts/*.lua`
   - Updates state:
     - `.hades2_mod/state.json` (`last_apply`)

4. `4. Restore Backups`
   - `app.py:_on_restore()`
   - Calls `self.service.restore_all_backups(self.state)`
   - Restores all files recorded in `known_backups` from:
     - `.hades2_mod/originals/Content/Scripts/*.lua`
   - Back to:
     - `Content/Scripts/*.lua`
   - Updates state:
     - `.hades2_mod/state.json` (`last_restore`)

## 4) Practical workflow for hero initial stats

1. Edit `Content/Scripts/HeroData.lua` and/or `Content/Scripts/RunLogic.lua` using the edit points above.
2. Keep a safe backup before broad edits.
3. If you are using the desktop tool for patchable profiles, use the Actions in order:
   - `1. Backup Originals`
   - `2. Generate Copies`
   - `3. Apply Replacement`
   - `4. Restore Backups` (only if rollback is needed)

Note:

- Current desktop tabs focus on rarity/boon/weapon/reward/keepsake profiles.
- Hero initial stats are currently controlled directly in Lua script files shown above.
