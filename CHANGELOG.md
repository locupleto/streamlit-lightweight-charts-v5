# Changelog

## Unreleased

### Security
- Migrated the frontend build from the abandoned Create React App
  (react-scripts) to Vite; npm audit findings went from 47 (21 high,
  1 critical, all in the frozen CRA toolchain) to 0
- Added CI gate failing on high/critical npm audit findings, plus weekly
  Dependabot updates for npm, pip, and GitHub Actions

### Changed
- Upgraded React 16.13 to 18.3 (createRoot, automatic JSX runtime) and
  TypeScript to 5.x; upgraded lightweight-charts to 5.2.0, Vite to 8.x
- Loading the frontend from the dev server is now an explicit opt-in via
  the LWC_V5_DEV_SERVER environment variable; installed releases no longer
  probe localhost:3001 on import
- Build backend switched from setuptools + MANIFEST.in to hatchling; the
  version is single-sourced in pyproject.toml and __version__ is read from
  package metadata; the wheel now ships the LICENSE file
- requires-python raised to >=3.9 (3.7/3.8 are EOL)
- Releases publish via GitHub Actions and PyPI Trusted Publishing on
  version tags; frontend/build/ is no longer committed to git

### Added
- Cloud fill support: a series config can carry a `cloud` payload
  ({time, a, b} points plus colors) rendered by a new IchimokuCloud
  canvas primitive that fills between the two tracks, bull/bear colored
  with exact crossover seams - enables Ichimoku kumo and similar bands
- Ichimoku Kinko Hyo demo (demo/ichimoku_demo.py) and IchimokuIndicator
  overlay (demo/indicators.py) with forward-displaced Senkou spans and
  Chikou span
- CI workflow running frontend typecheck/build/audit, package build and
  twine check, and a Playwright e2e smoke test on every push and PR
- Deterministic e2e smoke test (e2e/smoke_app.py) replacing the leftover
  component-template test

## 0.1.8 (2025-12-27)

### Security
- Reduced npm security vulnerabilities from 15 to 9 through dependency updates
- Added SECURITY.md with vulnerability reporting guidelines and supported versions policy

### Fixed
- Fixed minimal_demo.py bug where `.iloc[0]` caused empty DataFrame errors when no data exists
- Corrected README.md code example to use `.iloc[0]` for proper single-row access instead of `[0]`
- Improved error handling in demo applications

### Changed
- Updated yfinance requirement to >=1.0 to avoid Yahoo Finance API rate limiting issues
- Upgraded lightweight-charts to version 5.1.0 (from 5.0.0)
- Synchronized version numbers across all project files (package.json, setup.py, __init__.py)

### Added
- Implemented setStretchFactor() API for advanced chart layout control
- Enhanced TestPyPI deployment workflow documentation in DEVELOP_AND_DEPLOY.txt

## 0.1.7 (2025-06-20)

### Security
- **CRITICAL**: Removed vulnerable "build" package containing js-yaml < 3.13.1 (code injection vulnerability)
- **HIGH**: Eliminated timespan package RegEx DoS vulnerability (no patch available)
- **CRITICAL**: Fixed uglify-js RegEx DoS vulnerability
- Resolved multiple dependency security issues without breaking functionality

### Changed
- Streamlined dependencies by removing unnecessary "build" package
- Component functionality fully preserved and tested with demo applications
- Updated all version numbers to maintain consistency across project files

## 0.1.6 (2025-04-12)

### Fixed
- Fixed window resize detection issue that was preventing charts from resizing properly
- Eliminated flickering during resize operations
- Improved resize handling with requestAnimationFrame for smoother performance
- Reduced MIN_RESIZE_INTERVAL from 1000ms to 500ms for more responsive resizing

### Changed
- Simplified ResizeObserver implementation for more reliable resize detection
- Improved debounce mechanism in handleResize function