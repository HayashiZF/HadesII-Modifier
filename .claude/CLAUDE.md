# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository nature

This folder is a Hades II script dump/modding base, not a standalone app project. It contains many top-level Lua modules but no package manifest, build system, test runner, linter config, README, Cursor rules, or Copilot instructions were found in this folder.

Because of that:
- There are no repo-local `build`, `lint`, or `test` commands to run here.
- Changes here should be treated as script edits intended to be consumed by the game/mod loader outside this folder.
- Validation is primarily by inspecting load paths, inheritance, trigger hooks, and data/logic interactions.

## Common commands

### Repository inspection
- `ls *.lua` — list the top-level Lua modules in this script dump.
- `rg '^Import "' RunData.lua RoomLogic.lua UtilityLogic.lua` — inspect bootstrap/load order.
- `rg 'InheritFrom|DeepInheritance' *.lua` — find data-driven inheritance patterns.
- `rg 'CurrentRun|GameState|MapState|SessionMapState' *.lua` — trace which state table a feature uses.
- `rg 'CallFunctionName\(|GetHeroTraitValues\(' *.lua` — trace dynamic dispatch and trait-driven behavior.
- `rg 'OnKeyPressed\{|OnAnyLoad|OnPreThingCreation' *.lua` — find engine/event hooks.

### Focused navigation patterns
- `rg 'NPC_<Name>|EnemyData_<Name>|EncounterData_<Name>|TraitData_<Name>' *.lua` — find a character/enemy/encounter/trait family.
- `rg 'SpawnUnit\(|SetupUnit\(|DeepCopyTable\(' *.lua` — trace how units or objects are instantiated.
- `rg 'EffectData\.|ApplyEffect\(|ActiveEffects' *.lua` — trace status-effect behavior.

### Copy-paste searches for common modding work

#### Find a trait and everything that consumes it
- `rg 'TraitNameHere' TraitData*.lua LootData*.lua PowersLogic.lua CombatLogic.lua EffectLogic.lua ManaLogic.lua RoomLogic.lua`
- `rg 'GetHeroTraitValues\("PropertyKeyHere"|HeroTraitValuesCache\.PropertyKeyHere' *.lua`

#### Find an enemy, its callbacks, and where it is spawned
- `rg 'EnemyNameHere' EnemyData*.lua EncounterData*.lua EncounterLogic.lua RoomData*.lua CombatLogic.lua`
- `rg 'OnDeathFunctionName|OnHitFunctionName|OnDamagedWeaponInterrupt|DefaultAIData' EnemyData*.lua`

#### Find an encounter and all related room/spawn logic
- `rg 'EncounterNameHere' EncounterData*.lua EncounterLogic.lua RoomData*.lua`
- `rg 'SpawnUnit\(|SelectSpawnPoint\(|WaveSpawnDelay|ActiveEnemyCap' EncounterData*.lua EncounterLogic.lua`

#### Find an effect from definition to application
- `rg 'EffectNameHere' EffectData.lua EffectLogic.lua PowersLogic.lua CombatLogic.lua WeaponData.lua ProjectileData.lua`
- `rg 'ApplyEffect\(' *.lua`

#### Find dynamic callback references before renaming a function
- `rg 'FunctionNameHere' *.lua`
- `rg 'FunctionName|OnApplyFunctionName|OnDamagedFunctionName|OnClearFunctionName|ProjectileBlockFunctionName|OnDeathFunctionName' *.lua`

#### Find inheritance chains that may be overriding your change
- `rg 'InheritFrom|DeepInheritance' EnemyData*.lua TraitData*.lua EffectData.lua EncounterData*.lua`
- `rg 'BaseVulnerableEnemy|BaseBossEnemy|BaseAlly|DefaultAchievement|BaseBadge' *.lua`

## High-level architecture

## 1. Bootstrapping is split between data imports and runtime initialization

