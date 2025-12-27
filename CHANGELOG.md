# Changelog

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