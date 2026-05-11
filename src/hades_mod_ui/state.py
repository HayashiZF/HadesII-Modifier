from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

BOON_MULTIPLIER_GOD_SOURCES: tuple[tuple[str, str, str], ...] = (
    ("aphrodite", "Aphrodite", "TraitData_Aphrodite.lua"),
    ("apollo", "Apollo", "TraitData_Apollo.lua"),
    ("ares", "Ares", "TraitData_Ares.lua"),
    ("artemis", "Artemis", "TraitData_Artemis.lua"),
    ("athena", "Athena", "TraitData_Athena.lua"),
    ("demeter", "Demeter", "TraitData_Demeter.lua"),
    ("dionysus", "Dionysus", "TraitData_Dionysus.lua"),
    ("hephaestus", "Hephaestus", "TraitData_Hephaestus.lua"),
    ("hera", "Hera", "TraitData_Hera.lua"),
    ("hermes", "Hermes", "TraitData_Hermes.lua"),
    ("hestia", "Hestia", "TraitData_Hestia.lua"),
    ("poseidon", "Poseidon", "TraitData_Poseidon.lua"),
    ("zeus", "Zeus", "TraitData_Zeus.lua"),
)

BOON_MULTIPLIER_GOD_FILE_MAP: dict[str, str] = {
    key: file_name for key, _title, file_name in BOON_MULTIPLIER_GOD_SOURCES
}

DEFAULT_BOON_MULTIPLIER_STATE: dict[str, Any] = {
    "gods": {
        key: {
            "enabled": False,
            "boons": {},
        }
        for key, _title, _file_name in BOON_MULTIPLIER_GOD_SOURCES
    }
}

DEFAULT_UI_LAYOUT_STATE: dict[str, Any] = {
    "panes": {
        "main_vertical": None,
        "bottom_horizontal": None,
    }
}

DEFAULT_INITIAL_STATS_STATE: dict[str, Any] = {
    "enabled": False,
    "max_health": "30",
    "max_mana": "50",
    "starting_money": "0",
}


DEFAULT_RARITY_EDITOR_STATE: dict[str, dict[str, Any]] = {
    "normal_gods": {
        "enabled": False,
        "values": {
            "Rare": "0.10",
            "Epic": "0.05",
            "Duo": "0.12",
            "Legendary": "0.10",
        },
    },
    "hermes": {
        "enabled": False,
        "values": {
            "Rare": "0.06",
            "Epic": "0.03",
            "Legendary": "0.01",
        },
    },
    "chaos": {
        "enabled": False,
        "values": {
            "Rare": "0.40",
            "Epic": "0.10",
            "Duo": "0",
            "Legendary": "0.05",
        },
    },
    "artemis": {
        "enabled": False,
        "values": {
            "Rare": "0.0",
            "Epic": "0.0",
        },
        "roll_order": "Common, Rare, Epic",
    },
    "hades": {
        "enabled": False,
        "values": {
            "Common": "1",
            "Legendary": "0.1",
        },
        "roll_order": "Common, Heroic",
    },
    "icarus": {
        "enabled": False,
        "values": {
            "Rare": "0.05",
            "Epic": "0.01",
        },
        "roll_order": "Common, Rare, Epic",
    },
}

WEAPON_DAMAGE_WEAPONS: tuple[str, ...] = (
    "WeaponStaffSwing",
    "WeaponDagger",
    "WeaponAxe",
    "WeaponTorch",
    "WeaponLob",
    "WeaponSuit",
)

DEFAULT_WEAPON_DAMAGE_STATE: dict[str, dict[str, Any]] = {
    weapon_name: {
        "enabled": False,
        "value": "0",
    }
    for weapon_name in WEAPON_DAMAGE_WEAPONS
}

REWARD_EDITOR_SECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Money",
        (
            "RoomMoneyDrop",
            "RoomMoneyBigDrop",
            "RoomMoneyTripleDrop",
            "RoomMoneySmallDrop",
            "RoomMoneyTinyDrop",
        ),
    ),
    (
        "Health",
        (
            "MaxHealthDrop",
            "MaxHealthDropSmall",
            "MaxHealthDropBig",
        ),
    ),
    (
        "Mana",
        (
            "MaxManaDrop",
            "MaxManaDropSmall",
            "MaxManaDropBig",
        ),
    ),
)