Two files give the big picture:
- `RunData.lua` is the main data registry/import hub.
- `RoomLogic.lua` is the runtime bootstrap for map loads.

`RunData.lua` seeds the major global tables (`RoomData`, `TraitData`, `EnemyData`, `LootData`, `ScreenData`, etc.) and then imports the many `*Data.lua` modules that populate them. It also conditionally imports some content only when `fullGame` is enabled.

`RoomLogic.lua` then initializes live runtime state on map load:
- `GameStateInit()` for persistent progression/state
- `RunStateInit()` for the current run
- `SessionMapStateInit()` for transient per-room/per-session combat state
- `MapStateInit()` for live objects and map-local caches
- `DoPatches()` for save/data migrations

When trying to understand “where something comes from,” usually start with `RunData.lua` for static definitions and `RoomLogic.lua` for when those definitions become active.

## 2. The codebase is heavily data-driven

A large amount of behavior is encoded in tables rather than hardcoded control flow.

Common pattern:
- `SomethingData.lua` defines large tables.
- `SomethingLogic.lua` interprets or mutates them at runtime.
- `SomethingPresentation.lua` handles VFX/UI/audio-facing presentation.

Examples:
- `EnemyData*.lua` defines enemy/NPC/unit archetypes.
- `EncounterData*.lua` defines combat encounter composition and special encounter variants.
- `TraitData*.lua` defines boons, weapons, aspects, keepsakes, and meta-upgrade-driven trait effects.
- `EffectData.lua` defines status/effect records that runtime logic applies and clears.
- `HeroData.lua` defines the base hero table that `RunLogic.lua` clones into the active hero.

For most modding tasks, edits are safer and more idiomatic when made in the data table that drives the feature, not by rewriting shared runtime logic.

## 3. Runtime state is organized into a few important global tables

These are the most important state layers to distinguish:

- `GameState` — persistent progression/save data across runs.
  - Initialized in `RunLogic.lua`.
  - Patched/migrated in `PatchLogic.lua`.
  - Save filtering is defined in `SaveLogic.lua`.

- `CurrentRun` — state for the active run.
  - Contains the active hero, room progression, picked traits, records, etc.

- `MapState` — live room/map state.
  - Active obstacles, spawn points, aggroed units, spell summons, UI-related map flags, and other room-local runtime structures.

- `SessionMapState` — transient combat/session caches.
  - Projectile bookkeeping, hit records, locks, queued voice lines, temporary counters, per-frame caches.

- `SessionState` — broader session/runtime caches not tied to one room instance.
  - Global cooldowns, property change caches, objective swaps, config-derived flags.

A lot of bugs come from editing logic against the wrong state layer. Before changing behavior, confirm whether the feature is supposed to persist across saves, across a run, or only within the current room/combat context.

## 4. Units are usually spawned from data templates, then customized at runtime

A recurring pattern in encounter/combat code is:
1. `DeepCopyTable(...)` from a base template in `EnemyData` or related data.
2. Optionally merge/overwrite variant data with `OverwriteSelf(...)`.
3. `SpawnUnit(...)` to create the engine object.
4. `SetupUnit(...)` to bind runtime behavior.

This pattern appears clearly in `EncounterLogic.lua` for Artemis, Icarus, Heracles, and Nemesis combat spawns.

When modifying a spawn behavior, check all four layers:
- base data template
- variant/overwrite data
- spawn point selection logic
- post-spawn setup/presentation

## 5. Inheritance and merging are core composition mechanisms

This codebase uses table composition extensively.

Important mechanisms:
- `InheritFrom = { ... }` in data tables
- `DeepInheritance = true` for nested merges
- `DeepCopyTable`, `MergeTables`, `DeepMergeTables`, `OverwriteSelf` from utility/runtime helpers

Example: `EnemyData.lua` defines reusable bases like `IsNeutral`, `BaseVulnerableEnemy`, and `BaseBossEnemy`, then concrete enemies inherit from them elsewhere.

