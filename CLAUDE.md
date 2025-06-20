# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend Development (TypeScript/React)
```bash
cd lightweight_charts_v5/frontend
npm install                    # Install dependencies
npm run build                  # Build the React component
npm start                      # Start development server on port 3001
```

### Python Package Development
```bash
pip install -e .               # Install package in editable mode
pip install -e .[devel]        # Install with development dependencies
pip install -e .[demo]         # Install with demo dependencies (yfinance, numpy)
```

### Testing
```bash
# Python tests (pytest available in devel extras)
pytest

# Frontend tests
cd lightweight_charts_v5/frontend
npm test
```

### Running Demos
```bash
streamlit run demo/minimal_demo.py    # Basic stock chart example
streamlit run demo/chart_demo.py      # Advanced multi-pane example with indicators
```

### Build and Release Process
```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build frontend first
cd lightweight_charts_v5/frontend
npm install && npm run build
cd ../..

# Build Python package
python -m pip install --upgrade build
python -m build
```

## Architecture Overview

This is a Streamlit component that wraps TradingView's Lightweight Charts v5 library for financial charting.

### Key Components

**Python Layer (`lightweight_charts_v5/`)**:
- `__init__.py`: Main component interface with `lightweight_charts_v5_component()` function
- Handles dev server detection (port 3001) vs production build switching
- Supports both single-pane (`data` param) and multi-pane (`charts` param) configurations

**Frontend Layer (`lightweight_charts_v5/frontend/`)**:
- `LightweightChartsComponent.tsx`: Core React component implementing multi-pane chart logic
- Built with React 16.13.1 and TypeScript
- Uses `lightweight-charts` v5.0.2 library
- Handles complex pane height initialization and window resize race conditions

**Demo Applications (`demo/`)**:
- Multiple example implementations showing various chart types and indicators
- Uses Yahoo Finance data via `yfinance` library

### Development Workflow

The component supports dual-mode development:
1. **Development**: Auto-detects if React dev server is running on port 3001
2. **Production**: Uses built static files from `frontend/build/`

### Key Technical Challenges Solved

1. **Pane Height Management**: Sequential bottom-to-top height setting with async delays
2. **Window Resize Handling**: Debounced resize events (800ms) with disposal state tracking
3. **Chart Disposal**: Proper cleanup to prevent "Object is disposed" errors during paint cycles

### Chart Configuration

Charts support:
- Multiple panes with synchronized time scales
- Various series types: Candlestick, Line, Area, Histogram, Bar
- Overlay indicators (moving averages, etc.)
- Rectangle drawing for support/resistance areas
- Screenshot functionality
- Custom themes and styling
- Google Fonts integration

## Mermaid Diagram Generation

### **When to Generate Diagrams**
When users request visual documentation or illustrations using terms like:
- "draw a diagram"
- "make me a mermaid diagram" 
- "illustrate for me"
- "show me a flowchart"
- "create a diagram showing..."
- Any request for visual representation of architecture, processes, or relationships

### **Standard Diagram Generation Process**
1. **Use the MCP Mermaid service** via `mcp__mermaid-diagram__generate_diagram`
2. **Always specify a descriptive file_name** (required parameter, without extension)
3. **Use dark theme for dark environments** or default theme for light environments
4. **Diagrams are automatically saved** with the specified filename and appropriate extension

### **Updated Implementation Pattern**
```python
# Generate Mermaid diagram with required file_name parameter
diagram_result = mcp__mermaid-diagram__generate_diagram(
    mermaid_code=mermaid_syntax,
    file_name="architecture-overview",  # REQUIRED: descriptive name without extension
    theme="dark",  # Use "dark" for dark environments, "default" for light environments
    format="svg",  # Default: svg, also supports png, pdf
    backgroundColor="transparent"  # Default: transparent (adapts to container theme)
    # Other parameters: width=1920, height=1080, scale=2
)

# File is automatically saved as: architecture-overview.svg
# For SVG format: Content is also returned for immediate embedding
# For PNG/PDF: Only file path is returned
```

