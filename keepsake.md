# Keepsake Buffing Guide (`TraitData_Keepsake.lua`)

This guide shows how to buff every keepsake trait in this repo safely and predictably.

## 1. Files you will edit

- Main data: `Content/Scripts/TraitData_Keepsake.lua`
- Runtime behavior (for special keepsakes):
  - `Content/Scripts/KeepsakeLogic.lua`
  - `Content/Scripts/PowersLogic.lua`
  - `Content/Scripts/RoomLogic.lua`
  - `Content/Scripts/GiftLogic.lua`

## 2. Core buff rules (important)

Most keepsakes scale like this:

1. Base stat is set on the trait (for example `BonusMoney = { BaseValue = 100 }`).
2. Current keepsake rank applies `RarityLevels.*.Multiplier`.
3. Tooltip values come from `ExtractValues` and `ReportValues`.

Practical implication:

- To make all ranks stronger, increase `BaseValue`.
- To change rank progression, edit `RarityLevels` multipliers.
- For chance-based keepsakes, keep chance <= `1.0` (100%) to avoid odd behavior.

## 3. Per-keepsake buff map

All line references below are from current `Content/Scripts/TraitData_Keepsake.lua`.

### `BlockDeathKeepsake` (line ~99)

- Buff keys:
  - `BlockDeathHealth = { BaseValue = 30 }`
  - `BlockDeathTimer = 10`
  - `RarityLevels.*.Multiplier`
- Stronger version example:
  - `BlockDeathHealth` to `45`
  - `BlockDeathTimer` to `12`

### `ReincarnationKeepsake` (line ~193)

- Buff keys:
  - `KeepsakeLastStandHealAmount = { BaseValue = 51 }`
  - `RarityLevels.*.Multiplier`
- Stronger version example:
  - Heal `51 -> 75`

### `DoorHealReserveKeepsake` (line ~282)

- Buff keys:
  - `DoorHealReserve = { BaseValue = 50 }`
  - `RarityLevels.*.Multiplier`
- Stronger version example:
  - Reserve `50 -> 80`

### `DeathVengeanceKeepsake` (line ~371)

- Buff keys:
  - `AddOutgoingDamageModifiers.VengeanceMultiplier.BaseValue = 1.20`
  - `RarityLevels.*.Multiplier`
- Stronger version example:
  - `1.20 -> 1.35`

### `LowHealthCritKeepsake` (line ~474)

- Buff keys:
  - `AddOutgoingCritModifiers.ActiveTraitChance = { BaseValue = 0.20 }`
  - `CapMaxHealth = 30` (this is a penalty cap; raise it to reduce downside)
  - `RarityLevels.*.Multiplier`
- Stronger version example:
  - Crit chance `0.20 -> 0.30`
  - HP cap `30 -> 40` (safer)

### `SpellTalentKeepsake` (line ~574)

- Buff keys:
  - `TalentPointCount = { BaseValue = 3 }`
  - `AcquireFunctionArgs.Count = { BaseValue = 3 }`
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Uses `KeepsakeAcquireSpellDrop` in `KeepsakeLogic.lua` and additional level-up handling in `AdvanceKeepsake`.
- Stronger version example:
  - `TalentPointCount` and `Count` to `4`

### `BonusMoneyKeepsake` (line ~678)

- Buff keys:
  - `BonusMoney = { BaseValue = 100 }`
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Reward payout is consumed in `KeepsakeLogic.lua` when equipped.
- Stronger version example:
  - `100 -> 175`

### `BossPreDamageKeepsake` (line ~765)

- Buff keys:
  - `EncounterPreDamage.PreDamage = { BaseValue = 0.05 }`
  - `AddIncomingDamageModifiers.BossDamageMultiplier = 0.90` (lower = better defense)
  - `RarityLevels.*.Multiplier`
- Stronger version example:
  - Pre-damage `0.05 -> 0.08`
  - Boss multiplier `0.90 -> 0.80`

### `ManaOverTimeRefundKeepsake` (line ~870)

- Buff keys:
  - `AcquireFunctionArgs.Amount = { BaseValue = 50 }`
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Refund spending/expiration handled by `CheckOverTimeManaRefund` in `KeepsakeLogic.lua`.
- Stronger version example:
  - `Amount 50 -> 80`

