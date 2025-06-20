# Changelog

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