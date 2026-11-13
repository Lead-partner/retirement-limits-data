#!/usr/bin/env python3
"""Build canonical dataset.json and derived CSVs from sourced official figures.

Every dollar amount in this file was read from a primary source on 2026-11-13
(Europe/Oslo). Do not add a figure here without a source URL.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RETRIEVED = "2026-11-13"

# Official source URLs (retrieved 2026-11-13)
SRC = {
    "cola_page": "https://www.irs.gov/retirement-plans/cola-increases-for-dollar-limitations-on-benefits-and-contributions",
    "cola_pdf": "https://www.irs.gov/pub/foia/ig/tege/cola-table-dci005ma4578824.pdf",
    "n_25_67": "https://www.irs.gov/pub/irs-drop/n-25-67.pdf",
    "ir_2025_111": "https://www.irs.gov/newsroom/401k-limit-increases-to-24500-for-2026-ira-limit-increases-to-7500",
    "ira_topics": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-ira-contribution-limits",
    "p590a": "https://www.irs.gov/pub/irs-pdf/p590a.pdf",
    "p590b": "https://www.irs.gov/publications/p590b",
    "tsp_hist": "https://www.tsp.gov/hr-payroll-resources/historical-info/",
    "tsp_25_3": "https://www.tsp.gov/bulletins/25-3/",
    "ecfr_rmd": "https://www.ecfr.gov/current/title-26/chapter-I/subchapter-A/part-1/subject-group-ECFR6f8c3724b50e44d/section-1.401(a)(9)-9",
    "fr_td9930": "https://www.govinfo.gov/content/pkg/FR-2020-11-12/html/2020-24723.htm",
    "usc_408": "https://www.law.cornell.edu/uscode/text/26/408",
    "cmeg_gold": "https://www.cmegroup.com/rulebook/COMEX/1a/113.pdf",
    "cmeg_silver": "https://www.cmegroup.com/rulebook/COMEX/1a/112.pdf",
    "cmeg_plat": "https://www.cmegroup.com/rulebook/NYMEX/1a/105.pdf",
    "cmeg_pall": "https://www.cmegroup.com/rulebook/NYMEX/1a/106.pdf",
}

DISCLAIMER = (
    "This dataset restates publicly available U.S. tax-administration figures "
    "for research and software use. It is not legal, tax, or investment advice, "
    "is not an official IRS or Treasury publication, and may lag later "
    "corrections or legislation. Confirm every figure against the cited primary "
    "source before relying on it. Contribution limits can also be reduced by "
    "taxable compensation, income phase-outs, plan terms, and aggregation rules "
    "that are not fully encoded here."
)


def srcs(*keys: str) -> list[dict]:
    labels = {
        "cola_page": "IRS COLA increases for dollar limitations (web table)",
        "cola_pdf": "IRS Prior Years COLA Tables PDF",
        "n_25_67": "IRS Notice 2025-67",
        "ir_2025_111": "IRS IR-2025-111 (13 Nov 2025)",
        "ira_topics": "IRS Retirement topics — IRA contribution limits",
        "p590a": "IRS Publication 590-A (2025), for use in preparing 2025 returns (15 Jan 2026)",
        "p590b": "IRS Publication 590-B (2025), Appendix B, Table I",
        "tsp_hist": "TSP Historical information on contribution limits",
        "tsp_25_3": "TSP Bulletin 25-3, 2026 TSP Contribution Limits (19 Nov 2025)",
        "ecfr_rmd": "26 CFR § 1.401(a)(9)-9 (eCFR; authoritative but unofficial)",
        "fr_td9930": "T.D. 9930, 85 Fed. Reg. 72472 (12 Nov 2020)",
        "usc_408": "26 U.S.C. § 408(m) (Cornell LII unofficial official-text publication)",
        "cmeg_gold": "CME Group COMEX Rulebook Chapter 113 (Gold Futures)",
        "cmeg_silver": "CME Group COMEX Rulebook Chapter 112 (Silver Futures)",
        "cmeg_plat": "CME Group NYMEX Rulebook Chapter 105 (Platinum Futures)",
        "cmeg_pall": "CME Group NYMEX Rulebook Chapter 106 (Palladium Futures)",
    }
    return [
        {"url": SRC[k], "label": labels[k], "retrieved_date": RETRIEVED}
        for k in keys
    ]


# IRA annual contribution limit (IRC 219) and age-50 catch-up.
# 1997–2001 from Pub. 590-A 2025 historical worksheet (no age-50 catch-up yet).
# 2002–2025 from the IRS Prior Years COLA Tables PDF (Code § 219(b)(5)(A)/(B))
#   and the same Pub. 590-A worksheet (2025 itself is in What's New for 2025).
# 2026 from Notice 2025-67, IR-2025-111, the IRS COLA web table, and Pub. 590-A
#   "What's New for 2026".
# Pre-1997 is omitted: Pub. 590-A lists "$2,250" for "before 1997", which was the
# combined worker-plus-spouse figure, not a clean individual limit.
IRA_ROWS = [
    # year, limit, catch_up_50, source keys
    (1997, 2000, None, ("p590a",)),
    (1998, 2000, None, ("p590a",)),
    (1999, 2000, None, ("p590a",)),
    (2000, 2000, None, ("p590a",)),
    (2001, 2000, None, ("p590a",)),
    (2002, 3000, 500, ("cola_pdf", "p590a")),
    (2003, 3000, 500, ("cola_pdf", "p590a")),
    (2004, 3000, 500, ("cola_pdf", "p590a")),
    (2005, 4000, 500, ("cola_pdf", "p590a")),
    (2006, 4000, 1000, ("cola_pdf", "p590a")),
    (2007, 4000, 1000, ("cola_pdf", "p590a")),
    (2008, 5000, 1000, ("cola_pdf", "p590a")),
    (2009, 5000, 1000, ("cola_pdf", "p590a")),
    (2010, 5000, 1000, ("cola_pdf", "p590a")),
    (2011, 5000, 1000, ("cola_pdf", "p590a")),
    (2012, 5000, 1000, ("cola_pdf", "p590a")),
    (2013, 5500, 1000, ("cola_pdf", "p590a")),
    (2014, 5500, 1000, ("cola_pdf", "p590a")),
    (2015, 5500, 1000, ("cola_pdf", "p590a")),
    (2016, 5500, 1000, ("cola_pdf", "p590a")),
    (2017, 5500, 1000, ("cola_pdf", "p590a")),
    (2018, 5500, 1000, ("cola_pdf", "p590a")),
    (2019, 6000, 1000, ("cola_pdf", "p590a")),
    (2020, 6000, 1000, ("cola_pdf", "p590a")),
    (2021, 6000, 1000, ("cola_pdf", "p590a")),
    (2022, 6000, 1000, ("cola_pdf", "p590a")),
    (2023, 6500, 1000, ("cola_pdf", "p590a", "cola_page", "ira_topics")),
    (2024, 7000, 1000, ("cola_pdf", "p590a", "cola_page", "ira_topics")),
    (2025, 7000, 1000, ("cola_pdf", "p590a", "cola_page", "ira_topics")),
    (2026, 7500, 1100, ("n_25_67", "ir_2025_111", "cola_page", "p590a", "ira_topics")),
]


# 402(g) elective deferrals apply to 401(k), 403(b), governmental 457(b), and TSP.
# 1987–2025 from the official TSP historical table (cross-checked against the IRS
# Prior Years COLA Tables PDF for 1989 and 1991–2025; the COLA PDF has no 1990
# column and no 1987–1988 pages). 2026 from Notice 2025-67, IR-2025-111, the
# IRS COLA web table, and TSP Bulletin 25-3.
ELECTIVE_402G = {
    1987: 7000, 1988: 7313, 1989: 7627, 1990: 7979, 1991: 8475,
    1992: 8728, 1993: 8994, 1994: 9240, 1995: 9240, 1996: 9500,
    1997: 9500, 1998: 10000, 1999: 10000, 2000: 10500, 2001: 10500,
    2002: 11000, 2003: 12000, 2004: 13000, 2005: 14000, 2006: 15000,
    2007: 15500, 2008: 15500, 2009: 16500, 2010: 16500, 2011: 16500,
    2012: 17000, 2013: 17500, 2014: 17500, 2015: 18000, 2016: 18000,
    2017: 18000, 2018: 18500, 2019: 19000, 2020: 19500, 2021: 19500,
    2022: 20500, 2023: 22500, 2024: 23000, 2025: 23500, 2026: 24500,
}

# IRC 415(c) annual additions. TSP historical table starts in 2002 (N/A before).
# 2002–2025 also in the IRS COLA PDF; 2026 from Notice 2025-67 / TSP Bulletin 25-3.
ADDITIONS_415C = {
    2002: 40000, 2003: 40000, 2004: 41000, 2005: 42000, 2006: 44000,
    2007: 45000, 2008: 46000, 2009: 49000, 2010: 49000, 2011: 49000,
    2012: 50000, 2013: 51000, 2014: 52000, 2015: 53000, 2016: 53000,
    2017: 54000, 2018: 55000, 2019: 56000, 2020: 57000, 2021: 58000,
    2022: 61000, 2023: 66000, 2024: 69000, 2025: 70000, 2026: 72000,
}

# IRC 414(v)(2)(B)(i) age-50 catch-up for most 401(k)/403(b)/gov. 457/TSP plans.
# IRS COLA PDF starts this column in 2002 ($1,000). The TSP historical table
# lists catch-up as N/A for 2002 (TSP did not yet administer the catch-up) and
# begins in 2003.
CATCHUP_414V_50 = {
    2002: 1000, 2003: 2000, 2004: 3000, 2005: 4000, 2006: 5000,
    2007: 5000, 2008: 5000, 2009: 5500, 2010: 5500, 2011: 5500,
    2012: 5500, 2013: 5500, 2014: 5500, 2015: 6000, 2016: 6000,
    2017: 6000, 2018: 6000, 2019: 6000, 2020: 6500, 2021: 6500,
    2022: 6500, 2023: 7500, 2024: 7500, 2025: 7500, 2026: 8000,
}

# SECURE 2.0 higher catch-up for ages 60–63, first applicable in 2025.
CATCHUP_414V_60_63 = {2025: 11250, 2026: 11250}

# SIMPLE IRA / SIMPLE 401(k) salary-reduction limit, IRC 408(p)(2)(E).
# IRS COLA PDF from 1997 (SIMPLE's first year) through 2025; 2026 from Notice
# 2025-67 and the IRS COLA web table.
SIMPLE_ELECTIVE = {
    1997: 6000, 1998: 6000, 1999: 6000, 2000: 6000, 2001: 6500,
    2002: 7000, 2003: 8000, 2004: 9000, 2005: 10000, 2006: 10000,
    2007: 10500, 2008: 10500, 2009: 11500, 2010: 11500, 2011: 11500,
    2012: 11500, 2013: 12000, 2014: 12000, 2015: 12500, 2016: 12500,
    2017: 12500, 2018: 12500, 2019: 13000, 2020: 13500, 2021: 13500,
    2022: 14000, 2023: 15500, 2024: 16000, 2025: 16500, 2026: 17000,
}

# IRC 414(v)(2)(B)(ii) SIMPLE catch-up (age 50).
SIMPLE_CATCHUP_50 = {
    2002: 500, 2003: 1000, 2004: 1500, 2005: 2000, 2006: 2500,
    2007: 2500, 2008: 2500, 2009: 2500, 2010: 2500, 2011: 2500,
    2012: 2500, 2013: 2500, 2014: 2500, 2015: 3000, 2016: 3000,
    2017: 3000, 2018: 3000, 2019: 3000, 2020: 3500, 2021: 3500,
    2022: 3500, 2023: 3500, 2024: 3500, 2025: 3500, 2026: 4000,
}

# SECURE 2.0 higher SIMPLE catch-up for ages 60–63.
SIMPLE_CATCHUP_60_63 = {2025: 5250, 2026: 5250}

# 26 CFR § 1.401(a)(9)-9(c) Table 2, applicable for distribution calendar years
# beginning on or after 1 Jan 2022 (T.D. 9930).
UNIFORM_LIFETIME = [
    (72, 27.4), (73, 26.5), (74, 25.5), (75, 24.6), (76, 23.7),
    (77, 22.9), (78, 22.0), (79, 21.1), (80, 20.2), (81, 19.4),
    (82, 18.5), (83, 17.7), (84, 16.8), (85, 16.0), (86, 15.2),
    (87, 14.4), (88, 13.7), (89, 12.9), (90, 12.2), (91, 11.5),
    (92, 10.8), (93, 10.1), (94, 9.5), (95, 8.9), (96, 8.4),
    (97, 7.8), (98, 7.3), (99, 6.8), (100, 6.4), (101, 6.0),
    (102, 5.6), (103, 5.2), (104, 4.9), (105, 4.6), (106, 4.3),
    (107, 4.1), (108, 3.9), (109, 3.7), (110, 3.5), (111, 3.4),
    (112, 3.3), (113, 3.1), (114, 3.0), (115, 2.9), (116, 2.8),
    (117, 2.7), (118, 2.5), (119, 2.3),
]
# Age 120 and older share the 2.0 denominator.
UNIFORM_LIFETIME_120_PLUS = 2.0


# IRS Publication 590-B (2025), Appendix B, Table I (For Use by Beneficiaries).
# Also 26 CFR § 1.401(a)(9)-9(b), Table 1, applicable for distribution calendar
# years beginning on or after 1 Jan 2022 (T.D. 9930). Values transcribed from
# the verified IRS table retrieved on 2026-11-13; no runtime fetch is needed.
SINGLE_LIFE = [
    (0, 84.6), (1, 83.7), (2, 82.8), (3, 81.8), (4, 80.8),
    (5, 79.8), (6, 78.8), (7, 77.9), (8, 76.9), (9, 75.9),
    (10, 74.9), (11, 73.9), (12, 72.9), (13, 71.9), (14, 70.9),
    (15, 69.9), (16, 69.0), (17, 68.0), (18, 67.0), (19, 66.0),
    (20, 65.0), (21, 64.1), (22, 63.1), (23, 62.1), (24, 61.1),
    (25, 60.2), (26, 59.2), (27, 58.2), (28, 57.3), (29, 56.3),
    (30, 55.3), (31, 54.4), (32, 53.4), (33, 52.5), (34, 51.5),
    (35, 50.5), (36, 49.6), (37, 48.6), (38, 47.7), (39, 46.7),
    (40, 45.7), (41, 44.8), (42, 43.8), (43, 42.9), (44, 41.9),
    (45, 41.0), (46, 40.0), (47, 39.0), (48, 38.1), (49, 37.1),
    (50, 36.2), (51, 35.3), (52, 34.3), (53, 33.4), (54, 32.5),
    (55, 31.6), (56, 30.6), (57, 29.8), (58, 28.9), (59, 28.0),
    (60, 27.1), (61, 26.2), (62, 25.4), (63, 24.5), (64, 23.7),
    (65, 22.9), (66, 22.0), (67, 21.2), (68, 20.4), (69, 19.6),
    (70, 18.8), (71, 18.0), (72, 17.2), (73, 16.4), (74, 15.6),
    (75, 14.8), (76, 14.1), (77, 13.3), (78, 12.6), (79, 11.9),
    (80, 11.2), (81, 10.5), (82, 9.9), (83, 9.3), (84, 8.7),
    (85, 8.1), (86, 7.6), (87, 7.1), (88, 6.6), (89, 6.1),
    (90, 5.7), (91, 5.3), (92, 4.9), (93, 4.6), (94, 4.3),
    (95, 4.0), (96, 3.7), (97, 3.4), (98, 3.2), (99, 3.0),
    (100, 2.8), (101, 2.6), (102, 2.5), (103, 2.3), (104, 2.2),
    (105, 2.1), (106, 2.1), (107, 2.1), (108, 2.0), (109, 2.0),
    (110, 2.0), (111, 2.0), (112, 2.0), (113, 1.9), (114, 1.9),
    (115, 1.8), (116, 1.8), (117, 1.6), (118, 1.4), (119, 1.1),
]
# Age 120 and older share the 1.0 life expectancy.
SINGLE_LIFE_120_PLUS = 1.0


def employer_sources(year: int) -> tuple[str, ...]:
    if year == 2026:
        return ("n_25_67", "ir_2025_111", "cola_page", "tsp_25_3")
    if year == 1990:
        return ("tsp_hist",)  # IRS COLA PDF has no 1990 column
    if year in (1987, 1988):
        return ("tsp_hist",)  # IRS COLA PDF in this edition starts later
    if year <= 2001:
        return ("tsp_hist", "cola_pdf")
    return ("tsp_hist", "cola_pdf")


def build() -> dict:
    ira = []
    for year, limit, catch, keys in IRA_ROWS:
        row = {
            "year": year,
            "contribution_limit": limit,
            "catch_up_age_50": catch,
            "total_if_age_50_or_older": None if catch is None else limit + catch,
            "applies_to": [
                "traditional_ira",
                "roth_ira",
            ],
            "code_section": "26 U.S.C. § 219(b)",
            "sources": srcs(*keys),
            "notes": (
                "This is the combined annual contribution limit across all traditional and Roth IRAs. "
                "It does not apply to rollovers. The deductible amount and Roth eligibility can be "
                "reduced by compensation and AGI phase-out rules that are not encoded in this row."
            ),
        }
        if year == 2026:
            row["notes"] += (
                " The age-50 IRA catch-up became subject to an annual COLA under the SECURE 2.0 Act "
                "and increased to $1,100 for 2026 (IR-2025-111; Notice 2025-67)."
            )
        ira.append(row)

    employer = []
    for year, elective in sorted(ELECTIVE_402G.items()):
        catch50 = CATCHUP_414V_50.get(year)
        catch60 = CATCHUP_414V_60_63.get(year)
        additions = ADDITIONS_415C.get(year)
        tsp_catch50 = None if year == 2002 else catch50
        tsp_catch60 = catch60
        keys = employer_sources(year)
        notes = (
            "The IRC § 402(g) elective-deferral limit is a personal, aggregated limit across "
            "401(k), 403(b), governmental 457(b), and TSP employee deferrals. Agency/employer "
            "automatic and matching contributions do not count toward 402(g) but do count toward "
            "the § 415(c) annual-additions limit. Catch-up amounts under § 414(v) are in addition "
            "to the 402(g) limit and are not annual additions."
        )
        if year == 2002:
            notes += (
                " IRS COLA tables list a $1,000 statutory age-50 catch-up for 2002; the official "
                "TSP historical table records catch-up as N/A for 2002 (tsp_catch_up_age_50 is null)."
            )
        if year >= 2025:
            notes += (
                " Beginning in 2025, SECURE 2.0 provides a higher catch-up limit for participants "
                "who attain age 60, 61, 62, or 63 during the calendar year. From 2026, catch-up "
                "contributions for some higher-wage participants must be Roth (see Notice 2025-67)."
            )
        employer.append({
            "year": year,
            "applies_to": [
                "401k",
                "403b",
                "governmental_457b",
                "thrift_savings_plan",
            ],
            "elective_deferral_402g": elective,
            "catch_up_age_50_414v": catch50,
            "catch_up_age_60_63_414v": catch60,
            "annual_additions_415c": additions,
            "tsp_catch_up_age_50": tsp_catch50,
            "tsp_catch_up_age_60_63": tsp_catch60,
            "code_sections": [
                "26 U.S.C. § 402(g)",
                "26 U.S.C. § 414(v)",
                "26 U.S.C. § 415(c)",
            ],
            "sources": srcs(*keys),
            "notes": notes,
        })

    simple = []
    for year, elective in sorted(SIMPLE_ELECTIVE.items()):
        keys = ("n_25_67", "ir_2025_111", "cola_page") if year == 2026 else ("cola_pdf",)
        if year >= 2023 and year != 2026:
            keys = ("cola_pdf", "cola_page")
        simple.append({
            "year": year,
            "applies_to": ["simple_ira", "simple_401k"],
            "elective_deferral": elective,
            "catch_up_age_50_414v": SIMPLE_CATCHUP_50.get(year),
            "catch_up_age_60_63_414v": SIMPLE_CATCHUP_60_63.get(year),
            "code_sections": [
                "26 U.S.C. § 408(p)(2)(E)",
                "26 U.S.C. § 414(v)(2)(B)(ii)",
            ],
            "sources": srcs(*keys),
            "notes": (
                "Certain SIMPLE plans of smaller eligible employers have a higher elective limit "
                "(110% of the regular SIMPLE limit) under SECURE 2.0; that higher figure is "
                "$18,100 for 2026 (Notice 2025-67) and is not a separate column in this file."
            ),
        })

    rmd = []
    for age, denom in UNIFORM_LIFETIME:
        rmd.append({
            "age": age,
            "age_is_120_or_older": False,
            "applicable_denominator": denom,
            "sources": srcs("ecfr_rmd", "fr_td9930"),
        })
    rmd.append({
        "age": 120,
        "age_is_120_or_older": True,
        "applicable_denominator": UNIFORM_LIFETIME_120_PLUS,
        "sources": srcs("ecfr_rmd", "fr_td9930"),
    })

    single_life = []
    for age, expectancy in SINGLE_LIFE:
        single_life.append({
            "age": age,
            "age_is_120_or_older": False,
            "life_expectancy": expectancy,
            "sources": srcs("p590b", "ecfr_rmd", "fr_td9930"),
        })
    single_life.append({
        "age": 120,
        "age_is_120_or_older": True,
        "life_expectancy": SINGLE_LIFE_120_PLUS,
        "sources": srcs("p590b", "ecfr_rmd", "fr_td9930"),
    })

    metals = {
        "statute": {
            "citation": "26 U.S.C. § 408(m)",
            "retrieved_date": RETRIEVED,
            "sources": srcs("usc_408"),
            "rule": (
                "The acquisition by an IRA of a 'collectible' is treated as a distribution equal "
                "to the cost of that collectible. 'Collectible' includes any metal or gem and any "
                "stamp or coin, with the exceptions in § 408(m)(3)."
            ),
            "named_coin_exceptions": [
                {
                    "description": "A gold coin described in paragraph (7), (8), (9), or (10) of 31 U.S.C. § 5112(a)",
                    "code": "26 U.S.C. § 408(m)(3)(A)(i)",
                },
                {
                    "description": "A silver coin described in 31 U.S.C. § 5112(e)",
                    "code": "26 U.S.C. § 408(m)(3)(A)(ii)",
                },
                {
                    "description": "A platinum coin described in 31 U.S.C. § 5112(k)",
                    "code": "26 U.S.C. § 408(m)(3)(A)(iii)",
                },
                {
                    "description": "A coin issued under the laws of any State",
                    "code": "26 U.S.C. § 408(m)(3)(A)(iv)",
                },
            ],
            "bullion_exception": (
                "Gold, silver, platinum, or palladium bullion of a fineness equal to or exceeding "
                "the minimum fineness that a contract market (as described in section 5 of the "
                "Commodity Exchange Act, 7 U.S.C. § 7) requires for metals which may be delivered "
                "in satisfaction of a regulated futures contract, if such bullion is in the physical "
                "possession of a trustee described in 26 U.S.C. § 408(a)."
            ),
            "notes": (
                "The statute incorporates contract-market delivery fineness by reference; those "
                "exchange rules can change. Coins that are not in the named U.S. Mint / state-issue "
                "list (for example many foreign bullion coins, or U.S. coins described in other "
                "paragraphs of 31 U.S.C. § 5112) are not automatically excepted as coins. They are "
                "excepted only if they meet the bullion fineness test and are held by the IRA trustee. "
                "This file does not determine whether any particular product is IRA-eligible."
            ),
        },
        "contract_market_minimum_fineness_retrieved": [
            {
                "metal": "gold",
                "minimum_fineness": 0.995,
                "fineness_notation": "995",
                "how_the_exchange_states_it": "assay to a minimum of 995 fineness",
                "contract_market": "COMEX (CME Group)",
                "contract": "Gold futures, Chapter 113",
                "sources": srcs("cmeg_gold"),
            },
            {
                "metal": "silver",
                "minimum_fineness": 0.999,
                "fineness_notation": "999",
                "how_the_exchange_states_it": "assay to a minimum of 999 fineness",
                "contract_market": "COMEX (CME Group)",
                "contract": "Silver futures, Chapter 112",
                "sources": srcs("cmeg_silver"),
            },
            {
                "metal": "platinum",
                "minimum_fineness": 0.9995,
                "fineness_notation": "999.5 / 99.95%",
                "how_the_exchange_states_it": "a minimum of 99.95% pure",
                "contract_market": "NYMEX (CME Group)",
                "contract": "Platinum futures, Chapter 105",
                "sources": srcs("cmeg_plat"),
            },
            {
                "metal": "palladium",
                "minimum_fineness": 0.9995,
                "fineness_notation": "999.5 / 99.95%",
                "how_the_exchange_states_it": "a minimum of 99.95% pure",
                "contract_market": "NYMEX (CME Group)",
                "contract": "Palladium futures, Chapter 106",
                "sources": srcs("cmeg_pall"),
            },
        ],
    }

    return {
        "meta": {
            "name": "us-retirement-limits",
            "title": "US retirement contribution limits, RMD Uniform Lifetime Table, and IRA-eligible metal rules",
            "version": "2026.1.0",
            "retrieved_date": RETRIEVED,
            "license_data": "CC-BY-4.0",
            "license_code": "MIT",
            "maintainer": "Lead Partner AS",
            "disclaimer": DISCLAIMER,
            "schema_version": 1,
        },
        "ira_contribution_limits": ira,
        "employer_plan_limits": employer,
        "simple_plan_limits": simple,
        "rmd_uniform_lifetime": {
            "table": "Uniform Lifetime Table (Table 2 to 26 CFR § 1.401(a)(9)-9(c))",
            "applicable_for_distribution_years": "calendar years beginning on or after 2022-01-01",
            "used_when": (
                "Lifetime required minimum distributions for an employee or IRA owner when the "
                "surviving spouse is not the sole designated beneficiary, or is the sole designated "
                "beneficiary but is not more than 10 years younger. RMD = prior year-end account "
                "balance ÷ applicable denominator for the age attained in the distribution year."
            ),
            "required_beginning_date_note": (
                "The table itself starts at age 72. The age at which RMDs must begin is a separate "
                "statutory rule (now generally age 73, and later age 75 for some later-born cohorts "
                "under SECURE 2.0) and is not encoded as a column here."
            ),
            "sources": srcs("ecfr_rmd", "fr_td9930"),
            "rows": rmd,
        },
        "rmd_single_life": {
            "table": "Single Life Expectancy Table (IRS Publication 590-B, Table I; Table 1 to 26 CFR § 1.401(a)(9)-9(b))",
            "applicable_for_distribution_years": "calendar years beginning on or after 2022-01-01",
            "used_when": (
                "Life expectancy lookups for beneficiaries using Table I (Single Life Expectancy). "
                "The applicable beneficiary distribution rules determine how the table is used."
            ),
            "sources": srcs("p590b", "ecfr_rmd", "fr_td9930"),
            "rows": single_life,
        },
        "ira_eligible_metals": metals,
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def primary_source(sources: list[dict]) -> tuple[str, str]:
    first = sources[0]
    return first["url"], first["retrieved_date"]


def emit(dataset: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "dataset.json").write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    ira_rows = []
    for r in dataset["ira_contribution_limits"]:
        url, date = primary_source(r["sources"])
        ira_rows.append({
            "year": r["year"],
            "contribution_limit": r["contribution_limit"],
            "catch_up_age_50": "" if r["catch_up_age_50"] is None else r["catch_up_age_50"],
            "total_if_age_50_or_older": "" if r["total_if_age_50_or_older"] is None else r["total_if_age_50_or_older"],
            "source_url": url,
            "retrieved_date": date,
        })
    write_csv(
        DATA / "ira-contribution-limits.csv",
        ["year", "contribution_limit", "catch_up_age_50", "total_if_age_50_or_older", "source_url", "retrieved_date"],
        ira_rows,
    )

    emp_rows = []
    for r in dataset["employer_plan_limits"]:
        url, date = primary_source(r["sources"])
        emp_rows.append({
            "year": r["year"],
            "elective_deferral_402g": r["elective_deferral_402g"],
            "catch_up_age_50_414v": "" if r["catch_up_age_50_414v"] is None else r["catch_up_age_50_414v"],
            "catch_up_age_60_63_414v": "" if r["catch_up_age_60_63_414v"] is None else r["catch_up_age_60_63_414v"],
            "annual_additions_415c": "" if r["annual_additions_415c"] is None else r["annual_additions_415c"],
            "tsp_catch_up_age_50": "" if r["tsp_catch_up_age_50"] is None else r["tsp_catch_up_age_50"],
            "tsp_catch_up_age_60_63": "" if r["tsp_catch_up_age_60_63"] is None else r["tsp_catch_up_age_60_63"],
            "source_url": url,
            "retrieved_date": date,
        })
    write_csv(
        DATA / "employer-plan-limits.csv",
        [
            "year", "elective_deferral_402g", "catch_up_age_50_414v",
            "catch_up_age_60_63_414v", "annual_additions_415c",
            "tsp_catch_up_age_50", "tsp_catch_up_age_60_63",
            "source_url", "retrieved_date",
        ],
        emp_rows,
    )

    simple_rows = []
    for r in dataset["simple_plan_limits"]:
        url, date = primary_source(r["sources"])
        simple_rows.append({
            "year": r["year"],
            "elective_deferral": r["elective_deferral"],
            "catch_up_age_50_414v": "" if r["catch_up_age_50_414v"] is None else r["catch_up_age_50_414v"],
            "catch_up_age_60_63_414v": "" if r["catch_up_age_60_63_414v"] is None else r["catch_up_age_60_63_414v"],
            "source_url": url,
            "retrieved_date": date,
        })
    write_csv(
        DATA / "simple-plan-limits.csv",
        ["year", "elective_deferral", "catch_up_age_50_414v", "catch_up_age_60_63_414v", "source_url", "retrieved_date"],
        simple_rows,
    )

    rmd_rows = []
    for r in dataset["rmd_uniform_lifetime"]["rows"]:
        url, date = primary_source(r["sources"])
        rmd_rows.append({
            "age": r["age"],
            "age_is_120_or_older": "true" if r["age_is_120_or_older"] else "false",
            "applicable_denominator": r["applicable_denominator"],
            "source_url": url,
            "retrieved_date": date,
        })
    write_csv(
        DATA / "rmd-uniform-lifetime.csv",
        ["age", "age_is_120_or_older", "applicable_denominator", "source_url", "retrieved_date"],
        rmd_rows,
    )

    single_life_rows = []
    for r in dataset["rmd_single_life"]["rows"]:
        url, date = primary_source(r["sources"])
        single_life_rows.append({
            "age": r["age"],
            "age_is_120_or_older": "true" if r["age_is_120_or_older"] else "false",
            "life_expectancy": r["life_expectancy"],
            "source_url": url,
            "retrieved_date": date,
        })
    write_csv(
        DATA / "rmd-single-life.csv",
        ["age", "age_is_120_or_older", "life_expectancy", "source_url", "retrieved_date"],
        single_life_rows,
    )

    metal_rows = []
    for r in dataset["ira_eligible_metals"]["contract_market_minimum_fineness_retrieved"]:
        url, date = primary_source(r["sources"])
        metal_rows.append({
            "metal": r["metal"],
            "minimum_fineness": r["minimum_fineness"],
            "fineness_notation": r["fineness_notation"],
            "how_the_exchange_states_it": r["how_the_exchange_states_it"],
            "contract_market": r["contract_market"],
            "contract": r["contract"],
            "source_url": url,
            "retrieved_date": date,
        })
    write_csv(
        DATA / "ira-eligible-metals-fineness.csv",
        [
            "metal", "minimum_fineness", "fineness_notation", "how_the_exchange_states_it",
            "contract_market", "contract", "source_url", "retrieved_date",
        ],
        metal_rows,
    )


if __name__ == "__main__":
    dataset = build()
    emit(dataset)
    print(f"Wrote dataset version {dataset['meta']['version']} to {DATA}")