REWARD_EDITOR_ORDER: tuple[str, ...] = tuple(
    reward_name
    for _section_title, reward_names in REWARD_EDITOR_SECTIONS
    for reward_name in reward_names
)

REWARD_EDITOR_ENTRIES: dict[str, dict[str, str]] = {
    "RoomMoneyDrop": {
        "amount_field": "DropMoney",
        "default_value": "100",
        "resource_cost_money": "100",
    },
    "RoomMoneyBigDrop": {
        "amount_field": "DropMoney",
        "default_value": "200",
        "resource_cost_money": "200",
    },
    "RoomMoneyTripleDrop": {
        "amount_field": "DropMoney",
        "default_value": "300",
        "resource_cost_money": "300",
    },
    "RoomMoneySmallDrop": {
        "amount_field": "DropMoney",
        "default_value": "50",
        "resource_cost_money": "50",
    },
    "RoomMoneyTinyDrop": {
        "amount_field": "DropMoney",
        "default_value": "20",
        "resource_cost_money": "20",
    },
    "MaxHealthDrop": {
        "amount_field": "AddMaxHealth",
        "default_value": "25",
        "resource_cost_money": "125",
    },
    "MaxHealthDropSmall": {
        "amount_field": "AddMaxHealth",
        "default_value": "5",
    },
    "MaxHealthDropBig": {
        "amount_field": "AddMaxHealth",
        "default_value": "50",
        "resource_cost_money": "250",
    },
    "MaxManaDrop": {
        "amount_field": "AddMaxMana",
        "default_value": "30",
        "resource_cost_money": "100",
    },
    "MaxManaDropSmall": {
        "amount_field": "AddMaxMana",
        "default_value": "10",
    },
    "MaxManaDropBig": {
        "amount_field": "AddMaxMana",
        "default_value": "60",
        "resource_cost_money": "200",
    },
}

DEFAULT_REWARD_EDITOR_STATE: dict[str, dict[str, Any]] = {
    reward_name: {
        **(
            {
                "resource_cost_money": reward_meta["resource_cost_money"],
            }
            if "resource_cost_money" in reward_meta
            else {}
        ),
        "enabled": False,
        "show_advanced": False,
        "value": reward_meta["default_value"],
    }
    for reward_name, reward_meta in REWARD_EDITOR_ENTRIES.items()
}