### `BossMetaUpgradeKeepsake` (line ~968)

- Buff keys:
  - `PostBossCardRarity = { BaseValue = 1 }`
  - `RemainingUses = 1`
  - `RarityLevels.*.Multiplier`
- Stronger version example:
  - `PostBossCardRarity 1 -> 2`
  - `RemainingUses 1 -> 2`

### `FountainRarityKeepsake` (line ~1054)

- Buff keys:
  - `FountainHealFractionBonus = 0.2`
  - `FountainRarity.NumTraits = 1`
  - `FountainRarity.TargetRarity = { BaseValue = 2 }`
  - `FountainRarity.MaxRarity = 1` (ceiling field)
- Stronger version example:
  - Heal bonus `0.2 -> 0.35`
  - `NumTraits 1 -> 2`
  - `TargetRarity 2 -> 3`

### `ArmorGainKeepsake` (line ~1199)

- Buff keys:
  - `DoorArmor = { BaseValue = 2 }`
  - `SetupFunction.Args.BaseAmount = 30`
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Armor setup/removal tied to `CostumeArmor` flow in `KeepsakeLogic.lua`.
- Stronger version example:
  - `DoorArmor 2 -> 4`
  - `BaseAmount 30 -> 50`

### `TempHammerKeepsake` (line ~1304)

- Buff keys:
  - `Duration = { BaseValue = 10 }`
- Runtime note:
  - Hammer grant is `GiveDurationHammer` in `PowersLogic.lua`; duration is assigned to `RemainingUses`.
- Stronger version example:
  - `Duration 10 -> 16`

### `DecayingBoostKeepsake` (line ~1383)

- Buff keys:
  - `InitialKeepsakeDamageBonus = { BaseValue = 2 }`
  - `DecayRate = 0.05` (lower = buff lasts longer)
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Decays each room in `RoomLogic.lua` (`CurrentKeepsakeDamageBonus = Current - DecayRate`).
- Stronger version example:
  - Initial bonus `2 -> 2.5`
  - Decay `0.05 -> 0.03`

### `DamagedDamageBoostKeepsake` (line ~1488)

- Buff keys:
  - `ExRunDamagedMultiplier = { BaseValue = 1.20 }`
  - `ExRunDamagedThreshold = 250` (lower threshold = easier activation)
  - `RarityLevels.*.Multiplier`
- Stronger version example:
  - Multiplier `1.20 -> 1.35`
  - Threshold `250 -> 180`

### `EscalatingKeepsake` (line ~1592)

- Buff keys:
  - `EscalatingKeepsakeGrowthPerRoom = { BaseValue = 0.005 }`
  - `EscalatingKeepsakeValue = 1.0` (starting value)
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Growth added per room in `RoomLogic.lua`.
- Stronger version example:
  - Growth `0.005 -> 0.010`
  - Start `1.0 -> 1.05`

### `TimedBuffKeepsake` (line ~1701)

- Buff keys:
  - `StartingTime = { BaseValue = 200 }`
  - `SetupFunction.Args.Multiplier = 0.8` (negative delta style field)
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Timer starts via `StartHermesKeepsakeTimer` in `PowersLogic.lua`.
- Stronger version example:
  - Duration `200 -> 300`
  - `Multiplier 0.8 -> 0.7` (stronger effect)

### `UnpickedBoonKeepsake` (line ~1805)

- Buff keys:
  - `DoubleBoonChance.BaseValue = 0.25`
  - `Uses = 1`
  - `RarityLevels.*.Multiplier`
- Stronger version example:
  - Chance `0.25 -> 0.40`
  - Uses `1 -> 2`

### `RandomBlessingKeepsake` (line ~1911)

- Buff keys:
  - `AcquireFunctionArgs.BlessingRarity = { BaseValue = 1 }`
  - `RoomsPerUpgrade.Amount = 8` (lower = more frequent upgrades)
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Blessing grant and behavior handled by `ChaosBlessingBonus` in `PowersLogic.lua`.
- Stronger version example:
  - Blessing rarity `1 -> 2`
  - Rooms per upgrade `8 -> 5`

### `SkipEncounterKeepsake` (line ~2021)