### **Diagram Types to Support**
- **Architecture diagrams**: System components, data flow
- **Process flowcharts**: User workflows, business processes  
- **Class diagrams**: Code structure, inheritance relationships
- **Sequence diagrams**: Interaction flows, API calls
- **Entity relationship diagrams**: Database schemas
- **Network diagrams**: System topology, connections

### **Best Practices**
- **Generate appropriate Mermaid syntax** for the requested diagram type
- **Use descriptive filenames** that clearly identify the diagram content
- **Use clear, descriptive node labels** and relationships
- **Keep diagrams focused** - break complex systems into multiple diagrams
- **Include diagram title** and brief description in Mermaid code when helpful
- **Validate syntax** using `mcp__mermaid-diagram__validate_mermaid` if uncertain
- **Choose appropriate themes**: Use "dark" for dark IDE/GitHub environments, "default" for light environments

### **Theme Selection Guidelines**
- **Dark environments** (VS Code dark, GitHub dark mode): Use `theme="dark"`
- **Light environments** (VS Code light, GitHub light mode): Use `theme="default"`
- **GitHub repositories**: Use `theme="dark"` for better visibility across light/dark modes
- **Custom styling**: Combine any theme with specific background colors

**Important**: There is no universal theme that works in both light and dark environments. The "default" theme uses dark text/lines which are invisible in dark environments, while the "dark" theme uses light text/lines which may be hard to read in light environments. Always choose based on your target viewing environment.

## Security Vulnerability Management

### **Checking for Security Issues**
```bash
# Check GitHub Dependabot alerts
gh api repos/locupleto/streamlit-lightweight-charts-v5/dependabot/alerts

# Run npm security audit (from frontend directory)
cd lightweight_charts_v5/frontend
npm audit --audit-level=high

# Auto-fix non-breaking vulnerabilities
npm audit fix

# Fix breaking changes (use with caution)
npm audit fix --force
```

### **Critical Security Workflow**
When security vulnerabilities are found:

1. **Assess Impact**: Prioritize CRITICAL and HIGH severity issues first
2. **Identify Root Cause**: Check if vulnerable packages are actually needed
3. **Remove Unnecessary Packages**: Sometimes the best fix is removing unused dependencies
4. **Update Dependencies**: Use npm update for transitive dependencies
5. **Test Thoroughly**: Always test component functionality after security fixes
6. **Update Version Numbers**: Bump version for security releases

### **Known Security Issues Resolved**
- **v0.1.7**: Removed "build" package that contained critical vulnerabilities (js-yaml, timespan, uglify-js)
- The "build" package was unnecessary and conflicted with React's build script
- Always verify that packages in dependencies are actually required for the component

### **Testing After Security Fixes**
```bash
# Test frontend build
cd lightweight_charts_v5/frontend
npm run build

# Test dev server
npm start

# Test component functionality
streamlit run demo/minimal_demo.py
streamlit run demo/chart_demo.py
```

## Version Management

### **Version Synchronization Requirements**
This project requires version numbers to be synchronized across multiple files:

1. **setup.py** - Python package version (line 10)
2. **lightweight_charts_v5/__init__.py** - Component `__version__` variable (line 9)
3. **lightweight_charts_v5/frontend/package.json** - Frontend version (line 3)
4. **CHANGELOG.md** - Release documentation

### **Version Update Workflow**
When releasing a new version:

```bash
# 1. Update all version numbers consistently
# 2. Add CHANGELOG.md entry with detailed changes
# 3. Test all functionality
# 4. Build and verify
# 5. Commit with descriptive message
```

### **Semantic Versioning Guidelines**
- **Patch (0.1.x)**: Bug fixes, security updates, minor improvements
- **Minor (0.x.0)**: New features, significant enhancements
- **Major (x.0.0)**: Breaking changes, major architectural changes

