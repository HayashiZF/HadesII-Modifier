# AGENTS.md

This file provides repository-specific guidance for coding agents working in this folder.

## Repository nature

This directory is primarily a Hades II script dump / modding base, and now also includes a Python desktop mod tool.

Working assumptions:

- Lua script editing still has no game-local package manifest, build system, linter, or test runner.
- Most work here is script/data editing intended to be loaded by the game or mod loader elsewhere.
- Validation is primarily static: import/load paths, inheritance chains, trait/property consumers, hook references, and save-state interactions.
- A local Python UI project exists under `src/` and can be packaged into `dist/HadesIIModUI.exe`.

Because of that:

- Do not invent Lua build/test/lint commands unless you actually find them.
- Prefer targeted data edits over broad shared-logic rewrites.
- Treat Lua gameplay code as an event-driven game-script source tree.
- For the desktop tool, follow the existing Python module boundaries instead of mixing UI, patch, and file ops logic.

## Desktop mod tool context

The repository now contains a Windows desktop helper executable workflow:

- Source root: `src/`
- UI entry point: `src/main.py`
- App package: `src/hades_mod_ui/`
- Build script: `build_exe.ps1`
- Build output: `dist/HadesIIModUI.exe`
- Runtime workspace: `.hades2_mod/`
- Runtime files:
  - generated copies: `.hades2_mod/generated/Content/Scripts/*.lua`
  - original backups: `.hades2_mod/originals/Content/Scripts/*.lua`
- app state: `.hades2_mod/state.json`

Current Python structure (post split, compatibility-first):

- Compatibility facades (stable imports):
  - `src/hades_mod_ui/app.py` -> re-exports `HadesModUI`, `run_app`
  - `src/hades_mod_ui/operations.py` -> re-exports `ModService`, `OperationError`
  - `src/hades_mod_ui/state.py` -> re-exports state constants/defaults/store
  - `src/hades_mod_ui/patches.py` -> re-exports patch functions/constants
- Main implementations:
  - `src/hades_mod_ui/ui/main_window.py`: primary Tk UI class implementation
  - `src/hades_mod_ui/operations_support/mod_service.py`: patch orchestration, validation, file workflow
  - `src/hades_mod_ui/state/`: state defaults/catalogs/store split
  - `src/hades_mod_ui/patches/`: validators/lua-ops/profile patching split
- Transitional legacy snapshots:
  - `src/hades_mod_ui/state_legacy.py`
  - `src/hades_mod_ui/patches_legacy.py`
- Test suite:
  - `tests/` (pytest-based lightweight regression and workflow coverage)

Important behavior constraints for this tool:

- The app targets `./Content/Scripts` under repo root as the effective Hades parent folder.
- The app should generate patched copies first, then apply copy/replace only when requested.
- Preserve backup-first behavior before replacement and full known-backup restore behavior.
- Keep Epic preset insertion idempotent and marker-based.

## First places to look

- `RunData.lua`: master import/data assembly.
- `RoomLogic.lua`: room bootstrap, map lifecycle, runtime state setup.
- `RunLogic.lua`: current run and persistent game-state initialization.
- `SaveLogic.lua`: save filtering / persistence rules.
- `PatchLogic.lua`: migrations and compatibility patches.
- `CombatLogic.lua`: central combat processing and combat hooks.
- `PowersLogic.lua`: boon / trait / weapon synergy logic.
- `EffectData.lua` and `EffectLogic.lua`: status effect definitions and runtime handling.
- `EncounterData*.lua` and `EncounterLogic.lua`: encounter composition and scripted spawns.
- `EnemyData*.lua` and `EnemyAILogic.lua`: enemy archetypes and AI behavior.
- `UILogic.lua`, `HUDData.lua`, `UIData.lua`, `*ScreenData.lua`: UI and HUD flow.
- `Debug.lua`: useful engine-facing hooks and debug helpers.
- `src/hades_mod_ui/ui/main_window.py`: desktop UI layout and interaction handlers.
- `src/hades_mod_ui/operations_support/mod_service.py`: backup/apply/restore and generation service.
- `src/hades_mod_ui/patches/profiles.py`: deterministic Lua text transforms and anchors.
- `src/hades_mod_ui/patches/validators.py`: user-input numeric/range validation for patch payloads.
- `src/hades_mod_ui/patches/lua_ops.py`: low-level Lua text replacement/search helpers.
- `src/hades_mod_ui/state/store.py`: JSON state persistence and deep-merge behavior.
- `src/hades_mod_ui/paths.py`: root/workspace path resolution and workspace naming.

