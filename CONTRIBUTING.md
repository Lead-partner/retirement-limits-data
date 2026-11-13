# Contributing

Corrections and well-sourced additions are welcome.

1. Every number needs a primary-source URL (IRS.gov, tsp.gov, a Federal Register or eCFR citation, the U.S. Code, or a contract-market rulebook) and a retrieved date.
2. Do not invent, interpolate, or copy figures from blogs, calculators, or secondary explainers.
3. Edit the tables in `scripts/build_dataset.py`, then run:

   ```bash
   python3 scripts/build_dataset.py
   python3 scripts/validate.py
   node tests/test_loader.js
   ```

4. Add or adjust a validation anchor in `scripts/validate.py` when you introduce a new official figure.
5. Open a pull request that quotes the source sentence or table cell you relied on.

This repository does not accept estimated fees, product reviews, or affiliate links.