KEEPSAKE_EDITOR_CONFIG: dict[str, dict[str, Any]] = {
    "BlockDeathKeepsake": {
        "title": "BlockDeathKeepsake",
        "fields": {
            "block_death_health": {
                "label": "BlockDeathHealth.BaseValue",
                "path": "BlockDeathHealth.BaseValue",
                "input_type": "int",
                "default": "30",
                "advanced": False,
            },
            "block_death_timer": {
                "label": "BlockDeathTimer",
                "path": "BlockDeathTimer",
                "input_type": "int",
                "default": "10",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
        },
    },
    "ReincarnationKeepsake": {
        "title": "ReincarnationKeepsake",
        "fields": {
            "heal_amount": {
                "label": "KeepsakeLastStandHealAmount.BaseValue",
                "path": "KeepsakeLastStandHealAmount.BaseValue",
                "input_type": "int",
                "default": "51",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.4901960784",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.9803921569",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.9607843137",
                "advanced": True,
            },
        },
    },
    "DoorHealReserveKeepsake": {
        "title": "DoorHealReserveKeepsake",
        "fields": {
            "door_heal_reserve": {
                "label": "DoorHealReserve.BaseValue",
                "path": "DoorHealReserve.BaseValue",
                "input_type": "int",
                "default": "50",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
        },
    },
    "DeathVengeanceKeepsake": {
        "title": "DeathVengeanceKeepsake",
        "fields": {
            "vengeance_multiplier": {
                "label": "AddOutgoingDamageModifiers.VengeanceMultiplier.BaseValue",
                "path": "AddOutgoingDamageModifiers.VengeanceMultiplier.BaseValue",
                "input_type": "positive_multiplier",
                "default": "1.20",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.25",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
        },
    },
    "LowHealthCritKeepsake": {
        "title": "LowHealthCritKeepsake",
        "fields": {
            "active_trait_chance": {
                "label": "AddOutgoingCritModifiers.ActiveTraitChance.BaseValue",
                "path": "AddOutgoingCritModifiers.ActiveTraitChance.BaseValue",
                "input_type": "chance_0_1",
                "default": "0.20",
                "advanced": False,
            },
            "cap_max_health": {
                "label": "CapMaxHealth",
                "path": "CapMaxHealth",
                "input_type": "int",
                "default": "30",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.25",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.5",
                "advanced": True,
            },
        },
    },
    "SpellTalentKeepsake": {
        "title": "SpellTalentKeepsake",
        "fields": {
            "talent_point_count": {
                "label": "TalentPointCount.BaseValue",
                "path": "TalentPointCount.BaseValue",
                "input_type": "int",
                "default": "3",
                "advanced": False,
            },
            "acquire_count": {
                "label": "AcquireFunctionArgs.Count.BaseValue",
                "path": "AcquireFunctionArgs.Count.BaseValue",
                "input_type": "int",
                "default": "3",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.3333333333",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.6666666667",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.3333333333",
                "advanced": True,
            },
        },
    },
    "BonusMoneyKeepsake": {
        "title": "BonusMoneyKeepsake",
        "fields": {
            "bonus_money": {
                "label": "BonusMoney.BaseValue",
                "path": "BonusMoney.BaseValue",
                "input_type": "int",
                "default": "100",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.25",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
        },
    },
    "BossPreDamageKeepsake": {
        "title": "BossPreDamageKeepsake",
        "fields": {
            "pre_damage": {
                "label": "EncounterPreDamage.PreDamage.BaseValue",
                "path": "EncounterPreDamage.PreDamage.BaseValue",
                "input_type": "chance_0_1",
                "default": "0.05",
                "advanced": False,
            },
            "boss_damage_multiplier": {
                "label": "AddIncomingDamageModifiers.BossDamageMultiplier",
                "path": "AddIncomingDamageModifiers.BossDamageMultiplier",
                "input_type": "positive_multiplier",
                "default": "0.90",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "5.0",
                "advanced": True,
            },
        },
    },
    "ManaOverTimeRefundKeepsake": {
        "title": "ManaOverTimeRefundKeepsake",
        "fields": {
            "amount": {
                "label": "AcquireFunctionArgs.Amount.BaseValue",
                "path": "AcquireFunctionArgs.Amount.BaseValue",
                "input_type": "int",
                "default": "50",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
        },
    },
    "BossMetaUpgradeKeepsake": {
        "title": "BossMetaUpgradeKeepsake",
        "fields": {
            "post_boss_card_rarity": {
                "label": "PostBossCardRarity.BaseValue",
                "path": "PostBossCardRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "remaining_uses": {
                "label": "RemainingUses",
                "path": "RemainingUses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "4.0",
                "advanced": True,
            },
        },
    },
    "FountainRarityKeepsake": {
        "title": "FountainRarityKeepsake",
        "fields": {
            "fountain_heal_fraction_bonus": {
                "label": "FountainHealFractionBonus",
                "path": "FountainHealFractionBonus",
                "input_type": "float",
                "default": "0.2",
                "advanced": False,
            },
            "fountain_num_traits": {
                "label": "FountainRarity.NumTraits",
                "path": "FountainRarity.NumTraits",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "fountain_target_rarity": {
                "label": "FountainRarity.TargetRarity.BaseValue",
                "path": "FountainRarity.TargetRarity.BaseValue",
                "input_type": "int",
                "default": "2",
                "advanced": False,
            },
            "fountain_max_rarity": {
                "label": "FountainRarity.MaxRarity",
                "path": "FountainRarity.MaxRarity",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": True,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
        },
    },
    "ArmorGainKeepsake": {
        "title": "ArmorGainKeepsake",
        "fields": {
            "door_armor": {
                "label": "DoorArmor.BaseValue",
                "path": "DoorArmor.BaseValue",
                "input_type": "int",
                "default": "2",
                "advanced": False,
            },
            "base_amount": {
                "label": "SetupFunction.Args.BaseAmount",
                "path": "SetupFunction.Args.BaseAmount",
                "input_type": "int",
                "default": "30",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
        },
    },
    "TempHammerKeepsake": {
        "title": "TempHammerKeepsake",
        "fields": {
            "duration": {
                "label": "Duration.BaseValue",
                "path": "Duration.BaseValue",
                "input_type": "int",
                "default": "10",
                "advanced": False,
            },
        },
    },
    "DecayingBoostKeepsake": {
        "title": "DecayingBoostKeepsake",
        "fields": {
            "initial_bonus": {
                "label": "InitialKeepsakeDamageBonus.BaseValue",
                "path": "InitialKeepsakeDamageBonus.BaseValue",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": False,
            },
            "decay_rate": {
                "label": "DecayRate",
                "path": "DecayRate",
                "input_type": "chance_0_1",
                "default": "0.05",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "0.3",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "0.4",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "0.5",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "0.7",
                "advanced": True,
            },
        },
    },
    "DamagedDamageBoostKeepsake": {
        "title": "DamagedDamageBoostKeepsake",
        "fields": {
            "damaged_multiplier": {
                "label": "AddOutgoingDamageModifiers.ExRunDamagedMultiplier.BaseValue",
                "path": "AddOutgoingDamageModifiers.ExRunDamagedMultiplier.BaseValue",
                "input_type": "positive_multiplier",
                "default": "1.20",
                "advanced": False,
            },
            "damaged_threshold": {
                "label": "AddOutgoingDamageModifiers.ExRunDamagedThreshold",
                "path": "AddOutgoingDamageModifiers.ExRunDamagedThreshold",
                "input_type": "int",
                "default": "250",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
        },
    },
    "EscalatingKeepsake": {
        "title": "EscalatingKeepsake",
        "fields": {
            "growth_per_room": {
                "label": "EscalatingKeepsakeGrowthPerRoom.BaseValue",
                "path": "EscalatingKeepsakeGrowthPerRoom.BaseValue",
                "input_type": "float",
                "default": "0.005",
                "advanced": False,
            },
            "start_value": {
                "label": "EscalatingKeepsakeValue",
                "path": "EscalatingKeepsakeValue",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
        },
    },
    "TimedBuffKeepsake": {
        "title": "TimedBuffKeepsake",
        "fields": {
            "starting_time": {
                "label": "StartingTime.BaseValue",
                "path": "StartingTime.BaseValue",
                "input_type": "int",
                "default": "200",
                "advanced": False,
            },
            "speed_multiplier": {
                "label": "SetupFunction.Args.Multiplier",
                "path": "SetupFunction.Args.Multiplier",
                "input_type": "positive_multiplier",
                "default": "0.8",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.25",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
        },
    },
    "UnpickedBoonKeepsake": {
        "title": "UnpickedBoonKeepsake",
        "fields": {
            "double_boon_chance": {
                "label": "DoubleBoonChance.BaseValue",
                "path": "DoubleBoonChance.BaseValue",
                "input_type": "chance_0_1",
                "default": "0.25",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "4.0",
                "advanced": True,
            },
        },
    },
    "RandomBlessingKeepsake": {
        "title": "RandomBlessingKeepsake",
        "fields": {
            "blessing_rarity": {
                "label": "AcquireFunctionArgs.BlessingRarity.BaseValue",
                "path": "AcquireFunctionArgs.BlessingRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "rooms_per_upgrade": {
                "label": "RoomsPerUpgrade.Amount",
                "path": "RoomsPerUpgrade.Amount",
                "input_type": "int",
                "default": "8",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "4.0",
                "advanced": True,
            },
        },
    },
    "SkipEncounterKeepsake": {
        "title": "SkipEncounterKeepsake",
        "fields": {
            "skip_encounter_chance": {
                "label": "AcquireFunctionArgs.SkipEncounterChance",
                "path": "AcquireFunctionArgs.SkipEncounterChance",
                "input_type": "chance_0_1",
                "default": "0.37",
                "advanced": False,
            },
            "remaining_uses": {
                "label": "AcquireFunctionArgs.RemainingUses.BaseValue",
                "path": "AcquireFunctionArgs.RemainingUses.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "4.0",
                "advanced": True,
            },
        },
    },
    "AthenaEncounterKeepsake": {
        "title": "AthenaEncounterKeepsake",
        "fields": {
            "rarity_level_bonus": {
                "label": "UniqueEncounterArgs.EncounterThreadedFunctions.Args.RarityLevelBonus.BaseValue",
                "path": "UniqueEncounterArgs.EncounterThreadedFunctions.Args.RarityLevelBonus.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "remaining_uses": {
                "label": "RemainingUses",
                "path": "RemainingUses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "4.0",
                "advanced": True,
            },
        },
    },
    "RarifyKeepsake": {
        "title": "RarifyKeepsake",
        "fields": {
            "rarity_uses": {
                "label": "RarityUpgradeData.Uses.BaseValue",
                "path": "RarityUpgradeData.Uses.BaseValue",
                "input_type": "int",
                "default": "2",
                "advanced": False,
            },
            "max_rarity": {
                "label": "RarityUpgradeData.MaxRarity",
                "path": "RarityUpgradeData.MaxRarity",
                "input_type": "int",
                "default": "3",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "4.0",
                "advanced": True,
            },
        },
    },
    "HadesAndPersephoneKeepsake": {
        "title": "HadesAndPersephoneKeepsake",
        "fields": {
            "fated_boon_level_bonus": {
                "label": "FatedBoonLevelBonus.BaseValue",
                "path": "FatedBoonLevelBonus.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "3.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "4.0",
                "advanced": True,
            },
        },
    },
    "GoldifyKeepsake": {
        "title": "GoldifyKeepsake",
        "fields": {
            "boon_conversion_uses": {
                "label": "BoonConversionUses.BaseValue",
                "path": "BoonConversionUses.BaseValue",
                "input_type": "int",
                "default": "2",
                "advanced": False,
            },
            "boosted_boon_value_addition": {
                "label": "BoostedBoonValueAddition",
                "path": "BoostedBoonValueAddition",
                "input_type": "int",
                "default": "100",
                "advanced": False,
            },
            "multiplier_common": {
                "label": "RarityLevels.Common.Multiplier",
                "path": "RarityLevels.Common.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.0",
                "advanced": True,
            },
            "multiplier_rare": {
                "label": "RarityLevels.Rare.Multiplier",
                "path": "RarityLevels.Rare.Multiplier",
                "input_type": "positive_multiplier",
                "default": "1.5",
                "advanced": True,
            },
            "multiplier_epic": {
                "label": "RarityLevels.Epic.Multiplier",
                "path": "RarityLevels.Epic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.0",
                "advanced": True,
            },
            "multiplier_heroic": {
                "label": "RarityLevels.Heroic.Multiplier",
                "path": "RarityLevels.Heroic.Multiplier",
                "input_type": "positive_multiplier",
                "default": "2.5",
                "advanced": True,
            },
        },
    },
    "ForceHephaestusBoonKeepsake": {
        "title": "ForceHephaestusBoonKeepsake",
        "fields": {
            "rarity_uses": {
                "label": "RarityUpgradeData.Uses",
                "path": "RarityUpgradeData.Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "max_rarity": {
                "label": "RarityUpgradeData.MaxRarity.BaseValue",
                "path": "RarityUpgradeData.MaxRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
        },
    },
    "ForceZeusBoonKeepsake": {
        "title": "ForceZeusBoonKeepsake",
        "fields": {
            "rarity_uses": {
                "label": "RarityUpgradeData.Uses",
                "path": "RarityUpgradeData.Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "max_rarity": {
                "label": "RarityUpgradeData.MaxRarity.BaseValue",
                "path": "RarityUpgradeData.MaxRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
        },
    },
    "ForceDemeterBoonKeepsake": {
        "title": "ForceDemeterBoonKeepsake",
        "fields": {
            "rarity_uses": {
                "label": "RarityUpgradeData.Uses",
                "path": "RarityUpgradeData.Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "max_rarity": {
                "label": "RarityUpgradeData.MaxRarity.BaseValue",
                "path": "RarityUpgradeData.MaxRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
        },
    },
    "ForceAphroditeBoonKeepsake": {
        "title": "ForceAphroditeBoonKeepsake",
        "fields": {
            "rarity_uses": {
                "label": "RarityUpgradeData.Uses",
                "path": "RarityUpgradeData.Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "max_rarity": {
                "label": "RarityUpgradeData.MaxRarity.BaseValue",
                "path": "RarityUpgradeData.MaxRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
        },
    },
    "ForcePoseidonBoonKeepsake": {
        "title": "ForcePoseidonBoonKeepsake",
        "fields": {
            "rarity_uses": {
                "label": "RarityUpgradeData.Uses",
                "path": "RarityUpgradeData.Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "max_rarity": {
                "label": "RarityUpgradeData.MaxRarity.BaseValue",
                "path": "RarityUpgradeData.MaxRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
        },
    },
    "ForceApolloBoonKeepsake": {
        "title": "ForceApolloBoonKeepsake",
        "fields": {
            "rarity_uses": {
                "label": "RarityUpgradeData.Uses",
                "path": "RarityUpgradeData.Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "max_rarity": {
                "label": "RarityUpgradeData.MaxRarity.BaseValue",
                "path": "RarityUpgradeData.MaxRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
        },
    },
    "ForceHestiaBoonKeepsake": {
        "title": "ForceHestiaBoonKeepsake",
        "fields": {
            "rarity_uses": {
                "label": "RarityUpgradeData.Uses",
                "path": "RarityUpgradeData.Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "max_rarity": {
                "label": "RarityUpgradeData.MaxRarity.BaseValue",
                "path": "RarityUpgradeData.MaxRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
        },
    },
    "ForceAresBoonKeepsake": {
        "title": "ForceAresBoonKeepsake",
        "fields": {
            "rarity_uses": {
                "label": "RarityUpgradeData.Uses",
                "path": "RarityUpgradeData.Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "max_rarity": {
                "label": "RarityUpgradeData.MaxRarity.BaseValue",
                "path": "RarityUpgradeData.MaxRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
        },
    },
    "ForceHeraBoonKeepsake": {
        "title": "ForceHeraBoonKeepsake",
        "fields": {
            "rarity_uses": {
                "label": "RarityUpgradeData.Uses",
                "path": "RarityUpgradeData.Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "max_rarity": {
                "label": "RarityUpgradeData.MaxRarity.BaseValue",
                "path": "RarityUpgradeData.MaxRarity.BaseValue",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
            "uses": {
                "label": "Uses",
                "path": "Uses",
                "input_type": "int",
                "default": "1",
                "advanced": False,
            },
        },
    },
}

KEEPSAKE_EDITOR_ORDER: tuple[str, ...] = tuple(KEEPSAKE_EDITOR_CONFIG.keys())

DEFAULT_KEEPSAKE_EDITOR_STATE: dict[str, dict[str, Any]] = {
    keepsake_name: {
        "enabled": False,
        "show_advanced": False,
        "fields": {
            field_name: str(field_meta["default"])
            for field_name, field_meta in keepsake_meta["fields"].items()
        },
    }
    for keepsake_name, keepsake_meta in KEEPSAKE_EDITOR_CONFIG.items()
}

DEFAULT_STATE: dict[str, Any] = {
    "ui_language": "en",
    "ui_layout": DEFAULT_UI_LAYOUT_STATE,
    "known_backups": [],
    "generated_files": [],
    "last_apply": None,
    "last_restore": None,
    "profiles": {
        "epic_preset": {
            "scope": "olympians_plus_hermes",
        },
        "initial_stats": DEFAULT_INITIAL_STATS_STATE,
        "rarity_editor": DEFAULT_RARITY_EDITOR_STATE,
        "reward_editor": DEFAULT_REWARD_EDITOR_STATE,
        "weapon_damage": DEFAULT_WEAPON_DAMAGE_STATE,
        "keepsake_editor": DEFAULT_KEEPSAKE_EDITOR_STATE,
        "boon_multiplier": DEFAULT_BOON_MULTIPLIER_STATE,
    },
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return copy.deepcopy(DEFAULT_STATE)

        with self.path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        return _deep_merge(DEFAULT_STATE, loaded)

    def save(self, state: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8", newline="") as handle:
            json.dump(state, handle, indent=2)