## Common navigation commands

### Repository inspection

- `Get-ChildItem *.lua`
- `Get-ChildItem src/hades_mod_ui -Recurse -File`
- `rg '^Import "' RunData.lua RoomLogic.lua UtilityLogic.lua`
- `rg 'InheritFrom|DeepInheritance' *.lua`
- `rg 'CurrentRun|GameState|MapState|SessionMapState' *.lua`
- `rg 'CallFunctionName\\(|GetHeroTraitValues\\(' *.lua`
- `rg 'OnKeyPressed\\{|OnAnyLoad|OnPreThingCreation' *.lua`

### Desktop tool inspection

- UI callbacks and tab builders:
  `rg '^    def _build_|^    def _on_|^    def _collect_' src/hades_mod_ui/ui/main_window.py`
- Operation validation and generators:
  `rg '^    def _validate_|^    def _build_|^    def generate_|^    def apply_|^    def backup_|^    def restore_' src/hades_mod_ui/operations_support/mod_service.py`
- Patch entry points:
  `rg '^def apply_|^def replace_|^def find_|^def validate_' src/hades_mod_ui/patches/profiles.py src/hades_mod_ui/patches/lua_ops.py src/hades_mod_ui/patches/validators.py`
- State constants/defaults/store boundaries:
  `rg '^DEFAULT_|^class StateStore|^BOON_|^REWARD_|^KEEPSAKE_' src/hades_mod_ui/state/*.py`

### Common modding searches

- Find a trait and its consumers:
  `rg 'TraitNameHere' TraitData*.lua LootData*.lua PowersLogic.lua CombatLogic.lua EffectLogic.lua ManaLogic.lua RoomLogic.lua`

- Find a trait property key consumer:
  `rg 'GetHeroTraitValues\\("PropertyKeyHere"|HeroTraitValuesCache\\.PropertyKeyHere' *.lua`

- Find an enemy and related logic:
  `rg 'EnemyNameHere' EnemyData*.lua EncounterData*.lua EncounterLogic.lua CombatLogic.lua`

- Find an encounter and its room logic:
  `rg 'EncounterNameHere' EncounterData*.lua EncounterLogic.lua RoomData*.lua`

- Find an effect definition and application path:
  `rg 'EffectNameHere' EffectData.lua EffectLogic.lua CombatLogic.lua PowersLogic.lua WeaponData.lua ProjectileData.lua`

- Find string-based callback references before renaming:
  `rg 'FunctionNameHere|OnApplyFunctionName|OnDamagedFunctionName|OnClearFunctionName|ProjectileBlockFunctionName|OnDeathFunctionName' *.lua`

## High-level architecture

### 1. Bootstrapping is split between imports and runtime initialization

- `RunData.lua` seeds large global data tables like `RoomData`, `TraitData`, `EnemyData`, `LootData`, `ScreenData`, then imports many `*Data.lua` modules.
- `RoomLogic.lua` initializes live runtime state when a map loads, including `GameStateInit()`, `RunStateInit()`, `SessionMapStateInit()`, `MapStateInit()`, and `DoPatches()`.

If you need to know where something comes from:

- start in `RunData.lua` for static definitions
- start in `RoomLogic.lua` for when that data becomes active

### 2. The codebase is heavily data-driven

Typical pattern:

- `SomethingData.lua` defines large tables
- `SomethingLogic.lua` consumes or mutates them
- `SomethingPresentation.lua` handles visuals, audio, or UI presentation

Examples:

- `EnemyData*.lua`: enemy/NPC/unit templates
- `EncounterData*.lua`: encounters and special encounter variants
- `TraitData*.lua`: boons, aspects, weapons, keepsakes, meta-upgrades
- `EffectData.lua`: status/effect records

For most modding tasks, prefer editing the table that drives the behavior rather than rewriting shared runtime logic.

### 3. Runtime state lives in several important global tables

- `GameState`: persistent progression/save data across runs
- `CurrentRun`: active run state
- `MapState`: live room/map state
- `SessionMapState`: transient per-room/per-combat caches
- `SessionState`: broader runtime caches not tied to one room

Before changing behavior, decide whether the feature should persist:

- across saves
- across the current run
- only for the current room/combat

### 4. Units are usually cloned from templates, then customized

Common pattern:

1. `DeepCopyTable(...)` from `EnemyData` or related data
2. optional overwrite/merge via helpers like `OverwriteSelf(...)`
3. `SpawnUnit(...)`
4. `SetupUnit(...)`

