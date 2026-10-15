## 2.0.0-RC3

- Added Apify Token, Actor ID and Input JSON fields under Settings.
- Added admin-only save/read/delete API, no-store responses, validation, blank-token preservation, ENV fallback and running-job lock.
- Encrypted server-side configuration with Fernet; local key file or SETTINGS_ENCRYPTION_KEY.
- EKAP reads saved configuration and continues sending credentials only in Authorization header.
- Fixed Jinja dictionary clear-method collision and corrupted separators.
- Restored standalone Dockerfile and environment examples; retained supplied connector code and existing features.
- Added 9 regression/security tests. 49 tests passed in this environment. No live portal/Actor or deployment certification.

# 2.0.0-RC2 native adapters
Full standalone package based on RC1; no patches/overlay.
Replaced all four TED fallback modules with native public-portal adapters: Slovakia UVO/EVO; Lithuania new CVP IS; Hungary EKR; Estonia RHR. No imports/calls to TED from these modules. Added public-page browser helper, Chromium Docker installation, portal-specific date parsing, native diagnostics, source metadata, local-language keywords and 16 additional tests (14 parser/workflow + 2 browser fixtures). Preserved TenderNed, UI, exports, analytics, filters, storage and translation.

These are beta implementations, not live-certified repairs. Native requests from the build environment returned HTTP 403. EKR modal detail parsing, RHR exact live labels, dynamic pagination and completeness remain unverified. See README_UA.md and TEST_RESULTS.md.
