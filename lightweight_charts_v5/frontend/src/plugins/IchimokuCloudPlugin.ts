// IchimokuCloudPlugin.ts — kumo (cloud) fill between Senkou Span A and B.
//
// lightweight-charts has no native "fill between two line series" (open
// feature request tradingview/lightweight-charts#140), so the cloud is a
// series primitive modeled on the official bands-indicator plugin example
// and our own StaticRectanglePlugin. Python attaches a `cloud` payload to
// a (typically transparent) carrier Line series config; this primitive maps
// each {time, a, b} point to pixel space and fills contiguous runs —
// bullColor where a >= b, bearColor where a < b — splitting polygons at the
// exact A/B crossover so colors never bleed across it.
import type { CanvasRenderingTarget2D } from 'fancy-canvas';
import type {
  IChartApi,
  ISeriesApi,
  IPrimitivePaneRenderer,
  IPrimitivePaneView,
  ISeriesPrimitive,
  SeriesType,
  Time,
} from 'lightweight-charts';

export interface IchimokuCloudOptions {
  points: { time: Time; a: number; b: number }[];
  bullColor: string;
  bearColor: string;
  /** Edge strokes for spans A and B — per SEGMENT, matching the fill's
   *  regime (green edges on green cloud, red on red). The Senkou Line
   *  series themselves are transparent carriers. */
  bullLineColor: string;
  bearLineColor: string;
  lineWidth: number;
}

interface CloudPoint {
  x: number;
  yA: number;
  yB: number;
  bull: boolean;
}

/** Split mapped points into same-color runs, inserting the interpolated
 *  crossover point at each color flip so adjacent fills share an exact seam. */
function buildRuns(pts: CloudPoint[]): { bull: boolean; pts: CloudPoint[] }[] {
  const runs: { bull: boolean; pts: CloudPoint[] }[] = [];
  let current: CloudPoint[] = [];
  let currentBull: boolean | null = null;

  for (const p of pts) {
    if (currentBull === null || p.bull === currentBull) {
      current.push(p);
      currentBull = p.bull;
      continue;
    }
    // Color flip between prev and p — interpolate the crossover in pixel
    // space (where yA - yB crosses zero on the segment).
    const prev = current[current.length - 1];
    const d0 = prev.yA - prev.yB;
    const d1 = p.yA - p.yB;
    const denom = d0 - d1;
    const t = denom === 0 ? 0.5 : d0 / denom;
    const xi = prev.x + (p.x - prev.x) * t;
    const yi = prev.yA + (p.yA - prev.yA) * t;
    const cross: CloudPoint = { x: xi, yA: yi, yB: yi, bull: p.bull };
    current.push(cross);
    runs.push({ bull: currentBull, pts: current });
    current = [cross, p];
    currentBull = p.bull;
  }
  if (current.length > 1 && currentBull !== null) {
    runs.push({ bull: currentBull, pts: current });
  }
  return runs;
}

class IchimokuCloudRenderer implements IPrimitivePaneRenderer {
  _segments: CloudPoint[][];
  _options: IchimokuCloudOptions;

  constructor(segments: CloudPoint[][], options: IchimokuCloudOptions) {
    this._segments = segments;
    this._options = options;
  }

  draw(target: CanvasRenderingTarget2D) {
    target.useBitmapCoordinateSpace((scope) => {
      const ctx = scope.context;
      const hr = scope.horizontalPixelRatio;
      const vr = scope.verticalPixelRatio;
      const lw = this._options.lineWidth * Math.max(hr, vr);
      ctx.save();
      ctx.lineJoin = 'round';
      for (const segment of this._segments) {
        for (const run of buildRuns(segment)) {
          if (run.pts.length < 2) continue;
          // Fill — colors carry their own alpha.
          ctx.beginPath();
          ctx.moveTo(run.pts[0].x * hr, run.pts[0].yA * vr);
          for (let i = 1; i < run.pts.length; i++) {
            ctx.lineTo(run.pts[i].x * hr, run.pts[i].yA * vr);
          }
          for (let i = run.pts.length - 1; i >= 0; i--) {
            ctx.lineTo(run.pts[i].x * hr, run.pts[i].yB * vr);
          }
          ctx.closePath();
          ctx.fillStyle = run.bull ? this._options.bullColor : this._options.bearColor;
          ctx.fill();

          // Edge strokes — BOTH span lines in the run's color.
          ctx.strokeStyle = run.bull ? this._options.bullLineColor : this._options.bearLineColor;
          ctx.lineWidth = lw;
          ctx.beginPath();
          ctx.moveTo(run.pts[0].x * hr, run.pts[0].yA * vr);
          for (let i = 1; i < run.pts.length; i++) {
            ctx.lineTo(run.pts[i].x * hr, run.pts[i].yA * vr);
          }
          ctx.stroke();
          ctx.beginPath();
          ctx.moveTo(run.pts[0].x * hr, run.pts[0].yB * vr);
          for (let i = 1; i < run.pts.length; i++) {
            ctx.lineTo(run.pts[i].x * hr, run.pts[i].yB * vr);
          }
          ctx.stroke();
        }
      }
      ctx.restore();
    });
  }
}

class IchimokuCloudPaneView implements IPrimitivePaneView {
  _chart: IChartApi;
  _series: ISeriesApi<SeriesType>;
  _options: IchimokuCloudOptions;
  _segments: CloudPoint[][] = [];

  constructor(chart: IChartApi, series: ISeriesApi<SeriesType>, options: IchimokuCloudOptions) {
    this._chart = chart;
    this._series = series;
    this._options = options;
  }

  update() {
    const timeScale = this._chart.timeScale();
    // A point that can't be mapped (off-scale time) breaks the polygon into
    // separate segments rather than bridging a gap with a straight edge.
    const segments: CloudPoint[][] = [];
    let current: CloudPoint[] = [];
    for (const p of this._options.points) {
      const x = timeScale.timeToCoordinate(p.time);
      const yA = this._series.priceToCoordinate(p.a);
      const yB = this._series.priceToCoordinate(p.b);
      if (x === null || yA === null || yB === null) {
        if (current.length > 1) segments.push(current);
        current = [];
        continue;
      }
      current.push({ x, yA, yB, bull: p.a >= p.b });
    }
    if (current.length > 1) segments.push(current);
    this._segments = segments;
  }

  zOrder() {
    return 'bottom' as const; // beneath the candles
  }

  renderer() {
    this.update();
    return new IchimokuCloudRenderer(this._segments, this._options);
  }
}

// Series primitive — attach to the Senkou A series (supplies the price scale).
export class IchimokuCloud implements ISeriesPrimitive<Time> {
  private _paneView: IchimokuCloudPaneView;

  constructor(chart: IChartApi, series: ISeriesApi<SeriesType>, options: IchimokuCloudOptions) {
    this._paneView = new IchimokuCloudPaneView(chart, series, options);
    series.attachPrimitive(this);
  }

  paneViews() {
    return [this._paneView];
  }

  updateAllViews() {
    this._paneView.update();
  }
}
