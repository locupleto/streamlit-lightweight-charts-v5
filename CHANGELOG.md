# Changelog

## 0.1.6 (2025-04-12)

### Fixed
- Fixed window resize detection issue that was preventing charts from resizing properly
- Eliminated flickering during resize operations
- Improved resize handling with requestAnimationFrame for smoother performance
- Reduced MIN_RESIZE_INTERVAL from 1000ms to 500ms for more responsive resizing

### Changed
- Simplified ResizeObserver implementation for more reliable resize detection
- Improved debounce mechanism in handleResize function