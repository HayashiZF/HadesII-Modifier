from __future__ import annotations


def collect_profile_state(app: object, profile: str):
    return app._collect_profile_state(profile)


def persist_ui_state(app: object):
    return app._persist_ui_state()


__all__ = ["collect_profile_state", "persist_ui_state"]
