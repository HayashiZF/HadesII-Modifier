# Guide: Force God Boon Offers to Epic During Gameplay

## Goal

Make boon offers from the gods come up at `Epic` rarity during normal gameplay, without editing individual boon definitions.

This guide does **not** apply any code changes yet. It explains where the rarity is actually decided, what to change later, and what edge cases to account for.

## Where boon rarity is really decided

The important pipeline in this script dump is:

1. `HeroData.lua` defines the base boon rarity chances for normal god boons.
   - `C:\Users\Administrator\Agents\Scripts - backup\HeroData.lua:170`
   - `C:\Users\Administrator\Agents\Scripts - backup\HeroData.lua:181`

2. `RoomLogic.lua` builds the effective rarity table in `GetRarityChances( loot )`.
   - `C:\Users\Administrator\Agents\Scripts - backup\RoomLogic.lua:2125`
   - This function starts from `HeroData.BoonData.RarityChances`, then applies room overrides, loot overrides, and hero rarity bonuses.

3. `TraitLogic.lua` calls `GetRarityChances` inside `SetTraitsOnLoot( lootData, args )`.
   - `C:\Users\Administrator\Agents\Scripts - backup\TraitLogic.lua:1750`
   - `C:\Users\Administrator\Agents\Scripts - backup\TraitLogic.lua:1766`

4. `TraitLogic.lua` then rolls each offered boon rarity from `lootData.RarityChances`.
   - `C:\Users\Administrator\Agents\Scripts - backup\TraitLogic.lua:1819`
   - `C:\Users\Administrator\Agents\Scripts - backup\TraitLogic.lua:1827`

5. The boon rarity roll order is defined in `TraitData.lua`.
   - `C:\Users\Administrator\Agents\Scripts - backup\TraitData.lua:713`
   - Current order: `Common`, `Rare`, `Epic`, `Duo`, `Legendary`

## What this means

If you only change `HeroData.BoonData.RarityChances`, you will change the base odds, but you will **not** fully control all god offers during gameplay.

That is because room and source-specific overrides can replace the base chances before the boon choices are rolled.

Examples already present in this dump:

- Chaos has its own `BoonRaritiesOverride`.
  - `C:\Users\Administrator\Agents\Scripts - backup\LootData_Chaos.lua:91`
- Several room files inject `BoonRaritiesOverride`.
  - `C:\Users\Administrator\Agents\Scripts - backup\RoomDataF.lua:1058`
  - `C:\Users\Administrator\Agents\Scripts - backup\RoomDataG.lua:1898`
  - `C:\Users\Administrator\Agents\Scripts - backup\RoomDataQ.lua:1355`
- There are scripted narrative cases that temporarily force Epic already.
  - `C:\Users\Administrator\Agents\Scripts - backup\NPCData_Dionysus.lua:1618`

## Recommended place to patch later

When you are ready to implement, the safest gameplay-level patch point is:

- `C:\Users\Administrator\Agents\Scripts - backup\TraitLogic.lua:1766`

Reason:

- By this point, `lootData.RarityChances = GetRarityChances( lootData )` has already pulled in:
  - base hero boon odds
  - room overrides
  - source-specific overrides
  - temporary and permanent rarity bonuses
- A clamp applied here will affect the final offer-generation step instead of fighting many earlier data sources.

## Recommended behavior to enforce

For god boon offers, normalize the final rarity chances to Epic-only:

- `Common = 0`
- `Rare = 0`
- `Epic = 1`
- `Duo = 0`
- `Legendary = 0`

If you want to include Hermes and other god-like shop sources, the condition should usually be based on:

- `lootData.GodLoot`
- or `lootData.TreatAsGodLootByShops`

Why both matter:

- Standard Olympian boon pickups use `GodLoot = true`
- Hermes is marked `TreatAsGodLootByShops = true`
  - `C:\Users\Administrator\Agents\Scripts - backup\LootData_Hermes.lua:10`
- Hades uses a custom NPC-style boon source with its own rarity data
  - `C:\Users\Administrator\Agents\Scripts - backup\NPCData_Hades.lua:58`

## Best scope choices

### Option A: Standard Olympian gods only

Use only:

- `lootData.GodLoot == true`

This is the cleanest interpretation if you mean the normal Aphrodite/Apollo/Ares/etc. boon reward flow.

### Option B: Include Hermes and similar god-style offers

Use:

- `lootData.GodLoot`
- `or lootData.TreatAsGodLootByShops`

This is broader and closer to "all gods" in gameplay terms.

### Option C: Include special sources like Chaos or Hades too

This needs extra handling because they do not follow the exact same data flags as the ordinary Olympian loot tables.

For that version, you should explicitly decide whether you want to cover:

- Chaos
- Hermes
- Hades
- narrative-only forced boon moments

## Why editing each god file is not the right first move

It is tempting to edit every `LootData_<God>.lua` or `TraitData_<God>.lua`, but that is not the main rarity control point.

Reasons:

- `LootData_<God>.lua` mostly defines the pool and presentation, not the final rolled rarity.
- `TraitData_<God>.lua` defines what each boon does at each rarity tier, not the chance that the game offers that tier.
- the actual roll happens later in `SetTraitsOnLoot()` and the offer-building loop in `TraitLogic.lua`

## One important edge case

Not every trait can necessarily become `Epic`.

The offer generator checks whether a trait actually has that rarity in its `RarityLevels` before rolling it. That logic is in:

- `C:\Users\Administrator\Agents\Scripts - backup\TraitLogic.lua:1827`

So a forced Epic rule should assume:

- regular boons with `Epic` in `RarityLevels` will become Epic
- Duo and Legendary boons should usually keep their own handling
- special boons without an Epic tier may need a fallback rule if you want to avoid unexpected `Common` results

## Practical implementation plan for later

When you decide to make the code change, the clean order is:

1. Patch `SetTraitsOnLoot()` in `TraitLogic.lua` after `lootData.RarityChances = GetRarityChances( lootData )`
2. Apply the Epic-only clamp only for the boon sources you want
3. Leave weapon upgrades, stack upgrades, and other non-god reward types alone
4. Sanity-check special sources like Chaos/Hades/Hermes based on your desired scope

## If you want the smallest possible change later

The smallest likely patch is:

- one localized condition in `TraitLogic.lua`
- no edits to individual god loot files
- no edits to individual boon `RarityLevels`

That approach is preferable in this repository because the project is heavily data-driven and shared-base edits can have wide side effects.

## Suggested validation checklist after implementation

Since this repository does not have a normal automated test setup, validation should be static plus in-game:

- confirm the patch only runs for the intended boon sources
- confirm `WeaponUpgrade`, `StackUpgrade`, and other non-god rewards are untouched
- confirm room overrides no longer bypass the Epic rule for your targeted sources
- confirm Hermes, Hades, and Chaos behave according to the scope you chose
- confirm Duo and Legendary boons are either intentionally suppressed or intentionally preserved

## Short version

If the goal is "all normal god boon offers become Epic during gameplay", the best future patch point is **not** `HeroData.lua`. It is the final offer setup in:

- `C:\Users\Administrator\Agents\Scripts - backup\TraitLogic.lua:1766`

That is the point where the game has already assembled the effective rarity chances, and where a single Epic-only clamp can reliably control the final boon offers.
