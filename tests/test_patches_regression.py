from __future__ import annotations

from hades_mod_ui.patches import (
    EPIC_MARKER_START,
    apply_epic_preset,
    apply_initial_stats_hero_data_profile,
    apply_initial_stats_run_logic_profile,
)


def test_apply_epic_preset_is_idempotent() -> None:
    source = "\n".join(
        [
            "function Test()",
            "\t\tlootData.RarityChances = GetRarityChances( lootData )",
            "end",
        ]
    )
    once = apply_epic_preset(source)
    twice = apply_epic_preset(once)
    assert once == twice
    assert once.count(EPIC_MARKER_START) == 1


def test_apply_initial_stats_hero_data_profile_replaces_scalars() -> None:
    source = "MaxHealth = 30,\nMaxMana = 50,\n"
    out = apply_initial_stats_hero_data_profile(
        source,
        {"max_health": "200", "max_mana": "300", "enabled": True, "starting_money": "0"},
    )
    assert "MaxHealth = 200," in out
    assert "MaxMana = 300," in out


def test_apply_initial_stats_run_logic_profile_replaces_return() -> None:
    source = "\n".join(
        [
            "function CalculateStartingMoney()",
            "\treturn 0",
            "end",
        ]
    )
    out = apply_initial_stats_run_logic_profile(
        source,
        {"starting_money": "999", "enabled": True, "max_health": "0", "max_mana": "0"},
    )
    assert "\treturn 999" in out