**Security fixes should always increment at least the patch version** to ensure users can identify which versions contain security improvements.

### **Pre-Release Checklist**
- [ ] All version numbers synchronized
- [ ] CHANGELOG.md updated with clear release notes
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Component functionality tested with demo applications
- [ ] No high/critical security vulnerabilities (`npm audit`)
- [ ] All tests passing (if applicable)

### **Build and Release to PyPI Process**

This project has a complete automated build and release workflow to PyPI. The user has `.pypirc` configured with both test and production PyPI credentials.

#### **Step 1: Clean and Build**
```bash
# Clean previous build artifacts
rm -rf build/ dist/ streamlit_lightweight_charts_v5.egg-info/

# Build frontend React component
cd lightweight_charts_v5/frontend
npm install && npm run build
cd ../..

# Install/upgrade build tools
python -m pip install --upgrade build twine

# Build Python package
python -m build
```

#### **Step 2: Verify Build Output**
```bash
# Check built packages
ls -la dist/
# Should show:
# streamlit_lightweight_charts_v5-X.X.X-py3-none-any.whl
# streamlit_lightweight_charts_v5-X.X.X.tar.gz
```

#### **Step 3: Test on PyPI Test Server**
```bash
# Upload to PyPI test (requires .pypirc with testpypi section)
python -m twine upload --repository testpypi dist/streamlit_lightweight_charts_v5-X.X.X*

# Test installation from PyPI test
pip install --index-url https://test.pypi.org/simple/ streamlit-lightweight-charts-v5==X.X.X

# Verify package works
streamlit run demo/minimal_demo.py
```

#### **Step 4: Release to Production PyPI**
```bash
# Upload to production PyPI (requires .pypirc with pypi section)
python -m twine upload --repository pypi dist/streamlit_lightweight_charts_v5-X.X.X*

# Verify on PyPI
# Check: https://pypi.org/project/streamlit-lightweight-charts-v5/X.X.X/
```

#### **PyPI Configuration (.pypirc)**
The user has `~/.pypirc` configured with both test and production credentials:
```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = production_api_token_here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = test_api_token_here
```

#### **Build Validation**
The build process validates:
- Frontend compiles without errors (only linting warnings expected)
- Python package includes all necessary files (frontend build assets)
- Version numbers are consistent across all project files
- Component functionality preserved (tested via demo apps)
- Package uploads successfully to both test and production PyPI

#### **Post-Release Verification**
- [ ] Package appears on PyPI with correct version
- [ ] Installation works: `pip install streamlit-lightweight-charts-v5==X.X.X`
- [ ] Component functionality confirmed with demo applications
- [ ] No breaking changes introduced

## Project-Specific Considerations

### **Dependency Management Best Practices**
- **Avoid unnecessary packages**: Remove any package not directly used by the component
- **Check package.json regularly**: Ensure all dependencies are actually required
- **Prefer React ecosystem tools**: Use react-scripts for building rather than external build tools
- **Monitor package age**: Very old packages (like "build" 0.1.4 from 2013) often have security issues

### **Component Architecture Notes**
- **Dual-mode development**: Component automatically switches between dev server (port 3001) and production build
- **React version constraint**: Currently uses React 16.13.1 - updates should be tested carefully
- **Streamlit integration**: Uses streamlit-component-lib v2.0.0 for proper Streamlit integration
- **TradingView dependency**: Core functionality depends on lightweight-charts v5.0.2

### **Common Troubleshooting**
- **Port 3001 conflicts**: Kill existing processes with `lsof -ti:3001 | xargs kill -9`
- **Build package conflicts**: If "build" package reappears, remove it immediately
- **Version mismatches**: Always check all 4 version locations when issues arise
- **Yarn vs NPM**: This project uses NPM exclusively - stick to npm commands