When tuning a spawn, check:

- the base template
- any variant overwrite data
- spawn point selection
- post-spawn setup

### 5. Inheritance and merging matter

This repo relies heavily on:

- `InheritFrom = { ... }`
- `DeepInheritance = true`
- `DeepCopyTable`
- `MergeTables`
- `DeepMergeTables`
- `OverwriteSelf`

Before editing a concrete object, trace its inheritance chain. Many unintended global changes come from editing a shared base instead of a leaf entry.

### 6. Trait behavior is usually aggregated through cached values

Trait effects are commonly consumed through:

- `CurrentRun.Hero.HeroTraitValuesCache`
- `GetHeroTraitValues(...)`

That means a boon change often spans both:

- the source trait definition in `TraitData*.lua`
- the consumer logic in `CombatLogic.lua`, `PowersLogic.lua`, `EffectLogic.lua`, `ManaLogic.lua`, or `RoomLogic.lua`

If a trait seems ignored, search for the property key it contributes, not only the trait name.

### 7. Dynamic dispatch is common

Many behaviors are driven by function names stored in data and executed via `CallFunctionName(...)`.

Consequences:

- callers may be far from definitions
- renaming a function can silently break behavior
- a direct reference search may miss string-based dispatch

When editing a callback, search both:

- the function definition
- string fields that reference it

### 8. Control flow is hook-driven

This codebase uses engine-style hooks such as:

- `OnPreThingCreation`
- `OnAnyLoad`
- `OnMenuOpened`
- `OnMenuCloseFinished`
- `OnKeyPressed`
- combat hooks like `OnProjectileBlock`, `OnDodge`, `OnWeaponTriggerRelease`

Do not expect a single conventional app entry point or linear call chain.

### 9. Presentation is usually separate from mechanics

- mechanical logic: `CombatLogic.lua`, `PowersLogic.lua`, `EffectLogic.lua`, `RunLogic.lua`, `EncounterLogic.lua`
- presentation logic: `*Presentation.lua`, `AudioPresentation.lua`, `CombatPresentation.lua`, `RoomPresentation.lua`

If the change is purely mechanical, avoid editing presentation files unless the mechanic also needs player-facing feedback.

### 10. Save compatibility matters

If a change introduces persistent state, inspect:

- `RunLogic.lua` for initialization
- `SaveLogic.lua` for persistence rules
- `PatchLogic.lua` for backward compatibility

Prefer narrow state scope:

- `SessionMapState` for temporary combat bookkeeping
- `MapState` for room-local state
- `CurrentRun` for run-lifetime state
- `GameState` only when the change truly must persist across runs/saves

## Modder workflows

### Changing a boon, blessing, keepsake, aspect, or weapon trait

Start with:

- `TraitData*.lua`
- `LootData*.lua` if the issue is acquisition/offering logic
- `WeaponData.lua` if weapon properties are involved

Recommended flow:

1. Find the trait entry.
2. Identify the exact property keys or callback names it contributes.
3. Find the consumer logic for those properties.
4. Check whether values are cached on the hero.
5. If effects/projectiles/follow-up attacks are involved, inspect `EffectData.lua`, `ProjectileData.lua`, and `WeaponData.lua`.

Common mistake:

- changing text or rarity data and expecting the mechanic itself to change

### Changing an enemy or boss

Start with:

- `EnemyData*.lua`
- `EnemyAILogic.lua`
- `CombatLogic.lua`

Recommended flow:

1. Find the concrete enemy table.
2. Trace `InheritFrom`.
3. Check which fields are inherited versus overridden.
4. Search referenced weapons, projectiles, and effects.
5. If the enemy has special spawning, inspect `EncounterLogic.lua` and encounter data too.

Common mistake:

- editing a widely shared base when only one enemy should change

### Changing an encounter, room event, or ally assist spawn

Start with:

- `EncounterData*.lua`
- `EncounterLogic.lua`
- `RoomData*.lua`

Check:

- wave logic
- spawn caps
- spawn point selection
- room requirements
- encounter flags written to room/run state

Common mistake:

- editing a unit template but not the encounter-time overwrite/variant path

### Changing a status effect or debuff

Start with:

- `EffectData.lua`
- `EffectLogic.lua`
- `CombatLogic.lua` or `PowersLogic.lua`

Typical chain:

1. trait/weapon/projectile applies the effect
2. `EffectData.lua` defines duration, stacking, flags, VFX, callbacks
3. runtime logic reacts via `OnApplyFunctionName`, `OnDamagedFunctionName`, `OnClearFunctionName`, etc.

