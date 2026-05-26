from __future__ import annotations

import pytest

from hades_mod_ui.patches import (
    PatchError,
    parse_roll_order,
    validate_number_string,
    validate_positive_number_string,
    validate_probability_string,
    validate_signed_number_string,
    validate_whole_number_string,
)


def test_validate_number_string_accepts_zero_or_more() -> None:
    assert validate_number_string(" 1.25 ", "x") == "1.25"


def test_validate_number_string_rejects_negative() -> None:
    with pytest.raises(PatchError):
        validate_number_string("-1", "x")


def test_validate_signed_number_string_accepts_negative() -> None:
    assert validate_signed_number_string("-2.5", "x") == "-2.5"


def test_validate_positive_number_string_rejects_zero() -> None:
    with pytest.raises(PatchError):
        validate_positive_number_string("0", "x")


def test_validate_probability_string_range_check() -> None:
    assert validate_probability_string("0.25", "x") == "0.25"
    with pytest.raises(PatchError):
        validate_probability_string("1.5", "x")


def test_validate_whole_number_string() -> None:
    assert validate_whole_number_string("42", "x") == "42"
    with pytest.raises(PatchError):
        validate_whole_number_string("4.2", "x")


def test_parse_roll_order() -> None:
    assert parse_roll_order("Common, Rare, Epic", "roll") == ["Common", "Rare", "Epic"]
    with pytest.raises(PatchError):
        parse_roll_order("", "roll")
