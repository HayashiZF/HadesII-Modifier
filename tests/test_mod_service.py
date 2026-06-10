from __future__ import annotations

from pathlib import Path

import pytest

from hades_mod_ui.operations import ModService, OperationError
from hades_mod_ui.patches import PatchError
from hades_mod_ui.paths import AppPaths
from hades_mod_ui.state import StateStore


def _build_paths(root: Path) -> AppPaths:
    scripts_dir = root / "Content" / "Scripts"
    workspace_dir = root / ".hades2_mod"
    return AppPaths(
        root_dir=root,
        scripts_dir=scripts_dir,
        workspace_dir=workspace_dir,
        legacy_workspace_dir=root / ".hades2_mod_ui",
        generated_scripts_dir=workspace_dir / "generated" / "Content" / "Scripts",
        originals_scripts_dir=workspace_dir / "originals" / "Content" / "Scripts",
        state_file=workspace_dir / "state.json",
        dist_dir=root / "dist",
        build_dir=root / "build",
    )


def test_get_target_files_initial_stats_enabled(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    service = ModService(paths, StateStore(paths.state_file))
    targets = service.get_target_files("initial_stats", {"enabled": True})
    assert targets == ["HeroData.lua", "RunLogic.lua"]


def test_get_target_files_weapon_damage_disabled_returns_empty(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    service = ModService(paths, StateStore(paths.state_file))
    targets = service.get_target_files(
        "weapon_damage",
        {
            "WeaponStaffSwing": {
                "flat_enabled": False,
                "multiplier_enabled": False,
                "range_enabled": False,
                "interval_enabled": False,
            },
            "WeaponDagger": {
                "flat_enabled": False,
                "multiplier_enabled": False,
                "range_enabled": False,
                "interval_enabled": False,
            },
            "WeaponAxe": {
                "flat_enabled": False,
                "multiplier_enabled": False,
                "range_enabled": False,
                "interval_enabled": False,
            },
            "WeaponTorch": {
                "flat_enabled": False,
                "multiplier_enabled": False,
                "range_enabled": False,
                "interval_enabled": False,
            },
            "WeaponLob": {
                "flat_enabled": False,
                "multiplier_enabled": False,
                "range_enabled": False,
                "interval_enabled": False,
            },
            "WeaponSuit": {
                "flat_enabled": False,
                "multiplier_enabled": False,
                "range_enabled": False,
                "interval_enabled": False,
            },
        },
    )
    assert targets == []


def test_generate_copies_requires_enabled_initial_stats(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    paths.scripts_dir.mkdir(parents=True)
    service = ModService(paths, StateStore(paths.state_file))
    with pytest.raises(OperationError):
        service.generate_copies("initial_stats", {"enabled": False}, {"profiles": {}})


def test_normalize_boon_multiplier_state_builds_defaults_from_metadata(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    service = ModService(paths, StateStore(paths.state_file))
    metadata = {
        "gods": {
            "zeus": {
                "boons": {
                    "LightningBoon": {
                        "fields": {
                            "RarityLevels.Common.Multiplier": {"default": "1.0"}
                        }
                    }
                }
            }
        }
    }
    normalized = service.normalize_boon_multiplier_state({"profiles": {}}, metadata)
    field = normalized["profiles"]["boon_multiplier"]["gods"]["zeus"]["boons"]["LightningBoon"]["fields"][
        "RarityLevels.Common.Multiplier"
    ]
    assert field["value"] == "1.0"


def test_normalize_weapon_damage_state_migrates_legacy_shape(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    service = ModService(paths, StateStore(paths.state_file))
    normalized = service.normalize_weapon_damage_state(
        {
            "profiles": {
                "weapon_damage": {
                    "WeaponStaffSwing": {
                        "enabled": True,
                        "value": "7",
                    }
                }
            }
        }
    )
    weapon = normalized["profiles"]["weapon_damage"]["WeaponStaffSwing"]
    assert weapon["flat_enabled"] is True
    assert weapon["flat_value"] == "7"
    assert weapon["multiplier_enabled"] is False
    assert weapon["range_enabled"] is False
    assert weapon["interval_enabled"] is False


def test_validate_weapon_damage_state_rejects_invalid_multiplier(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    service = ModService(paths, StateStore(paths.state_file))
    state = service.default_weapon_damage_state()
    state["WeaponStaffSwing"]["multiplier_enabled"] = True
    state["WeaponStaffSwing"]["multiplier_value"] = "0"
    with pytest.raises(PatchError):
        service._validate_weapon_damage_state(state)


def test_validate_weapon_damage_state_accepts_signed_flat_and_positive_multipliers(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    service = ModService(paths, StateStore(paths.state_file))
    state = service.default_weapon_damage_state()
    state["WeaponStaffSwing"]["flat_enabled"] = True
    state["WeaponStaffSwing"]["flat_value"] = "-2.5"
    state["WeaponStaffSwing"]["multiplier_enabled"] = True
    state["WeaponStaffSwing"]["multiplier_value"] = "1.05"
    state["WeaponStaffSwing"]["range_enabled"] = True
    state["WeaponStaffSwing"]["range_multiplier"] = "1.30"
    state["WeaponStaffSwing"]["interval_enabled"] = True
    state["WeaponStaffSwing"]["interval_multiplier"] = "0.80"
    validated = service._validate_weapon_damage_state(state)
    assert validated["WeaponStaffSwing"]["flat_value"] == "-2.5"
    assert validated["WeaponStaffSwing"]["multiplier_value"] == "1.05"


def test_validate_keepsake_editor_state_rejects_zero_thresholds(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    service = ModService(paths, StateStore(paths.state_file))
    state = service.default_keepsake_editor_state()
    state["BlockDeathKeepsake"]["enabled"] = True
    state["BlockDeathKeepsake"]["fields"]["keepsake_chamber_thresholds"] = "1, 0"
    with pytest.raises(PatchError):
        service._validate_keepsake_editor_state(state)