For mods, prefer extending an existing base or variant instead of duplicating a full table unless you intentionally want to fork behavior.

## 6. Trait/boon behavior is aggregated through cached trait values

The hero’s build is not handled one trait at a time in most runtime code. Instead, runtime systems read from aggregated caches such as `CurrentRun.Hero.HeroTraitValuesCache` and helper queries like `GetHeroTraitValues(...)`.

This pattern is used throughout combat and power processing for:
- on-dodge hooks
- on-block hooks
- on-hit/on-damage effects
- weapon fire overrides
- mana/cost modifiers
- enemy death triggers
- effect apply/clear callbacks

This means a “simple boon change” often requires checking both:
- the source `TraitData*.lua` entry
- the consuming runtime logic in `CombatLogic.lua`, `PowersLogic.lua`, `EffectLogic.lua`, `ManaLogic.lua`, etc.

If a trait appears to “do nothing,” search for the exact property key it contributes, not only the trait name.

## 7. Dynamic dispatch is common

A lot of runtime behavior is driven by function names stored in data, then executed via `CallFunctionName(...)`.

This is used in combat, audio, encounters, cosmetics, effects, and UI. As a result:
- behavior may be declared far from the function that executes it
- renaming a function without updating string references can silently break behavior
- finding callers often requires searching for both the function definition and the string-valued field that references it

When editing dispatch-driven code, search for both:
- the function name itself
- fields like `FunctionName`, `OnApplyFunctionName`, `OnDamagedFunctionName`, `ProjectileBlockFunctionName`, etc.

## 8. Event hooks are engine-style, not conventional app entry points

This repository relies on hook registrations such as:
- `OnPreThingCreation`
- `OnAnyLoad`
- `OnMenuOpened`
- `OnMenuCloseFinished`
- `OnKeyPressed`
- combat hooks like `OnProjectileBlock`, `OnDodge`, `OnWeaponTriggerRelease`

So the control flow is event-driven and distributed. When tracing behavior, do not expect a single linear call stack like a typical app.

`Debug.lua` is especially useful for discovering available debug hooks and engine-facing keybind-triggered helpers.

## 9. Presentation is usually separated from mechanics

The repo often splits mechanical changes from audiovisual/UI effects:
- `CombatLogic.lua`, `PowersLogic.lua`, `EffectLogic.lua`, `RunLogic.lua`, `EncounterLogic.lua` contain game rules/state changes.
- `*Presentation.lua`, `AudioPresentation.lua`, `CombatPresentation.lua`, `RoomPresentation.lua`, etc. contain VFX, camera, audio, and animation-facing behavior.
- `UILogic.lua` and HUD/screen data modules manage menus, HUD creation, and UI lifecycle.

If a change is purely mechanical, avoid modifying presentation files unless the mechanic also needs player-facing feedback.

## 10. Save compatibility matters

`PatchLogic.lua` contains migration/cleanup logic for evolving save structures.
`SaveLogic.lua` defines what parts of global state and run state are preserved.

If you add new persistent structures or rely on older saved data, review:
- whether the state belongs in `GameState`, `CurrentRun`, `MapState`, or `SessionMapState`
- whether it needs save whitelist support
- whether old saves need patching/default initialization

Not every new field should be persisted. Many runtime caches are intentionally rebuilt instead of saved.

## Modder workflows

## Changing a boon, blessing, keepsake, aspect, or weapon trait

Start here first:
- `TraitData*.lua` for the trait definition
- `LootData*.lua` if the issue is about offering/acquiring the boon rather than the boon effect itself
- `WeaponData.lua` if the trait modifies weapon behavior through weapon properties

Then verify where the trait is consumed:
- `rg '<property key>' TraitData*.lua CombatLogic.lua PowersLogic.lua EffectLogic.lua ManaLogic.lua RoomLogic.lua`
- `rg 'GetHeroTraitValues\("<property key>"' *.lua`