- Buff keys:
  - `AcquireFunctionArgs.SkipEncounterChance = 0.37`
  - `AcquireFunctionArgs.RemainingUses = { BaseValue = 1 }`
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Runtime trait is spawned by `DionysusSkipTrait` in `PowersLogic.lua`.
- Stronger version example:
  - Chance `0.37 -> 0.55`
  - Uses `1 -> 2`

### `AthenaEncounterKeepsake` (line ~2163)

- Buff keys:
  - `UniqueEncounterArgs.EncounterThreadedFunctions.Args.RarityLevelBonus = { BaseValue = 1 }`
  - `RemainingUses = 1`
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Trigger path uses skip-encounter checks in `RoomLogic.lua`.
- Stronger version example:
  - Rarity bonus `1 -> 2`
  - Uses `1 -> 2`

### `RarifyKeepsake` (line ~2306)

- Buff keys:
  - `RarityUpgradeData.Uses = { BaseValue = 2 }`
  - `RarityUpgradeData.MaxRarity = 3`
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - In `AdvanceKeepsake`, uses get hard-incremented by `+2` on keepsake level-up.
- Stronger version example:
  - Uses `2 -> 3`
  - Max rarity `3 -> 4` (if your rarity enum supports it in your build)

### `HadesAndPersephoneKeepsake` (line ~2404)

- Buff keys:
  - `FatedBoonLevelBonus = { BaseValue = 1 }`
  - `RarityLevels.*.Multiplier`
- Runtime note:
  - Behavior driven by `GiveRandomHadesBoonAndBoostBoons` acquire function.
- Stronger version example:
  - `FatedBoonLevelBonus 1 -> 2`

### `GoldifyKeepsake` (line ~2507)

- Buff keys:
  - `BoonConversionUses = { BaseValue = 2 }`
  - `BoostedBoonValueAddition = 100`
  - `RarityLevels.*.Multiplier`
- Runtime notes:
  - Uses are spent in `GiftLogic.lua` when converting rewards.
  - `AdvanceKeepsake` in `KeepsakeLogic.lua` adds `+1` conversion use on level-up.
- Stronger version example:
  - Uses `2 -> 3`
  - Value addition `100 -> 150`

### Force-God Boon Keepsakes (same structure)

- Traits:
  - `ForceHephaestusBoonKeepsake` (~2588)
  - `ForceZeusBoonKeepsake` (~2674)
  - `ForceDemeterBoonKeepsake` (~2761)
  - `ForceAphroditeBoonKeepsake` (~2847)
  - `ForcePoseidonBoonKeepsake` (~2934)
  - `ForceApolloBoonKeepsake` (~3020)
  - `ForceHestiaBoonKeepsake` (~3106)
  - `ForceAresBoonKeepsake` (~3192)
  - `ForceHeraBoonKeepsake` (~3278)
- Buff keys in each:
  - `RarityUpgradeData.Uses`
  - `RarityUpgradeData.MaxRarity = { BaseValue = 1 }`
  - `Uses`
  - Inherited `RarityLevels.*.Multiplier` via `BaseBoonUpgradeKeepsake`
- Stronger version example:
  - `Uses 1 -> 2`
  - `MaxRarity BaseValue 1 -> 2`

## 4. Quick safe tuning presets

If you want a fast, stable power increase across all keepsakes:

1. Increase each main `BaseValue` field by `+25%` to `+40%`.
2. Set each `Rare/Epic/Heroic` multiplier about `+0.25` higher than current.
3. For chance keepsakes (`DoubleBoonChance`, `SkipEncounterChance`), cap at `0.60`.
4. For decay keepsakes, reduce decay gradually (`0.05 -> 0.04` first, then test).

## 5. Validation checklist after edits

1. Equip each edited keepsake once and verify tooltip numbers update.
2. Trigger at least one effect activation path (boss, fountain, boon room, etc.).
3. Check expiry/use counters (`Uses`, `RemainingUses`) decrement as expected.
4. Re-open keepsake rack and confirm rank scaling still displays correctly.

## 6. Common pitfalls

1. Editing only tooltip extraction fields does not buff gameplay.
2. Some keepsakes spawn runtime traits (`AcquireFunctionName`) that also need logic awareness.
3. Over-buffing multipliers with additive and multiplicative stacking together can spike damage unexpectedly.
4. `Rarify`/`Goldify` have level-up logic in `AdvanceKeepsake`; keep that in mind when changing uses.
