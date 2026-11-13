import {
  employerPlanLimit,
  iraLimit,
  loadDataset,
  metalFineness,
  rmdAmount,
  rmdDenominator,
  singleLifeExpectancy,
} from "../src/js/index.js";
import assert from "node:assert/strict";

const d = loadDataset();
if (d.meta.version !== "2026.1.0") throw new Error("version");
if (iraLimit(2026, 49).applicable_limit !== 7500) throw new Error("IRA 49");
if (iraLimit(2026, 62).applicable_limit !== 8600) throw new Error("IRA 62");
if (employerPlanLimit(2026).elective_deferral_402g !== 24500) throw new Error("402g");
if (rmdDenominator(72) !== 27.4) throw new Error("RMD 72");
if (rmdAmount(274000, 72) !== 10000) throw new Error("RMD math");
const singleRows = d.rmd_single_life.rows;
assert.deepEqual(singleRows.map((row) => row.age), Array.from({ length: 121 }, (_, age) => age));
for (const [age, expectancy] of [[0, 84.6], [55, 31.6], [57, 29.8], [120, 1.0]]) {
  assert.equal(singleRows[age].life_expectancy, expectancy, `Single Life data age ${age}`);
  assert.equal(singleLifeExpectancy(age), expectancy, `Single Life loader age ${age}`);
}
for (let age = 0; age <= 120; age++) {
  assert.equal(singleRows[age].age_is_120_or_older, age === 120);
  if (age > 0) {
    assert.ok(singleRows[age - 1].life_expectancy >= singleRows[age].life_expectancy, `Single Life data increased at age ${age}`);
    assert.ok(singleLifeExpectancy(age - 1) >= singleLifeExpectancy(age), `Single Life loader increased at age ${age}`);
  }
}
assert.equal(singleLifeExpectancy(121), 1.0);
assert.equal(singleLifeExpectancy(150), 1.0);
assert.equal(singleLifeExpectancy(55, d), 31.6);
for (const age of [-1, 55.5, 120.5, "55", null, undefined, true, NaN, Infinity]) {
  assert.throws(() => singleLifeExpectancy(age), /age must be a non-negative integer/);
}
if (metalFineness("silver").minimum_fineness !== 0.999) throw new Error("silver");
console.log("js loader ok");