Typical trait edit flow:
1. Find the trait entry in `TraitData*.lua`.
2. Identify the exact property/function names it contributes.
3. Find the consumer logic for those properties.
4. Check whether the behavior is cached on the hero via `HeroTraitValuesCache`.
5. If the trait spawns effects, projectiles, or follow-up attacks, also inspect `EffectData.lua`, `ProjectileData.lua`, and `WeaponData.lua`.

Common mistake: changing display text or rarity data and expecting gameplay to change. The mechanical effect usually comes from trait property keys consumed elsewhere.

## Changing an enemy or boss

Start here first:
- `EnemyData*.lua` for base stats, AI parameters, weapons, death behavior, loot, and flags
- `EnemyAILogic.lua` for shared AI/state-machine logic
- `CombatLogic.lua` for global combat rules that affect all enemies

Recommended workflow:
1. Find the concrete enemy table.
2. Trace its `InheritFrom` chain back to shared bases.
3. Check which fields are inherited versus overridden locally.
4. Search for any named weapons/projectiles/effects referenced by that enemy.
5. If the enemy is spawned specially, inspect `EncounterLogic.lua` or encounter-specific data too.

Useful searches:
- `rg '<EnemyName>' EnemyData*.lua EncounterData*.lua EncounterLogic.lua CombatLogic.lua`
- `rg 'OnDeathFunctionName|OnHitFunctionName|OnDamagedWeaponInterrupt|DefaultAIData' EnemyData*.lua`

Common mistake: editing a shared base like `BaseVulnerableEnemy` when the goal was to tune one enemy only.

## Changing an encounter, room event, or ally assist spawn

Start here first:
- `EncounterData*.lua` for encounter definitions and room-specific encounter composition
- `EncounterLogic.lua` for special scripted spawns and event flow
- `RoomData*.lua` for room-level setup and progression rules

If the mod changes who appears in combat or when they appear, inspect:
- wave logic
- spawn caps
- spawn point selection
- room requirements
- encounter flags written onto `CurrentRun.CurrentRoom` or the encounter object

Useful searches:
- `rg '<EncounterName>|ArtemisId|IcarusId|NemesisId|HeraclesId' EncounterData*.lua EncounterLogic.lua RoomData*.lua`
- `rg 'SpawnUnit\(|SelectSpawnPoint\(|WaveSpawnDelay|ActiveEnemyCap' EncounterLogic.lua EncounterData*.lua`

Common mistake: editing the spawned unit template but not the encounter-time overwrite/variant data.

## Changing a status effect or debuff

Start here first:
- `EffectData.lua` for the effect definition
- `EffectLogic.lua` for application/clear/tick behavior
- `CombatLogic.lua` or `PowersLogic.lua` if the effect is attached to damage, crits, or trait callbacks

Typical effect chain:
1. Trait/weapon/projectile applies the effect.
2. `EffectData` defines duration, stacking, flags, VFX, and optional callbacks.
3. Runtime logic reacts through `OnApplyFunctionName`, `OnDamagedFunctionName`, `OnClearFunctionName`, etc.

Useful searches:
- `rg '<EffectName>' EffectData.lua EffectLogic.lua CombatLogic.lua PowersLogic.lua WeaponData.lua ProjectileData.lua`
- `rg 'ApplyEffect\(' *.lua`

Common mistake: changing `EffectData` duration or flags without checking custom callback logic that also modifies the outcome.

## Changing UI, HUD, codex, or screen behavior

Start here first:
- `UILogic.lua` for global UI lifecycle and screen setup
- `HUDData.lua`, `UIData.lua`, `*ScreenData.lua` for screen structure/data
- `*Presentation.lua` when the issue is animation/audio/camera-facing rather than data layout

If a UI element appears on load or screen open, search hooks such as:
- `OnAnyLoad`
- `OnMenuOpened`
- `OnMenuCloseFinished`

Common mistake: editing presentation-only code when the actual widget/configuration lives in `ScreenData`.

