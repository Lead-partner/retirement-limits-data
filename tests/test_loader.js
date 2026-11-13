import {
  employerPlanLimit,
  iraLimit,
  loadDataset,
  metalFineness,
  rmdAmount,
  rmdDenominator,
} from "../src/js/index.js";

const d = loadDataset();
if (d.meta.version !== "2026.1.0") throw new Error("version");
if (iraLimit(2026, 49).applicable_limit !== 7500) throw new Error("IRA 49");
if (iraLimit(2026, 62).applicable_limit !== 8600) throw new Error("IRA 62");
if (employerPlanLimit(2026).elective_deferral_402g !== 24500) throw new Error("402g");
if (rmdDenominator(72) !== 27.4) throw new Error("RMD 72");
if (rmdAmount(274000, 72) !== 10000) throw new Error("RMD math");
if (metalFineness("silver").minimum_fineness !== 0.999) throw new Error("silver");
console.log("js loader ok");
