"""Tiny loader for the US retirement-limits dataset.

This package is not published to PyPI. Copy this file, or clone the repository.
"""

from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


@lru_cache(maxsize=1)
def load_dataset(path: Optional[Path] = None) -> dict[str, Any]:
    target = Path(path) if path else DATA / "dataset.json"
    with target.open(encoding="utf-8") as f:
        return json.load(f)


def ira_limit(year: int, age: Optional[int] = None, dataset: Optional[dict] = None) -> dict:
    """Return the IRA contribution row for a calendar year.

    If age is 50 or older at year-end, include the catch-up in ``applicable_limit``.
    """
    data = dataset or load_dataset()
    row = _find_year(data["ira_contribution_limits"], year)
    catch = row["catch_up_age_50"]
    applicable = row["contribution_limit"]
    if age is not None and age >= 50 and catch is not None:
        applicable = row["total_if_age_50_or_older"]
    return {**row, "applicable_limit": applicable}


def employer_plan_limit(year: int, dataset: Optional[dict] = None) -> dict:
    data = dataset or load_dataset()
    return _find_year(data["employer_plan_limits"], year)


def simple_plan_limit(year: int, dataset: Optional[dict] = None) -> dict:
    data = dataset or load_dataset()
    return _find_year(data["simple_plan_limits"], year)


def rmd_denominator(age: int, dataset: Optional[dict] = None) -> float:
    """Uniform Lifetime Table denominator for the age attained in the distribution year."""
    data = dataset or load_dataset()
    if age >= 120:
        row = next(r for r in data["rmd_uniform_lifetime"]["rows"] if r["age_is_120_or_older"])
        return float(row["applicable_denominator"])
    for row in data["rmd_uniform_lifetime"]["rows"]:
        if row["age"] == age and not row["age_is_120_or_older"]:
            return float(row["applicable_denominator"])
    raise KeyError(f"No Uniform Lifetime denominator for age {age}")


def rmd_amount(account_balance: float, age: int, dataset: Optional[dict] = None) -> float:
    """Prior year-end balance divided by the Uniform Lifetime denominator."""
    if account_balance < 0:
        raise ValueError("account_balance must be >= 0")
    return account_balance / rmd_denominator(age, dataset)


def metal_fineness(metal: str, dataset: Optional[dict] = None) -> dict:
    data = dataset or load_dataset()
    key = metal.strip().lower()
    for row in data["ira_eligible_metals"]["contract_market_minimum_fineness_retrieved"]:
        if row["metal"] == key:
            return row
    raise KeyError(f"No contract-market fineness row for metal {metal!r}")


def iter_csv(name: str):
    path = DATA / name
    with path.open(encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f)


def _find_year(rows: list[dict], year: int) -> dict:
    for row in rows:
        if row["year"] == year:
            return row
    raise KeyError(f"No row for year {year}")
