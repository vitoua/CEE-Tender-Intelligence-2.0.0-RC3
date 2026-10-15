# RC3 validation

Executed in preparation environment:
- tests/test_app.py: 26 passed.
- tests/test_native.py: 14 passed.
- tests/test_apify_settings.py: 9 passed.
- Total: 49 passed.
- Python compileall: passed.
- node --check app/static/app.js: passed.

New checks cover missing/invalid admin credentials, disabled settings without server admin token, encrypted database values, token non-disclosure, no-store responses, blank-token preservation, JSON/Actor/token validation, cross-origin write rejection, deletion/ENV fallback, running-job lock, mocked EKAP use of saved credentials and corrected clear-selection label.

Not executed for RC3: browser integration tests, visual browser QA, Docker build, clean pinned dependency installation, Render deployment, live Apify requests/paid Actor runs, live portal collection, memory/load tests. The 2 existing native browser-fixture tests are retained but were not rerun. No synthetic tenders, database, secrets or generated encryption keys are shipped. All executed connector tests use synthetic fixtures or mocked requests, not live portal evidence.
