from __future__ import annotations

import copy

from hades_mod_ui.state import DEFAULT_STATE, StateStore


def test_state_store_loads_defaults_when_missing(tmp_path) -> None:
    store = StateStore(tmp_path / "state.json")
    loaded = store.load()
    assert loaded["profiles"].keys() == DEFAULT_STATE["profiles"].keys()


def test_state_store_deep_merges_with_defaults(tmp_path) -> None:
    store = StateStore(tmp_path / "state.json")
    partial = {
        "ui_language": "zh",
        "profiles": {
            "initial_stats": {
                "enabled": True,
                "max_health": "77",
            }
        },
    }
    store.save(partial)
    loaded = store.load()
    assert loaded["ui_language"] == "zh"
    assert loaded["profiles"]["initial_stats"]["enabled"] is True
    assert loaded["profiles"]["initial_stats"]["max_health"] == "77"
    assert "max_mana" in loaded["profiles"]["initial_stats"]


def test_state_store_round_trip_preserves_shape(tmp_path) -> None:
    store = StateStore(tmp_path / "state.json")
    payload = copy.deepcopy(DEFAULT_STATE)
    payload["known_backups"] = ["HeroData.lua"]
    store.save(payload)
    loaded = store.load()
    assert loaded["known_backups"] == ["HeroData.lua"]
