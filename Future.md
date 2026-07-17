# Future Work — Marker API Enhancements

Not scheduled. Captured from a design discussion about encoding trading-ranker
metadata (medal tier, gate status) in chart markers.

## Context

The current `createSeriesMarkers()` call in `LightweightChartsComponent.tsx`
works correctly but exposes only a minimal subset of the v5 marker API. Two
gaps block richer marker styling from the Python side:

1. The `SeriesMarker` TypeScript interface is missing `size` and `id`.
2. The third argument of `createSeriesMarkers(series, markers, options?)` is
   never passed, so `zOrder` and `autoScale` are not configurable.

Reference: `lightweight_charts_v5/frontend/src/LightweightChartsComponent.tsx`
lines 63-69 (interface) and 380-394 (call site).

## Plan

### 1. Extend the `SeriesMarker` interface

Add two optional fields:

```typescript
interface SeriesMarker {
  time: string
  position: "aboveBar" | "belowBar" | "inBar"
  color: string
  shape: "circle" | "square" | "arrowUp" | "arrowDown"
  text: string
  size?: number   // v5 default 1; used to scale marker (e.g. medal tier)
  id?: string     // v5 marker id; required for click-handler routing
}
```

- `size` passes straight through to the v5 plugin — no wrapper logic needed.
- `id` likewise; only meaningful once a click handler is wired up (not part of
  this plan, but cheap to expose now).

No Python-side API break: both fields are optional dict keys.

### 2. Expose marker plugin `options`

Add an optional per-series `markerOptions` config object alongside `markers`:

```typescript
interface SeriesMarkerOptions {
  zOrder?: "top" | "normal" | "bottom"
  autoScale?: boolean
}

interface SeriesConfig {
  // ...existing fields...
  markers?: SeriesMarker[]
  markerOptions?: SeriesMarkerOptions
}
```

Pass it through at the call site:

```typescript
createSeriesMarkers(
  seriesInstances[paneIndex][seriesIndex],
  s.markers,
  s.markerOptions   // undefined is safe; plugin uses defaults
)
```

Defaults (if omitted) match v5 library defaults — no behavior change for
existing users.

### 3. Optional: sort markers by time before passing through

Lightweight-charts requires time-ascending markers or rendering breaks
silently. Current implementation trusts callers. Add a defensive sort in the
Python wrapper (`lightweight_charts_v5/__init__.py`) before serializing:

```python
if "markers" in series and series["markers"]:
    series["markers"] = sorted(series["markers"], key=lambda m: m["time"])
```

Cheap, prevents a class of silent bugs.

### 4. Optional: retain the plugin handle

Store the return value of `createSeriesMarkers()` so in-place marker updates
become possible without a full chart rebuild:

```typescript
const markerPluginsRef = useRef<ISeriesMarkersPluginApi<Time>[]>([])
// ...
const plugin = createSeriesMarkers(series, s.markers, s.markerOptions)
markerPluginsRef.current.push(plugin)
```

No leak risk today (chart.remove() cascades), so this is a pure ergonomics
improvement — defer until a concrete use case appears (e.g. a "toggle
sub-Bronze markers" UI control that should not re-render the whole chart).

## Scope / Non-Goals

- No price-based position variants (`atPriceTop` / `atPriceBottom` /
  `atPriceMiddle`) — not needed for current use cases.
- No marker click handler — `id` is exposed for future use only.
- No Python-side helper for medal-tier → size/color mapping; that belongs in
  the trading-lab repo (caller side), not here.

## Version impact

- Minor version bump (new optional fields, fully backwards compatible).
- CHANGELOG entry under "Added".
- Update demo showing `size` + `zOrder` to verify end-to-end.

## Estimated effort

~1-2 hours including demo update and manual test. No frontend architectural
changes.
