# Boon Multiplier Guide

This guide explains how to set boon multipliers in detail in this repository.

It covers:

- where boon multipliers are defined
- how to edit one boon safely
- how to batch-edit many boons
- how to validate changes in this repo workflow

## 1. Know what "multiplier" means for boons

There is no single global `BoonMultiplier` field for all boons.

In this script dump, a boon can scale through several patterns:

1. `RarityLevels` multipliers (most common for core boon scaling)
2. nested action/modifier multipliers (`BaseValue`, `SourceIsMultiplier`, `AbsoluteStackValues`)
3. additive values (`ChangeValue`) that are not multipliers

So first identify which pattern your target boon uses.

## 2. Main files you will edit

Primary boon definitions are in:

- `Content/Scripts/TraitData_*.lua` (for example `TraitData_Aphrodite.lua`, `TraitData_Zeus.lua`)

Where boons are offered (pool/source) is in:

- `Content/Scripts/LootData_*.lua`

Helpful runtime consumers:

- `Content/Scripts/CombatLogic.lua`
- `Content/Scripts/PowersLogic.lua`
- `Content/Scripts/EffectLogic.lua`

## 3. Fast way to find a boon and its multiplier fields

From repo root:

```powershell
Get-ChildItem .\Content\Scripts\TraitData_*.lua | Select-String -Pattern "Boon =|RarityLevels|Multiplier|BaseValue|SourceIsMultiplier|AbsoluteStackValues"
```

If you already know the boon name:

```powershell
Get-ChildItem .\Content\Scripts\TraitData_*.lua | Select-String -Pattern "AphroditeWeaponBoon|RarityLevels|Multiplier|BaseValue|AbsoluteStackValues"
```

Tip: use the exact trait key (example: `ZeusWeaponBoon`, `PoseidonWeaponBoon`) instead of localized display text.

## 4. Pattern A (most common): edit `RarityLevels` multiplier

Example (real structure from `TraitData_Aphrodite.lua`):

```lua
AphroditeWeaponBoon =
{
    RarityLevels =
    {
        Common = { Multiplier = 1.00, },
        Rare = { Multiplier = 1.25, },
        Epic = { Multiplier = 1.50, },
        Heroic = { Multiplier = 1.75, },
    },
}
```

How to edit:

1. Open the boon block in its `TraitData_<God>.lua` file.
2. Find `RarityLevels`.
3. Change each rarity `Multiplier` value you want.
4. Keep commas/braces exactly valid Lua syntax.

If you want the same scaling for many gods, repeat this for each `*WeaponBoon`, `*SpecialBoon`, `*CastBoon`, etc. trait block.

## 5. Pattern B: edit nested runtime multipliers

Some boons use multiplier payloads inside runtime action tables, for example:

- `AddOutgoingDamageModifiers`
- `OnEnemyDamagedAction.Args`
- effect argument blocks

Example patterns seen in this repo:

```lua
ProximityMultiplier =
{
    BaseValue = 1.8,
    SourceIsMultiplier = true,
    AbsoluteStackValues =
    {
        [1] = 1.25,
        [2] = 1.15,
    },
}
```

and

```lua
DamageMultiplier =
{
    BaseValue = 1,
    AbsoluteStackValues =
    {
        [1] = 0.25,
    },
}
```

How to edit:

1. Keep `SourceIsMultiplier = true` unchanged unless you intentionally want non-multiplier behavior.
2. `BaseValue` controls the default multiplier.
3. `AbsoluteStackValues` controls stack/pom style overrides by level index.
4. If both exist, stack values can override progression behavior.

## 6. Pattern C: additive values are not multipliers

Some boon lines use `ChangeValue` or flat values instead of multiplier math.

Example:

```lua
BaseValue = 6
```

or

```lua
ChangeValue = 25
```

Do not treat these as percent multipliers unless the consumer code expects that format.

Rule of thumb:

- `Multiplier` / `SourceIsMultiplier` fields => multiplicative scaling
- plain `ChangeValue` / many `BaseValue` fields => often flat/additive scaling

When unsure, search the consumer key in logic files (`CombatLogic.lua`, `PowersLogic.lua`, `EffectLogic.lua`).

## 7. How to set multipliers for each boon category

Use this repeatable sequence for every boon you want:

1. Find boon trait key in `TraitData_*.lua`.
2. Confirm category by slot/behavior (`Slot = "Melee"`, cast action, effect, etc.).
3. Edit `RarityLevels.Multiplier` if present.
4. Edit nested `...Multiplier.BaseValue` / `AbsoluteStackValues` if that boon uses runtime modifiers.
5. Leave unrelated `PropertyChanges` cosmetic lines alone.

This avoids accidental edits to VFX/SFX-only data.

## 8. Batch editing many boons

To locate all explicit `Multiplier` lines quickly:

```powershell
Get-ChildItem .\Content\Scripts\TraitData_*.lua | Select-String -Pattern "Multiplier\s*="
```

To locate stack-style tuning blocks:

```powershell
Get-ChildItem .\Content\Scripts\TraitData_*.lua | Select-String -Pattern "AbsoluteStackValues|SourceIsMultiplier|BaseValue"
```

Edit in small batches (one god file or one boon family at a time), then validate.

## 9. Repo-safe workflow (important)

Because this repo has a mod workspace flow, use this order:

1. Edit source files under `Content/Scripts/*.lua`.
2. If you use the desktop tool, generate patched copies first into `.hades2_mod/generated/...`.
3. Backup originals before replacement (`.hades2_mod/originals/...`).
4. Apply replacement only after checks.
5. Restore from backups if needed.

## 10. Validation checklist (no test runner required)

After editing multipliers:

1. Confirm Lua syntax is still valid (braces, commas, table nesting).
2. Re-search your boon key to verify only intended lines changed.
3. Re-search shared keys (`Multiplier`, `BaseValue`) to ensure no accidental global edits.
4. In game, verify actual damage/effect values match expectation across rarity tiers.
5. If results look wrong, check for secondary modifiers from other boons, keepsakes, or meta-upgrades.

## 11. Common mistakes

- Editing `PropertyChanges` and expecting numeric boon scaling changes.
- Changing only tooltip extract/report lines while leaving real source multiplier unchanged.
- Editing a shared base trait when only one boon should change.
- Treating flat `ChangeValue` fields as if they were percentage multipliers.

## 12. Practical example template

Use this template when tuning a single boon:

1. Locate trait block: `YourGodSomethingBoon = { ... }`
2. Tune rarity scaling:

```lua
RarityLevels =
{
    Common = { Multiplier = 1.00, },
    Rare = { Multiplier = 1.30, },
    Epic = { Multiplier = 1.60, },
    Heroic = { Multiplier = 1.90, },
}
```

3. Tune runtime multiplier block if present:

```lua
SomeMultiplier =
{
    BaseValue = 1.20,
    SourceIsMultiplier = true,
    AbsoluteStackValues =
    {
        [1] = 1.20,
        [2] = 1.35,
        [3] = 1.50,
    },
}
```

4. Validate with the checklist above.

---

If you want, the next step can be a follow-up table listing exact boon trait keys per god file so you can edit every boon in a strict checklist order.
