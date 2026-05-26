from __future__ import annotations


def refresh_preview(app: object) -> None:
    app._refresh_preview()


def append_log(app: object, message: str) -> None:
    app._append_log(message)


__all__ = ["append_log", "refresh_preview"]