## Save-safe modding rules

When adding mod state, decide first whether it belongs in:
- `GameState` for persistent progression across runs
- `CurrentRun` for current-run persistence
- `MapState` for live room state that may be saved selectively
- `SessionMapState` or `SessionState` for transient caches that should usually not persist

Before adding persistent state, inspect:
- `RunLogic.lua` for default initialization
- `SaveLogic.lua` for whitelist/blacklist behavior
- `PatchLogic.lua` for backward compatibility with older saves

If a mod only needs temporary bookkeeping during combat, prefer `SessionMapState` over `GameState`.

## Debugging heuristics for mods

When a change seems ignored:
1. Confirm the file is part of the import path in `RunData.lua` or loaded by runtime logic.
2. Check whether the edited table inherits from something that later overwrites it.
3. Search for dynamic dispatch string references instead of only direct function calls.
4. Check whether a cached trait/property value is built once and reused.
5. Verify whether the behavior is gated by `GameStateRequirements`, `RequiredTraitName`, room set, or `fullGame` checks.

When a change affects too much:
1. Search upward for shared bases in `InheritFrom` chains.
2. Check whether the edited function is called via `CallFunctionName(...)` from many data tables.
3. Search for the same property key in multiple `TraitData*.lua` or `EnemyData*.lua` families.

## Best places to look by mod type

- New boon behavior: `TraitData*.lua` -> `PowersLogic.lua` / `CombatLogic.lua` -> `EffectData.lua`
- Enemy stat/AI tweak: `EnemyData*.lua` -> `EnemyAILogic.lua` -> referenced weapon/projectile/effect data
- Spawn/encounter change: `EncounterData*.lua` -> `EncounterLogic.lua` -> `RoomData*.lua`
- Hero baseline tweak: `HeroData.lua` -> `RunLogic.lua` -> consuming logic
- Save/progression tweak: `RunLogic.lua` -> `SaveLogic.lua` -> `PatchLogic.lua`
- HUD/menu tweak: `UILogic.lua` -> `HUDData.lua` / `UIData.lua` / `*ScreenData.lua`

## Safe mod edit patterns

### Prefer additive edits over shared-base edits

Safer pattern:
- copy a concrete enemy/trait/effect definition or create a narrow variant override
- point the intended encounter/reward/source at that new definition

Riskier pattern:
- editing a shared base such as `BaseVulnerableEnemy`, a widely reused trait property key, or a global combat helper when you only meant to change one feature

Good use cases:
- one custom enemy variant for a specific encounter
- one boon variant with a different callback or numeric tuning
- one room/encounter override that swaps a spawn or reward source

### Clone-and-override enemy pattern

Use when you want a specific enemy variant without changing every instance of that enemy family.

Typical flow:
1. Find the concrete source enemy in `EnemyData*.lua`.
2. Copy that table into a new mod-specific entry.
3. Keep `InheritFrom` intact if possible.
4. Override only the fields you need.
5. Update the encounter/spawn source to use the new name.

Check all linked references after cloning:
- `WeaponOptions` / named weapons
- `OnDeathFunctionName`, `OnHitFunctionName`, `OnDamaged...` callbacks
- `ActiveEnemyCap` or encounter composition rules
- any presentation assets referenced by name

### Add a new trait property key pattern

Use when the trait should contribute a new kind of behavior that existing consumer logic does not yet understand.

Typical flow:
1. Add the property/function payload in the `TraitData*.lua` entry.
2. Pick the runtime consumer file based on behavior type:
   - combat reaction -> `CombatLogic.lua`
   - boon/weapon synergy -> `PowersLogic.lua`
   - effect lifecycle -> `EffectLogic.lua`
   - mana/spell behavior -> `ManaLogic.lua`
   - room/reward behavior -> `RoomLogic.lua`
3. Read values through `GetHeroTraitValues("YourPropertyKey")` or the relevant hero cache.
4. Keep the consumer localized to the event where it matters.

