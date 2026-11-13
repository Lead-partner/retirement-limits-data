/**
 * Tiny loader for the US retirement-limits dataset.
 * This package is not published to npm. Copy this file, or clone the repository.
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const DATA = join(ROOT, "data");

export function loadDataset(path = join(DATA, "dataset.json")) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function findYear(rows, year) {
  const row = rows.find((r) => r.year === year);
  if (!row) throw new Error(`No row for year ${year}`);
  return row;
}

export function iraLimit(year, age, dataset = loadDataset()) {
  const row = findYear(dataset.ira_contribution_limits, year);
  let applicable = row.contribution_limit;
  if (age != null && age >= 50 && row.catch_up_age_50 != null) {
    applicable = row.total_if_age_50_or_older;
  }
  return { ...row, applicable_limit: applicable };
}

export function employerPlanLimit(year, dataset = loadDataset()) {
  return findYear(dataset.employer_plan_limits, year);
}

export function simplePlanLimit(year, dataset = loadDataset()) {
  return findYear(dataset.simple_plan_limits, year);
}

export function rmdDenominator(age, dataset = loadDataset()) {
  const rows = dataset.rmd_uniform_lifetime.rows;
  if (age >= 120) {
    return Number(rows.find((r) => r.age_is_120_or_older).applicable_denominator);
  }
  const row = rows.find((r) => r.age === age && !r.age_is_120_or_older);
  if (!row) throw new Error(`No Uniform Lifetime denominator for age ${age}`);
  return Number(row.applicable_denominator);
}

export function singleLifeExpectancy(age, dataset = loadDataset()) {
  if (!Number.isInteger(age) || age < 0) {
    throw new Error("age must be a non-negative integer");
  }
  const rows = dataset.rmd_single_life.rows;
  const row = rows.find((r) => r.age === Math.min(age, 120));
  if (!row) throw new Error(`No Single Life expectancy for age ${age}`);
  return Number(row.life_expectancy);
}

export function rmdAmount(accountBalance, age, dataset = loadDataset()) {
  if (accountBalance < 0) throw new Error("accountBalance must be >= 0");
  return accountBalance / rmdDenominator(age, dataset);
}

export function metalFineness(metal, dataset = loadDataset()) {
  const key = String(metal).trim().toLowerCase();
  const row = dataset.ira_eligible_metals.contract_market_minimum_fineness_retrieved.find(
    (r) => r.metal === key,
  );
  if (!row) throw new Error(`No contract-market fineness row for metal ${metal}`);
  return row;
}