Common mistake:

- changing effect duration/flags without checking custom callbacks that also modify the outcome

### Changing UI, HUD, codex, or screen behavior

Start with:

- `UILogic.lua`
- `HUDData.lua`
- `UIData.lua`
- `*ScreenData.lua`
- related `*Presentation.lua` only when presentation is the real issue

Common mistake:

- editing presentation-only code when the widget/config data lives in screen or UI data

## Safe mod edit patterns

### Prefer additive edits over shared-base edits

Safer pattern:

- create a narrow override or variant
- point only the intended source/encounter/reward to it

Riskier pattern:

- editing a widely reused base like `BaseVulnerableEnemy`
- overloading a shared property key used by many traits
- modifying a broad global helper when only one feature should change

### Clone-and-override enemy pattern

Use when one encounter should spawn a customized enemy variant.

Typical flow:

1. Copy the concrete enemy table.
2. Keep `InheritFrom` if possible.
3. Override only required fields.
4. Repoint the intended encounter/spawn source to the new entry.

After cloning, re-check:

- named weapons
- callback function names
- caps/composition rules
- presentation asset references

### Add a new trait property key pattern

Use when the trait should contribute a behavior the runtime does not yet understand.

Typical flow:

1. Add the new property payload in `TraitData*.lua`.
2. Add a localized consumer in the appropriate logic file.
3. Read values via `GetHeroTraitValues("YourPropertyKey")` or the hero cache.

Prefer:

- one narrow property key
- one matching consumer path

Avoid:

- overloading an unrelated shared property key

### Add a new effect callback pattern

Use when a buff/debuff needs custom runtime behavior.

Typical flow:

1. define or extend the effect in `EffectData.lua`
2. wire callback fields
3. implement the callback in `EffectLogic.lua`, `CombatLogic.lua`, or `PowersLogic.lua`
4. search all string references after any rename

### Encounter-specific spawn override pattern

If a spawn change should only affect one encounter or room, prefer editing:

- the relevant `EncounterData*.lua` entry
- a specific branch in `EncounterLogic.lua`
- the room's encounter selection in `RoomData*.lua`

Prefer not to edit:

- generic spawn helpers used by many encounters
- shared combat setup logic unless the change is intentionally global

## Debugging heuristics

When a change seems ignored:

1. Confirm the file is actually imported or loaded.
2. Check whether inheritance or later overwrites replace your edit.
3. Search for string-based callback dispatch.
4. Check whether the behavior is cached.
5. Verify `GameStateRequirements`, room requirements, or `fullGame` gating.

When a change affects too much:

1. Search upward for shared bases in `InheritFrom`.
2. Check whether the edited function is called by many data tables.
3. Search for the same property key across multiple trait/enemy families.

## Boon rarity note

If the task is about boon rarity:

- base rarity rates are built in `RoomLogic.lua` by `GetRarityChances`
- normal boon offer rolling is handled in `TraitLogic.lua`
- source-specific overrides may exist in loot, room, store, or NPC data
- a boon must also support the rolled rarity in its own `RarityLevels`

Do not assume each boon has an independent standalone rarity probability field.

## Agent rules for this repo

- Build context from the actual Lua files before making assumptions.
- Prefer `rg` for codebase search.
- Do not claim validation from tests unless you actually found and ran them.
- Be careful with dirty worktrees or user changes; do not revert unrelated edits.
- When a feature touches persistence, inspect `RunLogic.lua`, `SaveLogic.lua`, and `PatchLogic.lua` together.
- For modding requests, first classify the change as trait, enemy, encounter, effect, UI, or save/progression work, then start in the matching data file.
- For desktop-tool requests, classify first as UI (`ui/main_window.py`), patch logic (`patches/*`), or file workflow (`operations_support/mod_service.py`) before editing.
- Keep references current with the live workspace folder name `.hades2_mod` (legacy `.hades2_mod_ui` may only appear in migration logic).

## Python refactor guardrails

- Preserve facade imports (`hades_mod_ui.app`, `hades_mod_ui.operations`, `hades_mod_ui.state`, `hades_mod_ui.patches`) unless intentionally doing a breaking change.
- Prefer placing new logic in split packages first (`ui/`, `operations_support/`, `state/`, `patches/`) rather than growing facade files.
- Treat `state_legacy.py` and `patches_legacy.py` as transitional references; avoid adding new behavior there.
- For behavior-preserving refactors, run:
  - `python -m pytest -q`
  - optional compile sanity: `python -m compileall src`