Good pattern:
- add one narrowly named property key and one matching consumer path

Risky pattern:
- overloading an existing shared property key that many unrelated traits already use

### Add a new effect callback pattern

Use when a debuff/buff needs custom runtime behavior.

Typical flow:
1. Add or extend the effect in `EffectData.lua`.
2. Wire named callbacks such as:
   - `OnApplyFunctionName`
   - `OnDamagedFunctionName`
   - `OnClearFunctionName`
3. Implement the callback in the appropriate logic file, usually `EffectLogic.lua`, `CombatLogic.lua`, or `PowersLogic.lua`.
4. Search for all string references to the callback name after renaming.

If the effect is only data-driven, prefer duration/flags/stacking changes in `EffectData.lua` and avoid adding a new callback unless necessary.

### Encounter-specific spawn override pattern

Use when a spawn change should only happen in one encounter or room.

Safer places to edit:
- the relevant `EncounterData*.lua` entry
- a specific branch in `EncounterLogic.lua`
- the room’s encounter selection in `RoomData*.lua`

Less safe places to edit:
- shared spawn helpers used by many encounters
- generic enemy setup logic in `CombatLogic.lua` or `RoomLogic.lua`

### Save-state pattern

If the mod needs memory across rooms or runs, decide the narrowest state scope first.

Preferred order:
- `SessionMapState` for temporary combat bookkeeping
- `MapState` for live room state
- `CurrentRun` for run-lifetime state
- `GameState` only when the change truly needs persistence across runs/saves

If you add `GameState` or persistent `CurrentRun` fields, review `RunLogic.lua`, `SaveLogic.lua`, and `PatchLogic.lua` as one unit.

### Concrete do/don’t examples

Do:
- add a new `TraitData_*` entry and wire one new consumer for a custom boon mechanic
- add a new enemy variant and swap only one encounter to spawn it
- add a room-specific override in `EncounterLogic.lua` when a special ally spawn should happen only there
- keep presentation changes in `*Presentation.lua` unless mechanics truly require them

Don’t:
- tune `BaseVulnerableEnemy` just to change one miniboss
- rename a callback function without searching for string-based `FunctionName` references
- store temporary combat counters in `GameState`
- assume a trait change failed before checking whether its effect is gated by `GameStateRequirements`, room set, or `fullGame`

## Practical file map

Use this as the shortest route to the right subsystem:
- `RunData.lua` — master import/data assembly file
- `RoomLogic.lua` — map bootstrap, room lifecycle, map/session state init
- `RunLogic.lua` — hero/run creation and persistent `GameState` initialization
- `SaveLogic.lua` — save whitelists/blacklists
- `PatchLogic.lua` — save/data migrations
- `HeroData.lua` — base hero definition
- `CombatLogic.lua` — central combat processing and many combat hooks
- `PowersLogic.lua` — boon/trait/weapon synergy behavior layered onto combat
- `EffectData.lua` / `EffectLogic.lua` — status effect definitions and runtime handling
- `EncounterData*.lua` / `EncounterLogic.lua` — encounter composition and special spawn flow
- `EnemyData*.lua` / `EnemyAILogic.lua` — enemy archetypes and AI behavior
- `UILogic.lua` plus `*ScreenData.lua` / `HUDData.lua` — UI and HUD lifecycle
- `Debug.lua` — useful engine/debug hooks and keybind-based helpers

## Working assumptions for future Claude instances

- Treat this repository as a game-script source tree, not a standalone buildable Lua app.
- Prefer targeted data edits over broad runtime rewrites.
- Before changing behavior, identify the full chain: imported data table -> inheritance/merge -> runtime state table -> dispatch hook -> presentation.
- For modding requests, first classify the change as trait, enemy, encounter, effect, UI, or save/progression work and start in the matching data file.
- If a feature touches persistence, inspect `RunLogic.lua`, `PatchLogic.lua`, and `SaveLogic.lua` together.
