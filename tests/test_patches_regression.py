from __future__ import annotations

from hades_mod_ui.patches import (
    EPIC_MARKER_START,
    WEAPON_DAMAGE_MARKER_START,
    apply_epic_preset,
    apply_initial_stats_hero_data_profile,
    apply_initial_stats_run_logic_profile,
    apply_weapon_damage_profile,
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


def _weapon_profile(
    *,
    flat: bool = False,
    mult: bool = False,
    rng: bool = False,
    interval: bool = False,
) -> dict[str, dict[str, str | bool]]:
    names = (
        "WeaponStaffSwing",
        "WeaponDagger",
        "WeaponAxe",
        "WeaponTorch",
        "WeaponLob",
        "WeaponSuit",
    )
    profile: dict[str, dict[str, str | bool]] = {}
    for name in names:
        profile[name] = {
            "flat_enabled": False,
            "flat_value": "5",
            "multiplier_enabled": False,
            "multiplier_value": "1.05",
            "range_enabled": False,
            "range_multiplier": "1.30",
            "interval_enabled": False,
            "interval_multiplier": "0.80",
        }
    profile["WeaponStaffSwing"]["flat_enabled"] = flat
    profile["WeaponStaffSwing"]["multiplier_enabled"] = mult
    profile["WeaponStaffSwing"]["range_enabled"] = rng
    profile["WeaponStaffSwing"]["interval_enabled"] = interval
    return profile


def test_apply_weapon_damage_profile_flat_only() -> None:
    source = "\n".join(
        [
            "TraitSetData.DummyWeapons =",
            "{",
            "\tDummyWeaponStaff =",
            "\t{",
            "\t},",
            "\tDummyWeaponDagger =",
            "\t{",
            "\t},",
            "\tDummyWeaponAxe =",
            "\t{",
            "\t},",
            "\tDummyWeaponTorch =",
            "\t{",
            "\t},",
            "\tDummyWeaponLob =",
            "\t{",
            "\t},",
            "\tDummyWeaponSuit =",
            "\t{",
            "\t},",
            "}",
        ]
    )
    out = apply_weapon_damage_profile(source, _weapon_profile(flat=True))
    assert WEAPON_DAMAGE_MARKER_START in out
    assert "ValidBaseDamageAddition" in out
    assert "ValidWeaponMultiplier" not in out
    assert "PropertyChanges" not in out


def test_apply_weapon_damage_profile_multiplier_only() -> None:
    source = "\n".join(
        [
            "TraitSetData.DummyWeapons =",
            "{",
            "\tDummyWeaponStaff =",
            "\t{",
            "\t},",
            "\tDummyWeaponDagger =",
            "\t{",
            "\t},",
            "\tDummyWeaponAxe =",
            "\t{",
            "\t},",
            "\tDummyWeaponTorch =",
            "\t{",
            "\t},",
            "\tDummyWeaponLob =",
            "\t{",
            "\t},",
            "\tDummyWeaponSuit =",
            "\t{",
            "\t},",
            "}",
        ]
    )
    out = apply_weapon_damage_profile(source, _weapon_profile(mult=True))
    assert "ValidWeaponMultiplier" in out
    assert "SourceIsMultiplier = true" in out
    assert "ValidBaseDamageAddition" not in out


def test_apply_weapon_damage_profile_range_and_interval_only() -> None:
    source = "\n".join(
        [
            "TraitSetData.DummyWeapons =",
            "{",
            "\tDummyWeaponStaff =",
            "\t{",
            "\t},",
            "\tDummyWeaponDagger =",
            "\t{",
            "\t},",
            "\tDummyWeaponAxe =",
            "\t{",
            "\t},",
            "\tDummyWeaponTorch =",
            "\t{",
            "\t},",
            "\tDummyWeaponLob =",
            "\t{",
            "\t},",
            "\tDummyWeaponSuit =",
            "\t{",
            "\t},",
            "}",
        ]
    )
    out = apply_weapon_damage_profile(source, _weapon_profile(rng=True, interval=True))
    assert 'ProjectileProperty = "Range"' in out
    assert 'WeaponProperty = "AutoLockRange"' in out
    assert 'WeaponProperty = "Cooldown"' in out
    assert "PropertyChanges" in out
    assert "ValidBaseDamageAddition" not in out


def test_apply_weapon_damage_profile_combined_and_idempotent() -> None:
    source = "\n".join(
        [
            "TraitSetData.DummyWeapons =",
            "{",
            "\tDummyWeaponStaff =",
            "\t{",
            "\t},",
            "\tDummyWeaponDagger =",
            "\t{",
            "\t},",
            "\tDummyWeaponAxe =",
            "\t{",
            "\t},",
            "\tDummyWeaponTorch =",
            "\t{",
            "\t},",
            "\tDummyWeaponLob =",
            "\t{",
            "\t},",
            "\tDummyWeaponSuit =",
            "\t{",
            "\t},",
            "}",
        ]
    )
    profile = _weapon_profile(flat=True, mult=True, rng=True, interval=True)
    once = apply_weapon_damage_profile(source, profile)
    twice = apply_weapon_damage_profile(once, profile)
    assert once == twice
    assert once.count(WEAPON_DAMAGE_MARKER_START) == 1
