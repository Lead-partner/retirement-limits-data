# Schema

`data/dataset.json` is the canonical document. The CSV files are flattened views of the same figures, with one primary `source_url` and `retrieved_date` on every row. Dollar amounts are integers (USD, no cents). Fineness and RMD denominators are decimal numbers.

## `meta`

| Field | Type | Meaning |
|-------|------|---------|
| `name` | string | Machine name, `us-retirement-limits` |
| `version` | string | Dataset version, currently `2026.1.0` |
| `retrieved_date` | string | ISO date the sources were read, `YYYY-MM-DD` |
| `license_data` | string | `CC-BY-4.0` |
| `license_code` | string | `MIT` |
| `disclaimer` | string | Required warning text |

## `ira_contribution_limits[]`

One object per calendar year, 1997–2026.

| Field | Type | Meaning |
|-------|------|---------|
| `year` | integer | Tax year |
| `contribution_limit` | integer | Combined traditional + Roth IRA limit under IRC § 219(b) |
| `catch_up_age_50` | integer or null | Additional amount if age 50 or older at year-end; `null` before 2002 |
| `total_if_age_50_or_older` | integer or null | `contribution_limit + catch_up_age_50` |
| `sources` | array | Each entry has `url`, `label`, `retrieved_date` |

The limit does not apply to rollovers. Deductibility and Roth eligibility can be reduced by compensation and AGI phase-outs, which are not columns in this table.

Years before 1997 are omitted on purpose. Publication 590-A lists "$2,250" for "before 1997", but that figure was the combined worker-plus-spouse amount, not a clean individual limit.

## `employer_plan_limits[]`

One object per calendar year, 1987–2026. The § 402(g) elective-deferral limit applies in the aggregate to 401(k), 403(b), governmental 457(b), and TSP employee deferrals.

| Field | Type | Meaning |
|-------|------|---------|
| `elective_deferral_402g` | integer | IRC § 402(g) limit |
| `catch_up_age_50_414v` | integer or null | Statutory age-50 catch-up under § 414(v)(2)(B)(i); `null` before 2002 |
| `catch_up_age_60_63_414v` | integer or null | Higher SECURE 2.0 catch-up for ages 60–63; first applies in 2025 |
| `annual_additions_415c` | integer or null | IRC § 415(c) limit; `null` before 2002 in this dataset (TSP marks those years N/A) |
| `tsp_catch_up_age_50` | integer or null | Catch-up as administered by TSP; `null` in 2002 even though the statutory 401(k) catch-up was $1,000 |

Employer matching and automatic contributions do not count toward § 402(g) but do count toward § 415(c). Catch-up contributions under § 414(v) are in addition to the elective-deferral limit and are not annual additions.

## `simple_plan_limits[]`

SIMPLE IRA and SIMPLE 401(k) salary-reduction limits, 1997–2026, with the regular (not 110%) elective limit. The higher limit that applies to certain smaller eligible employers under SECURE 2.0 ($18,100 for 2026) is described in the row notes, not as a separate column.

## `rmd_uniform_lifetime`

Treasury regulation 26 CFR § 1.401(a)(9)-9(c), Table 2, applicable for distribution calendar years beginning on or after 1 January 2022.

| Field | Type | Meaning |
|-------|------|---------|
| `age` | integer | Age attained in the distribution year; `120` with `age_is_120_or_older: true` covers 120 and up |
| `applicable_denominator` | number | Divide the prior year-end account balance by this number |

The table starts at 72. The age at which RMDs must begin is a separate statutory rule and is not a column here.

## `ira_eligible_metals`

- `statute` — the text of the § 408(m) collectible rule and the four named coin exceptions, cited to 26 U.S.C. § 408(m).
- `contract_market_minimum_fineness_retrieved` — CME Group delivery minima read on the retrieval date (gold 0.995, silver 0.999, platinum 0.9995, palladium 0.9995). These are the "contract market" fineness requirements the statute incorporates by reference. They can change.

The dataset does not classify any commercial product as IRA-eligible.
