from __future__ import annotations

from ..operations_support.mod_service import ModService


def on_generate(app: object) -> None:
    app._on_generate()


def on_backup(app: object) -> None:
    app._on_backup()


def on_apply(app: object) -> None:
    app._on_apply()


def on_restore(app: object) -> None:
    app._on_restore()


__all__ = ["on_apply", "on_backup", "on_generate", "on_restore"]
