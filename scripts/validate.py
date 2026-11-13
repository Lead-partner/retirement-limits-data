#!/usr/bin/env python3
"""Validate dataset.json against schema rules and the derived CSVs."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "src" / "python"))
from retirement_limits import (  # noqa: E402
    employer_plan_limit,
    ira_limit,
    load_dataset,
    metal_fineness,
    rmd_amount,
    rmd_denominator,
)

errors: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def main() -> int:
    dataset = load_dataset()
    meta = dataset["meta"]
    check(meta["retrieved_date"] == "2026-11-13", "unexpected retrieved_date")
    check(meta["license_data"] == "CC-BY-4.0", "data license")
    check(meta["license_code"] == "MIT", "code license")
    check("disclaimer" in meta and len(meta["disclaimer"]) > 80, "missing disclaimer")

    ira = dataset["ira_contribution_limits"]
    years = [r["year"] for r in ira]
    check(years == list(range(1997, 2027)), f"IRA years {years[0]}-{years[-1]}")
    for row in ira:
        check(isinstance(row["contribution_limit"], int) and row["contribution_limit"] > 0, f"IRA limit {row['year']}")
        check(row["sources"] and all(s.get("url") and s.get("retrieved_date") for s in row["sources"]), f"IRA sources {row['year']}")
        if row["catch_up_age_50"] is None:
            check(row["year"] <= 2001, f"unexpected missing IRA catch-up {row['year']}")
            check(row["total_if_age_50_or_older"] is None, f"total set without catch-up {row['year']}")
        else:
            check(row["total_if_age_50_or_older"] == row["contribution_limit"] + row["catch_up_age_50"], f"IRA total {row['year']}")

    # Anchors from the 13 Nov 2026 source read
    anchors = {
        1997: (2000, None),
        2002: (3000, 500),
        2005: (4000, 500),
        2006: (4000, 1000),
        2008: (5000, 1000),
        2013: (5500, 1000),
        2019: (6000, 1000),
        2023: (6500, 1000),
        2024: (7000, 1000),
        2025: (7000, 1000),
        2026: (7500, 1100),
    }
    by_year = {r["year"]: r for r in ira}
    for year, (limit, catch) in anchors.items():
        check(by_year[year]["contribution_limit"] == limit, f"IRA {year} limit")
        check(by_year[year]["catch_up_age_50"] == catch, f"IRA {year} catch-up")

    emp = {r["year"]: r for r in dataset["employer_plan_limits"]}
    check(list(emp) == list(range(1987, 2027)), "employer year range")
    emp_anchors = {
        1987: (7000, None, None, None),
        1990: (7979, None, None, None),
        2002: (11000, 1000, None, 40000),
        2022: (20500, 6500, None, 61000),
        2025: (23500, 7500, 11250, 70000),
        2026: (24500, 8000, 11250, 72000),
    }
    for year, (elective, c50, c60, add) in emp_anchors.items():
        r = emp[year]
        check(r["elective_deferral_402g"] == elective, f"402g {year}")
        check(r["catch_up_age_50_414v"] == c50, f"414v 50 {year}")
        check(r["catch_up_age_60_63_414v"] == c60, f"414v 60-63 {year}")
        check(r["annual_additions_415c"] == add, f"415c {year}")
        check(r["sources"] and r["sources"][0]["url"], f"employer sources {year}")
    check(emp[2002]["tsp_catch_up_age_50"] is None, "TSP 2002 catch-up should be null")
    check(emp[2003]["tsp_catch_up_age_50"] == 2000, "TSP 2003 catch-up")

    # 402(g) should never fall year-over-year in this official series
    prev = None
    for year in range(1987, 2027):
        val = emp[year]["elective_deferral_402g"]
        if prev is not None:
            check(val >= prev, f"402(g) dropped {year-1}->{year}: {prev}->{val}")
        prev = val

    simple = {r["year"]: r for r in dataset["simple_plan_limits"]}
    check(simple[1997]["elective_deferral"] == 6000, "SIMPLE 1997")
    check(simple[2026]["elective_deferral"] == 17000, "SIMPLE 2026")
    check(simple[2026]["catch_up_age_50_414v"] == 4000, "SIMPLE catch-up 2026")
    check(simple[2026]["catch_up_age_60_63_414v"] == 5250, "SIMPLE 60-63 2026")

    rmd_rows = dataset["rmd_uniform_lifetime"]["rows"]
    check(len(rmd_rows) == 49, f"RMD row count {len(rmd_rows)}")
    expected = {
        72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 80: 20.2, 85: 16.0,
        90: 12.2, 95: 8.9, 100: 6.4, 110: 3.5, 119: 2.3,
    }
    by_age = {r["age"]: r for r in rmd_rows if not r["age_is_120_or_older"]}
    for age, denom in expected.items():
        check(by_age[age]["applicable_denominator"] == denom, f"RMD age {age}")
    last = rmd_rows[-1]
    check(last["age_is_120_or_older"] and last["applicable_denominator"] == 2.0, "RMD 120+")
    # Denominators must strictly decline through age 119
    denoms = [r["applicable_denominator"] for r in rmd_rows if not r["age_is_120_or_older"]]
    check(all(a > b for a, b in zip(denoms, denoms[1:])), "RMD denominators not strictly declining")

    metals = {m["metal"]: m for m in dataset["ira_eligible_metals"]["contract_market_minimum_fineness_retrieved"]}
    check(metals["gold"]["minimum_fineness"] == 0.995, "gold fineness")
    check(metals["silver"]["minimum_fineness"] == 0.999, "silver fineness")
    check(metals["platinum"]["minimum_fineness"] == 0.9995, "platinum fineness")
    check(metals["palladium"]["minimum_fineness"] == 0.9995, "palladium fineness")
    for m in metals.values():
        check(m["sources"] and m["sources"][0]["url"].endswith(".pdf"), f"metal source {m['metal']}")
    statute = dataset["ira_eligible_metals"]["statute"]
    check("408(m)" in statute["citation"], "missing 408(m) citation")
    check(len(statute["named_coin_exceptions"]) == 4, "named coin exceptions")

    # CSVs must stay in sync with JSON (primary source URL + retrieved date on every row)
    def csv_rows(name: str) -> list[dict]:
        with (DATA / name).open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    ira_csv = csv_rows("ira-contribution-limits.csv")
    check(len(ira_csv) == len(ira), "IRA csv length")
    for json_row, csv_row in zip(ira, ira_csv):
        check(int(csv_row["year"]) == json_row["year"], "IRA csv year")
        check(int(csv_row["contribution_limit"]) == json_row["contribution_limit"], "IRA csv limit")
        check(csv_row["source_url"].startswith("https://"), f"IRA csv source {csv_row['year']}")
        check(csv_row["retrieved_date"] == "2026-11-13", "IRA csv date")

    emp_csv = csv_rows("employer-plan-limits.csv")
    check(len(emp_csv) == len(emp), "employer csv length")
    for csv_row in emp_csv:
        check(csv_row["source_url"].startswith("https://"), "employer csv source")
        check(csv_row["retrieved_date"] == "2026-11-13", "employer csv date")

    rmd_csv = csv_rows("rmd-uniform-lifetime.csv")
    check(len(rmd_csv) == 49, "RMD csv length")
    for csv_row in rmd_csv:
        check(csv_row["source_url"].startswith("https://"), "RMD csv source")

    # Loader smoke tests
    check(ira_limit(2026, age=49)["applicable_limit"] == 7500, "loader IRA under 50")
    check(ira_limit(2026, age=50)["applicable_limit"] == 8600, "loader IRA age 50")
    check(employer_plan_limit(2026)["elective_deferral_402g"] == 24500, "loader 402g")
    check(rmd_denominator(75) == 24.6, "loader RMD 75")
    check(abs(rmd_amount(246000, 75) - 10000) < 1e-9, "loader RMD math")
    check(metal_fineness("Gold")["minimum_fineness"] == 0.995, "loader metal")

    if errors:
        print(f"{len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("validation ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
