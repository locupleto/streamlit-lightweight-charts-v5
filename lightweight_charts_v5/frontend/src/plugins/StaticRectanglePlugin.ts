// StaticRectanglePlugin.ts
import { CanvasRenderingTarget2D } from 'fancy-canvas';
import {
  Coordinate,
  IChartApi,
  ISeriesApi,
  IPrimitivePaneRenderer,
  IPrimitivePaneView,
  ISeriesPrimitive,
  SeriesType,
  Time,
} from 'lightweight-charts';

// Define the rectangle properties that will be passed from Python
export interface RectangleOptions {
    startTime: Time;
    startPrice: number;
    endTime: Time;
    endPrice: number;
    fillColor: string;
    borderColor?: string;
    borderWidth?: number;
    opacity?: number;
    zOrder?: 'top' | 'bottom'; // Just 'top' or 'bottom'
  }

class RectanglePaneRenderer implements IPrimitivePaneRenderer {
  _p1: { x: Coordinate | null; y: Coordinate | null };
  _p2: { x: Coordinate | null; y: Coordinate | null };
  _fillColor: string;
  _borderColor: string | undefined;
  _borderWidth: number;
  _opacity: number;

  constructor(
    p1: { x: Coordinate | null; y: Coordinate | null },
    p2: { x: Coordinate | null; y: Coordinate | null },
    fillColor: string,
    borderColor?: string,
    borderWidth?: number,
    opacity?: number
  ) {
    this._p1 = p1;
    this._p2 = p2;
    this._fillColor = fillColor;
    this._borderColor = borderColor;
    this._borderWidth = borderWidth || 0;
    this._opacity = opacity !== undefined ? opacity : 0.75;
  }

  draw(target: CanvasRenderingTarget2D) {
    target.useBitmapCoordinateSpace(scope => {
      if (
        this._p1.x === null ||
        this._p1.y === null ||
        this._p2.x === null ||
        this._p2.y === null
      ) {
        return;
      }
  
      const ctx = scope.context;
  
      // Calculate positions with proper scaling
      const x1 = Math.round(this._p1.x * scope.horizontalPixelRatio);
      const y1 = Math.round(this._p1.y * scope.verticalPixelRatio);
      const x2 = Math.round(this._p2.x * scope.horizontalPixelRatio);
      const y2 = Math.round(this._p2.y * scope.verticalPixelRatio);
  
      // Calculate rectangle dimensions
      const left = Math.min(x1, x2);
      const top = Math.min(y1, y2);
      const width = Math.abs(x2 - x1);
      const height = Math.abs(y2 - y1);
  
      // Save current context state
      ctx.save();
  
      // Set global alpha for opacity
      ctx.globalAlpha = this._opacity;
  
      // Fill rectangle
      ctx.fillStyle = this._fillColor;
      ctx.fillRect(left, top, width, height);
  
      // Only draw border if borderWidth is greater than 0
      if (this._borderColor && this._borderWidth > 0) {
        const borderWidth = this._borderWidth * Math.max(scope.horizontalPixelRatio, scope.verticalPixelRatio);
        ctx.strokeStyle = this._borderColor;
        ctx.lineWidth = borderWidth;
  
        // Adjust the stroke rectangle to account for the border width
        const offset = borderWidth / 2;
        ctx.strokeRect(
          left + offset, 
          top + offset, 
          width - borderWidth, 
          height - borderWidth
        );
      }
  
      // Restore context state
      ctx.restore();
    });
  }
}

class StaticRectanglePaneView implements IPrimitivePaneView {
  _chart: IChartApi;
  _series: ISeriesApi<SeriesType>;
  _options: RectangleOptions;
  _p1: { x: Coordinate | null; y: Coordinate | null } = { x: null, y: null };
  _p2: { x: Coordinate | null; y: Coordinate | null } = { x: null, y: null };

  constructor(chart: IChartApi, series: ISeriesApi<SeriesType>, options: RectangleOptions) {
    this._chart = chart;
    this._series = series;
    this._options = options;
  }

  update() {
    // Get price coordinates
    const y1 = this._series.priceToCoordinate(this._options.startPrice);
    const y2 = this._series.priceToCoordinate(this._options.endPrice);

    // Get time coordinates
    const timeScale = this._chart.timeScale();
    const x1 = timeScale.timeToCoordinate(this._options.startTime);
    const x2 = timeScale.timeToCoordinate(this._options.endTime);

    // Update points
    this._p1 = { x: x1, y: y1 };
    this._p2 = { x: x2, y: y2 };
  }

  zOrder() {
    return this._options.zOrder || 'bottom'; // Default to bottom if not specified
  }

  renderer() {
    // Make sure coordinates are updated before rendering
    this.update();

    return new RectanglePaneRenderer(
      this._p1,
      this._p2,
      this._options.fillColor,
      this._options.borderColor,
      this._options.borderWidth,
      this._options.opacity
    );
  }
}

// This class implements ISeriesPrimitive<Time> interface
export class StaticRectangle implements ISeriesPrimitive<Time> {
  private _chart: IChartApi;
  private _series: ISeriesApi<SeriesType>;
  private _options: RectangleOptions;
  private _paneView: StaticRectanglePaneView;

  constructor(chart: IChartApi, series: ISeriesApi<SeriesType>, options: RectangleOptions) {
    this._chart = chart;
    this._series = series;
    this._options = options;
    this._paneView = new StaticRectanglePaneView(chart, series, options);

    // Attach the primitive to the series
    this._series.attachPrimitive(this);
  }

  // Required method for ISeriesPrimitive
  paneViews() {
    return [this._paneView];
  }

  // Method to update rectangle options
  setOptions(options: Partial<RectangleOptions>) {
    this._options = { ...this._options, ...options };
    this._paneView.update();
    this._chart.applyOptions({});  // Trigger a redraw
  }
}