from abc import ABC, abstractmethod
from typing import Dict, Any, List, Literal, Optional
import pandas as pd
import numpy as np
from lightweight_charts_v5.chart_themes import ChartTheme, ChartThemes

# Base stand-alone Indicator class (has its own pane)
class Indicator(ABC):
    def __init__(self, df: pd.DataFrame, height: int = None, theme: Optional[ChartTheme] = None):
        self.df = df
        self.height = height
        self.theme = theme or ChartThemes.light()  # Default to light theme if none provided

    @abstractmethod
    def calculate(self) -> None:
        pass

    @abstractmethod
    def pane(self) -> Dict[str, Any]:
        pass

    def get_chart_config(self) -> Dict[str, Any]:
        """Get base chart configuration with theme applied"""
        return self.theme.to_dict()

# Base Overlay indicator class (shares pane with a host indicator)
class OverlayIndicator(ABC):
    """Abstract base class for overlay indicators"""

    @abstractmethod
    def calculate(self) -> None:
        """Calculate indicator values"""
        pass

    @abstractmethod
    def get_series_configs(self) -> List[Dict[str, Any]]:
        """Returns a list of series configurations for overlay plotting"""
        pass

class PriceIndicator(Indicator):
    """
    An example price chart indicator that can display OHLC price data in 
    multiple styles. Supports candlestick, bar, and line representations of 
    price data, along with optional overlay indicators and markers.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing price data with columns:
        - date: datetime or string
        - open: float
        - high: float
        - low: float
        - close: float

    height : int, optional
        Height of the chart pane in pixels.

    style : Literal["Candlestick", "Bar", "Line"], default="Candlestick"
        Visual representation style for price data:
        - "Candlestick": Traditional Japanese candlestick chart
        - "Bar": OHLC bar chart
        - "Line": Simple line chart using close prices

    overlays : List[Any], optional
        List of technical overlay indicators (e.g., moving averages)
        that will be plotted on top of the price chart.

    markers : List[Dict[str, Any]], optional
        List of marker configurations for highlighting specific points.
        Each marker should be a dictionary with keys:
        - time: str (timestamp)
        - position: "aboveBar" | "belowBar" | "inBar"
        - color: str (CSS color)
        - shape: "circle" | "square" | "arrowUp" | "arrowDown"
        - text: str

    theme : ChartTheme, optional
        Theme configuration for customizing chart appearance.
        If not provided, defaults to light theme.

    Attributes
    ----------
    style : str
        Current chart style ("Candlestick", "Bar", or "Line")
    overlays : List
        List of active overlay indicators
    markers : List[Dict]
        List of active markers

    Methods
    -------
    calculate() -> None
        Calculates values for any overlay indicators

    pane() -> Dict[str, Any]
        Returns the complete pane configuration including:
        - Chart configuration
        - Main price series
        - Overlay indicators
        - Markers
        - Theme settings

    Notes
    -----
    - The chart's appearance is controlled by the provided theme
    - Overlay indicators are calculated and plotted in the order they are provided
    - For Line style, only closing prices are used
    - Markers can be used with any style to highlight specific points
    """
    def __init__(self, df: pd.DataFrame, height: int = None, 
                 title: Optional[str] = None,
                 style: Literal["Candlestick", "Bar", "Line"] = "Candlestick",
                 overlays: Optional[List[Any]] = None, 
                 markers: Optional[List[Dict[str, Any]]] = None,
                 theme: Optional[ChartTheme] = None):
        super().__init__(df, height, theme)
        self.style = style
        self.overlays = overlays or []
        self.markers = markers or []
        self.title = title or "<Add your own chart title>"

    def calculate(self) -> None:
        # Calculate any overlay indicators
        for overlay in self.overlays:
            overlay.calculate()

    def pane(self) -> Dict[str, Any]:
        # Prepare main price series data
        price_data = self.df[['date', 'open', 'high', 'low', 'close']].copy()
        price_data.rename(columns={'date': 'time'}, inplace=True)
        price_data['time'] = price_data['time'].astype(str)
        price_records = price_data.to_dict(orient="records")

        # Calculate percentage change from previous day's close
        last_close = self.df['close'].iloc[-1]
        prev_close = self.df['close'].iloc[-2]
        pct_change = ((last_close - prev_close) / prev_close) * 100
        pct_change_str = f" ({'+' if pct_change >= 0 else ''}{pct_change:.2f}%)"

        # Append percentage change to title
        display_title = f"{self.title}{pct_change_str}"

        # Configure series based on style
        if self.style == "Candlestick":
            series_config = {
                "type": "Candlestick",
                "data": price_records,
                "options": {
                    "upColor": "rgb(54,116,217)",
                    "downColor": "rgb(225,50,85)",
                    "borderVisible": False,
                    "wickUpColor": "rgb(54,116,217)",
                    "wickDownColor": "rgb(225,50,85)",
                    "priceLineVisible": False
                }
            }
        elif self.style == "Bar":
            series_config = {
                "type": "Bar",
                "data": price_records,
                "options": {
                    "upColor": "rgb(54,116,217)",
                    "downColor": "rgb(225,50,85)",
                    "thinBars": False,
                    "openVisible": True,
                    "priceLineVisible": False
                }
            }
        elif self.style == "Line":
            # For line chart, we only need close prices
            line_data = self.df[['date', 'close']].copy()
            line_data.rename(columns={'date': 'time', 'close': 'value'}, inplace=True)
            line_data['time'] = line_data['time'].astype(str)
            series_config = {
                "type": "Line",
                "data": line_data.to_dict(orient="records"),
                "options": {
                    "color": self.theme.primary_line_color,
                    "lineWidth": 2,
                    "priceLineVisible": False
                }
            }

        # Create base series configuration
        series_configs = [series_config]

        # Add overlay configurations
        for overlay in self.overlays:
            if hasattr(overlay, 'get_series_configs'):
                # Handle indicators that return multiple series
                series_configs.extend(overlay.get_series_configs())
            else:
                # Handle indicators that return a single series (backward compatibility)
                series_configs.append(overlay.get_series_config())

        # Add markers last if present (so they end up on-top)
        if self.markers:
            series_configs[0]["markers"] = self.markers

        # Get base chart config from theme
        chart_config = self.get_chart_config()

        return {
            "chart": chart_config,
            "series": series_configs,
            "height": self.height,
            "title": display_title
        }
class VolumeIndicator(Indicator):
    def calculate(self) -> None:
        pass

    def pane(self) -> Dict[str, Any]:
        volume_data = self.df[['date', 'open', 'close', 'volume']].copy()
        volume_data.rename(columns={'date': 'time'}, inplace=True)
        volume_data['time'] = volume_data['time'].astype(str)
        volume_data['color'] = np.where(
            volume_data['open'] <= volume_data['close'],
            "rgba(38,166,154,0.8)",
            "rgba(239,83,80,0.8)"
        )
        volume_records = (volume_data[['time', 'volume', 'color']]
                         .rename(columns={'volume': 'value'})
                         .to_dict(orient="records"))

        # Get base chart config from theme
        chart_config = self.get_chart_config()

        return {
            "chart": {
                **chart_config,
                "height": self.height,
            },
            "series": [
                {
                    "type": "Histogram",
                    "data": volume_records,
                    "options": {
                        "color": "rgba(38,166,154,0.8)",
                        "priceFormat": {"type": "volume"},
                        "priceLineVisible": False
                    },
                    "priceScale": {
                        "scaleMargins": {"top": 0.8, "bottom": 0},
                        "independent": True,
                        "alignLabels": True,
                    }
                }
            ],
            "height": self.height,
            "title": "Volume"  # Add this line
        }
    
class SMAIndicator(OverlayIndicator):
    """
    Simple Moving Average indicator designed to be used as an overlay.
    Not derived from Indicator base class as it's not a separate pane indicator.
    """
    def __init__(self, df: pd.DataFrame, period: int = 20, color: str = "rgba(255, 140, 0, 0.8)"):
        self.df = df
        self.period = period
        self.color = color
        self.name = f'SMA({period})'

    def calculate(self) -> None:
        self.df[f'SMA_{self.period}'] = self.df['close'].rolling(window=self.period).mean()

    def get_series_config(self) -> Dict[str, Any]:
        """Returns the series configuration for overlay plotting (backward compatibility)"""
        return self.get_series_configs()[0]

    def get_series_configs(self) -> List[Dict[str, Any]]:
        """Returns a list of series configurations for overlay plotting"""
        sma_data = self.df[['date', f'SMA_{self.period}']].copy()
        sma_data.rename(columns={'date': 'time', f'SMA_{self.period}': 'value'}, inplace=True)
        sma_data['time'] = sma_data['time'].astype(str)
        sma_data = sma_data[sma_data['value'].notnull()]

        return [{
            "type": "Line",
            "data": sma_data.to_dict(orient="records"),
            "options": {
                "color": self.color,
                "lineWidth": 2,
                "priceLineVisible": False,
                "lastValueVisible": False,
            },
            "label": self.name
        }]
    
class MACDIndicator(Indicator):
    """
    Moving Average Convergence Divergence (MACD) indicator.

    Displays the MACD as a histogram with color-coded bars (green for positive, red for negative)
    and includes a zero line reference.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing price data with at least a 'close' column

    height : int, optional
        Height of the chart pane in pixels

    fast_period : int, default=12
        Period for the fast EMA calculation

    slow_period : int, default=26
        Period for the slow EMA calculation

    signal_period : int, default=9
        Period for the signal line calculation

    theme : ChartTheme, optional
        Theme configuration for customizing chart appearance

    Methods
    -------
    calculate() -> None
        Calculates MACD values based on configured periods

    pane() -> Dict[str, Any]
        Returns the complete pane configuration for the MACD histogram

    get_last_update() -> Dict[str, Any]
        Returns data for the last bar for real-time updates
    """
    def __init__(self, df: pd.DataFrame, height: int = None, 
                 fast_period: int = 12, slow_period: int = 26, signal_period: int = 9,
                 theme: Optional[ChartTheme] = None):
        super().__init__(df, height, theme)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self) -> None:
        # Calculate fast and slow EMAs
        self.df['EMA_fast'] = self.df['close'].ewm(span=self.fast_period, adjust=False).mean()
        self.df['EMA_slow'] = self.df['close'].ewm(span=self.slow_period, adjust=False).mean()

        # Calculate MACD line and signal line
        self.df['MACD'] = self.df['EMA_fast'] - self.df['EMA_slow']
        self.df['MACD_signal'] = self.df['MACD'].ewm(span=self.signal_period, adjust=False).mean()

        # Calculate histogram (MACD - signal)
        self.df['MACD_hist'] = self.df['MACD'] - self.df['MACD_signal']

    def pane(self) -> Dict[str, Any]:
        # Prepare MACD histogram data
        macd_data = self.df[['date', 'MACD_hist']].copy()
        macd_data.rename(columns={'date': 'time', 'MACD_hist': 'value'}, inplace=True)
        macd_data['time'] = macd_data['time'].astype(str)

        # Add color based on value (green for positive, red for negative)
        macd_data['color'] = np.where(
            macd_data['value'] >= 0,
            "rgba(0,255,0,0.8)",  # Green for positive values
            "rgba(255,0,80,0.8)"    # Red for negative values
        )

        # Filter out NaN values
        macd_data = macd_data[macd_data['value'].notnull()]
        macd_records = macd_data.to_dict(orient="records")

        # Create zero line data
        zero_line_data = self.df[['date']].copy()
        zero_line_data.rename(columns={'date': 'time'}, inplace=True)
        zero_line_data['time'] = zero_line_data['time'].astype(str)
        zero_line_data['value'] = 0
        zero_line_records = zero_line_data.to_dict(orient="records")

        # Get base chart config from theme
        chart_config = self.get_chart_config()
        chart_config["timeScale"] = {"visible": False}

        return {
            "chart": chart_config,
            "series": [
                {
                    "type": "Histogram",
                    "data": macd_records,
                    "options": {
                        "color": "rgba(38,166,154,0.8)",
                        "priceFormat": {
                            "type": 'price',
                            "precision": 4,
                            "minMove": 0.0001,
                        },
                        "priceLineVisible": False,
                        "lastValueVisible": True,
                    },
                    "priceScale": {
                        "scaleMargins": {
                            "top": 0.2,
                            "bottom": 0.2
                        },
                    },
                    "label": f"MACD({self.fast_period},{self.slow_period},{self.signal_period})"
                },
                {
                    "type": "Line",
                    "data": zero_line_records,
                    "options": {
                        "color": "rgba(120, 120, 120, 0.8)",  
                        "lineWidth": 1,
                        "lineStyle": 1,
                        "priceLineVisible": False,
                        "lastValueVisible": False,
                    }
                }
            ],
            "height": self.height,
            "title": f"MACD({self.fast_period},{self.slow_period},{self.signal_period})"
        }

class RSIIndicator(Indicator):
    def __init__(self, df: pd.DataFrame, height: int = None, window: int = 14, theme: Optional[ChartTheme] = None):
        super().__init__(df, height, theme)
        self.window = window

    def calculate(self) -> None:
        delta = self.df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=self.window, min_periods=self.window).mean()
        avg_loss = loss.rolling(window=self.window, min_periods=self.window).mean()
        rs = avg_gain / avg_loss
        self.df['RSI_14'] = 100 - (100 / (1 + rs))

    def pane(self) -> Dict[str, Any]:
        rsi_data = self.df[['date', 'RSI_14']].copy()
        rsi_data.rename(columns={'date': 'time', 'RSI_14': 'value'}, inplace=True)
        rsi_data['time'] = rsi_data['time'].astype(str)
        rsi_data = rsi_data[rsi_data['value'].notnull()]
        rsi_records = rsi_data.to_dict(orient="records")

        # Get base chart config from theme
        chart_config = self.get_chart_config()
        chart_config["timeScale"] = {"visible": False}

        return {
            "chart": chart_config,
            "series": [
                {
                    "type": "Area",
                    "data": rsi_records,
                    "options": {
                        "lineColor": "rgba(0, 0, 255, 1)",
                        "topColor": "rgba(0, 0, 255, 0.4)",
                        "bottomColor": "rgba(0, 0, 255, 0.0)",
                        "lineWidth": 2,
                        "priceFormat": {
                            "type": 'price',
                            "precision": 2,
                            "minMove": 0.01,
                        },
                        "priceLineVisible": False,
                    },
                    "priceScale": {
                        "scaleMargins": {
                            "top": 0.1,
                            "bottom": 0.1
                        },
                    },
                    "label": "RSI(14)"
                }
            ],
            "height": self.height,
            "title": "RSI(14)"  
        }

class WilliamsRIndicator(Indicator):
    def __init__(self, df: pd.DataFrame, height: int = None, period: int = 14, theme: Optional[ChartTheme] = None):
        super().__init__(df, height, theme)
        self.period = period

    def calculate(self) -> None:
        highest_high = self.df['high'].rolling(window=self.period).max()
        lowest_low = self.df['low'].rolling(window=self.period).min()
        self.df['Williams_R'] = -100 * (highest_high - self.df['close']) / (highest_high - lowest_low)

    def pane(self) -> Dict[str, Any]:
        williams_data = self.df[['date', 'Williams_R']].copy()
        williams_data.rename(columns={'date': 'time', 'Williams_R': 'value'}, inplace=True)
        williams_data['time'] = williams_data['time'].astype(str)
        williams_data = williams_data[williams_data['value'].notnull()]
        williams_records = williams_data.to_dict(orient="records")

        # Get base chart config from theme
        chart_config = self.get_chart_config()
        chart_config["timeScale"] = {"visible": False}

        return {
            "chart": chart_config,
            "series": [
                {
                    "type": "Line",
                    "data": williams_records,
                    "options": {
                        "color": "purple",
                        "lineWidth": 2,
                        "priceFormat": {
                            "type": 'price',
                            "precision": 2,
                            "minMove": 0.01,
                        },
                        "priceLineVisible": False
                    },
                    "priceScale": {
                        "scaleMargins": {
                            "top": 0.1,
                            "bottom": 0.1
                        },
                    },
                    "label": "Williams %R(14)"
                }
            ],
            "height": self.height,
            "title": "Williams %R(14)"  # Add this line
        }

class AVWAPIndicator(OverlayIndicator):
    """
    Anchored Volume Weighted Average Price (AVWAP) indicator.

    This indicator calculates VWAP values anchored to pivot points in the data,
    supporting both high and low pivots. It's designed to be used as an overlay
    on price charts.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing price and volume data

    left_strength : int, default=3
        Number of bars to the left required for pivot point detection

    right_strength : int, default=3
        Number of bars to the right required for pivot point detection

    color_high : str, default="rgba(255, 82, 82, 0.9)"
        Color for VWAP lines anchored to high pivots

    color_low : str, default="rgba(76, 175, 80, 0.9)"
        Color for VWAP lines anchored to low pivots

    line_width : int, default=3
        Width of VWAP lines

    realistic_mode : bool, default=False
        If True, only shows VWAP segments after pivot confirmation

    show_pivot_high : bool, default=True
        Whether to show VWAP lines anchored to high pivots

    show_pivot_low : bool, default=True
        Whether to show VWAP lines anchored to low pivots
    """
    def __init__(self, 
                 df: pd.DataFrame,
                 left_strength: int = 3, 
                 right_strength: int = 3,
                 color_high: str = "rgba(255, 82, 82, 0.9)",
                 color_low: str = "rgba(76, 175, 80, 0.9)",
                 line_width: int = 3,
                 realistic_mode: bool = False,
                 show_pivot_high: bool = True,
                 show_pivot_low: bool = True):
        self.df = df
        self.left_strength = left_strength
        self.right_strength = right_strength
        self.realistic_mode = realistic_mode
        self.show_pivot_high = show_pivot_high
        self.show_pivot_low = show_pivot_low

        self.colors = {
            'pivot_high': color_high,
            'pivot_low': color_low
        }

        self.line_width = line_width

        # Output column names
        self.output_columns = [
            f"AVWAP_high_{self.left_strength}_{self.right_strength}",
            f"AVWAP_low_{self.left_strength}_{self.right_strength}"
        ]

        # Initialize pivot indices
        self.pivot_high_indices = []
        self.pivot_low_indices = []

        # Calculate on initialization
        self.calculate()

    def _find_pivots(self, series: pd.Series, pivot_type: str = 'high') -> List[int]:
        """Find pivot points in the series."""
        if len(series) < (self.left_strength + self.right_strength + 1):
            return []

        pivots = []
        for i in range(self.left_strength, len(series) - self.right_strength):
            try:
                if pivot_type == 'high':
                    # Use iloc to avoid FutureWarning
                    if all(series.iloc[i] > series.iloc[i - j] for j in range(1, self.left_strength + 1)) and \
                       all(series.iloc[i] > series.iloc[i + j] for j in range(1, self.right_strength + 1)):
                        pivots.append(i)
                else:
                    # Use iloc to avoid FutureWarning
                    if all(series.iloc[i] < series.iloc[i - j] for j in range(1, self.left_strength + 1)) and \
                       all(series.iloc[i] < series.iloc[i + j] for j in range(1, self.right_strength + 1)):
                        pivots.append(i)
            except (IndexError, KeyError):
                continue
        return pivots

    def _calculate_anchored_vwap(self, df: pd.DataFrame, start_idx: int, end_idx: int, pivot_type: str = 'high') -> np.ndarray:
        """
        Calculate VWAP values anchored at a specific point
        """
        segment = df.iloc[start_idx:end_idx]

        # Use the appropriate price based on pivot type
        if pivot_type == 'high':
            # For pivot highs, anchor to the high price
            cumulative_pv = segment['high'] * segment['volume']
        else:
            # For pivot lows, anchor to the low price
            cumulative_pv = segment['low'] * segment['volume']

        cumulative_volume = segment['volume']

        cumulative_pv = cumulative_pv.cumsum()
        cumulative_volume = cumulative_volume.cumsum()

        # Avoid division by zero
        vwap = np.where(cumulative_volume != 0, 
                        cumulative_pv / cumulative_volume, 
                        np.nan)
        return vwap

    def calculate(self) -> None:
        """Calculate indicator values"""
        try:
            # Find pivot points
            self.pivot_high_indices = self._find_pivots(self.df['high'], 'high')
            self.pivot_low_indices = self._find_pivots(self.df['low'], 'low')

            # Initialize AVWAP columns with NaN
            for col_name in self.output_columns:
                self.df[col_name] = np.nan

            # Calculate VWAP for high pivots
            for i in range(len(self.pivot_high_indices)):
                start_idx = self.pivot_high_indices[i]

                if self.realistic_mode:
                    # In realistic mode, always continue to the end of data
                    end_idx = len(self.df)
                else:
                    # In normal mode, end at next pivot or end of data
                    end_idx = (self.pivot_high_indices[i + 1] 
                            if i + 1 < len(self.pivot_high_indices) 
                            else len(self.df))

                if self.realistic_mode:
                    # In realistic mode, start plotting only after right_strength bars
                    plot_start_idx = start_idx + self.right_strength
                else:
                    # In normal mode, start plotting from the pivot point
                    plot_start_idx = start_idx

                # Calculate VWAP values for this segment
                vwap_values = self._calculate_anchored_vwap(self.df, start_idx, end_idx, 'high')

                # In realistic mode, we only plot from when we know it's a pivot
                self.df.loc[self.df.index[plot_start_idx:end_idx], self.output_columns[0]] = vwap_values[plot_start_idx-start_idx:]

            # Calculate VWAP for low pivots
            for i in range(len(self.pivot_low_indices)):
                start_idx = self.pivot_low_indices[i]

                if self.realistic_mode:
                    # In realistic mode, always continue to the end of data
                    end_idx = len(self.df)
                else:
                    # In normal mode, end at next pivot or end of data
                    end_idx = (self.pivot_low_indices[i + 1] 
                            if i + 1 < len(self.pivot_low_indices) 
                            else len(self.df))

                if self.realistic_mode:
                    # In realistic mode, start plotting only after right_strength bars
                    plot_start_idx = start_idx + self.right_strength
                else:
                    # In normal mode, start plotting from the pivot point
                    plot_start_idx = start_idx

                # Calculate VWAP values for this segment
                vwap_values = self._calculate_anchored_vwap(self.df, start_idx, end_idx, 'low')

                # In realistic mode, we only plot from when we know it's a pivot
                self.df.loc[self.df.index[plot_start_idx:end_idx], self.output_columns[1]] = vwap_values[plot_start_idx-start_idx:]

        except Exception as e:
            print(f"Error in AVWAP calculate: {str(e)}")

    def get_series_config(self) -> Dict[str, Any]:
        """
        Returns a single series configuration for backward compatibility.
        """
        # For backward compatibility, return the first series from get_series_configs
        configs = self.get_series_configs()
        if configs:
            return configs[0]

        # Return an empty series if no data is available
        return {
            "type": "Line",
            "data": [],
            "options": {
                "color": self.colors['pivot_high'],
                "lineWidth": self.line_width,
                "priceLineVisible": False,
                "lastValueVisible": False,
            },
            "label": f"AVWAP({self.left_strength},{self.right_strength})"
        }

    def get_series_configs(self) -> List[Dict[str, Any]]:
        """Returns a list of series configurations for overlay plotting"""
        series_configs = []

        # Process high VWAP segments if they should be shown
        if self.show_pivot_high:
            for i in range(len(self.pivot_high_indices)):
                start_idx = self.pivot_high_indices[i]

                if not self.realistic_mode:
                    if i < len(self.pivot_high_indices) - 1:
                        end_idx = self.pivot_high_indices[i + 1]
                    else:
                        end_idx = len(self.df)

                    # 1. Dashed line (first right_strength bars)
                    dashed_segment_data = []
                    for idx in range(start_idx, min(start_idx + self.right_strength, end_idx)):
                        if idx < len(self.df):
                            value = self.df[self.output_columns[0]].iloc[idx]
                            if pd.notna(value):
                                dashed_segment_data.append({
                                    "time": str(self.df['date'].iloc[idx]),
                                    "value": value
                                })

                    if dashed_segment_data:
                        series_configs.append({
                            "type": "Line",
                            "data": dashed_segment_data,
                            "options": {
                                "color": self.colors['pivot_high'],
                                "lineWidth": self.line_width,
                                "lineStyle": 2,  # Dashed line
                                "lastValueVisible": False,
                                "priceLineVisible": False
                            }
                        })

                    # 2. Solid line (after right_strength bars)
                    solid_segment_data = []
                    for idx in range(start_idx + self.right_strength, end_idx):
                        if idx < len(self.df):
                            value = self.df[self.output_columns[0]].iloc[idx]
                            if pd.notna(value):
                                solid_segment_data.append({
                                    "time": str(self.df['date'].iloc[idx]),
                                    "value": value
                                })

                    if solid_segment_data:
                        series_configs.append({
                            "type": "Line",
                            "data": solid_segment_data,
                            "options": {
                                "color": self.colors['pivot_high'],
                                "lineWidth": self.line_width,
                                "lineStyle": 0,  # Solid line
                                "lastValueVisible": False,
                                "priceLineVisible": False
                            }
                        })
                else:
                    # Realistic mode - only show from confirmation onwards
                    if i < len(self.pivot_high_indices) - 1:
                        end_idx = self.pivot_high_indices[i + 1] + self.right_strength
                    else:
                        end_idx = len(self.df)

                    segment_data = []
                    for idx in range(start_idx + self.right_strength, end_idx):
                        if idx < len(self.df):
                            value = self.df[self.output_columns[0]].iloc[idx]
                            if pd.notna(value):
                                segment_data.append({
                                    "time": str(self.df['date'].iloc[idx]),
                                    "value": value
                                })

                    if segment_data:
                        series_configs.append({
                            "type": "Line",
                            "data": segment_data,
                            "options": {
                                "color": self.colors['pivot_high'],
                                "lineWidth": self.line_width,
                                "lastValueVisible": False,
                                "priceLineVisible": False
                            }
                        })

        # Process low VWAP segments if they should be shown
        if self.show_pivot_low:
            for i in range(len(self.pivot_low_indices)):
                start_idx = self.pivot_low_indices[i]

                if not self.realistic_mode:
                    if i < len(self.pivot_low_indices) - 1:
                        end_idx = self.pivot_low_indices[i + 1]
                    else:
                        end_idx = len(self.df)

                    # 1. Dashed line (first right_strength bars)
                    dashed_segment_data = []
                    for idx in range(start_idx, min(start_idx + self.right_strength, end_idx)):
                        if idx < len(self.df):
                            value = self.df[self.output_columns[1]].iloc[idx]
                            if pd.notna(value):
                                dashed_segment_data.append({
                                    "time": str(self.df['date'].iloc[idx]),
                                    "value": value
                                })

                    if dashed_segment_data:
                        series_configs.append({
                            "type": "Line",
                            "data": dashed_segment_data,
                            "options": {
                                "color": self.colors['pivot_low'],
                                "lineWidth": self.line_width,
                                "lineStyle": 2,  # Dashed line
                                "lastValueVisible": False,
                                "priceLineVisible": False
                            }
                        })

                    # 2. Solid line (after right_strength bars)
                    solid_segment_data = []
                    for idx in range(start_idx + self.right_strength, end_idx):
                        if idx < len(self.df):
                            value = self.df[self.output_columns[1]].iloc[idx]
                            if pd.notna(value):
                                solid_segment_data.append({
                                    "time": str(self.df['date'].iloc[idx]),
                                    "value": value
                                })

                    if solid_segment_data:
                        series_configs.append({
                            "type": "Line",
                            "data": solid_segment_data,
                            "options": {
                                "color": self.colors['pivot_low'],
                                "lineWidth": self.line_width,
                                "lineStyle": 0,  # Solid line
                                "lastValueVisible": False,
                                "priceLineVisible": False
                            }
                        })
                else:
                    # Realistic mode - only show from confirmation onwards
                    if i < len(self.pivot_low_indices) - 1:
                        end_idx = self.pivot_low_indices[i + 1] + self.right_strength
                    else:
                        end_idx = len(self.df)

                    segment_data = []
                    for idx in range(start_idx + self.right_strength, end_idx):
                        if idx < len(self.df):
                            value = self.df[self.output_columns[1]].iloc[idx]
                            if pd.notna(value):
                                segment_data.append({
                                    "time": str(self.df['date'].iloc[idx]),
                                    "value": value
                                })

                    if segment_data:
                        series_configs.append({
                            "type": "Line",
                            "data": segment_data,
                            "options": {
                                "color": self.colors['pivot_low'],
                                "lineWidth": self.line_width,
                                "lastValueVisible": False,
                                "priceLineVisible": False
                            }
                        })

        return series_configs
 
class PivotHighIndicator(OverlayIndicator):
    """
    Pivot High indicator that identifies pivot high points and draws horizontal lines
    from those points until price closes above them or a new pivot high is confirmed.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing price data with columns:
        - date: datetime or string
        - high: float
        - close: float

    left_strength : int, default=5
        Number of bars to the left that must be lower than the pivot bar.

    right_strength : int, default=5
        Number of bars to the right that must be lower than the pivot bar.

    color : str, default="rgba(255, 165, 0, 1)"
        Color of the pivot high lines (default is dark yellow/orange).

    line_width : int, default=2
        Width of the pivot high lines.

    realistic_mode : bool, default=False
        If True, only plots the line after the pivot is confirmed (right_strength bars later).
        If False, plots the line from the actual pivot point with dashed line during confirmation period.
    """
    def __init__(self, 
                 df: pd.DataFrame,
                 left_strength: int = 20, 
                 right_strength: int = 5,
                 color: str = "rgba(255, 165, 0, 1)",  # Darker yellow/orange
                 line_width: int = 3,
                 realistic_mode: bool = False):
        self.df = df
        self.left_strength = left_strength
        self.right_strength = right_strength
        self.color = color
        self.line_width = line_width
        self.realistic_mode = realistic_mode
        self.name = f'PivotHigh({left_strength},{right_strength})'

        # Output column name
        self.output_column = f"PivotHigh_{self.left_strength}_{self.right_strength}"

        # Initialize pivot indices
        self.pivot_high_indices = []

        # Calculate on initialization
        self.calculate()

    def _find_pivots(self) -> List[int]:
        """Find pivot high points in the series."""
        if len(self.df) < (self.left_strength + self.right_strength + 1):
            return []

        pivots = []
        for i in range(self.left_strength, len(self.df) - self.right_strength):
            try:
                # Use iloc to avoid FutureWarning
                if all(self.df['high'].iloc[i] > self.df['high'].iloc[i - j] for j in range(1, self.left_strength + 1)) and \
                   all(self.df['high'].iloc[i] > self.df['high'].iloc[i + j] for j in range(1, self.right_strength + 1)):
                    pivots.append(i)
            except (IndexError, KeyError):
                continue
        return pivots

    def calculate(self) -> None:
        """Calculate indicator values"""
        try:
            # Find pivot points
            self.pivot_high_indices = self._find_pivots()

            # Initialize column with NaN
            self.df[self.output_column] = np.nan

            # Process each pivot high
            for i in range(len(self.pivot_high_indices)):
                pivot_idx = self.pivot_high_indices[i]
                pivot_price = self.df['high'].iloc[pivot_idx]

                # Determine start point based on realistic_mode
                if self.realistic_mode:
                    # In realistic mode, start plotting only after right_strength bars
                    plot_start_idx = pivot_idx + self.right_strength
                else:
                    # In normal mode, start plotting from the pivot point
                    plot_start_idx = pivot_idx

                # Find where price closes above the pivot high or a new pivot is confirmed
                end_idx = None

                # Check for price closing above pivot high
                for j in range(plot_start_idx + 1, len(self.df)):
                    if self.df['close'].iloc[j] > pivot_price:
                        end_idx = j
                        break

                    # Check if a new pivot high is confirmed at this point
                    if not self.realistic_mode:
                        # In normal mode, a new pivot is confirmed after right_strength bars
                        for k in range(i + 1, len(self.pivot_high_indices)):
                            next_pivot_idx = self.pivot_high_indices[k]
                            next_pivot_confirmed_idx = next_pivot_idx + self.right_strength

                            # If we've reached the confirmation point of the next pivot
                            if j >= next_pivot_confirmed_idx:
                                end_idx = next_pivot_confirmed_idx
                                break

                        if end_idx is not None:
                            break
                    else:
                        # In realistic mode, a new pivot immediately replaces the current one
                        # when it's confirmed (since we're already plotting from confirmation)
                        for k in range(i + 1, len(self.pivot_high_indices)):
                            next_pivot_idx = self.pivot_high_indices[k]
                            next_pivot_confirmed_idx = next_pivot_idx + self.right_strength

                            if j == next_pivot_confirmed_idx:
                                end_idx = j
                                break

                        if end_idx is not None:
                            break

                # If no end condition found, extend to the last bar
                if end_idx is None:
                    end_idx = len(self.df)

                # Set the pivot price value for the range
                for j in range(plot_start_idx, end_idx):
                    if j < len(self.df):
                        self.df.loc[self.df.index[j], self.output_column] = pivot_price

        except Exception as e:
            print(f"Error in PivotHigh calculate: {str(e)}")

    def get_series_config(self) -> Dict[str, Any]:
        """
        Returns a single series configuration for backward compatibility.
        """
        # For backward compatibility, return the first series from get_series_configs
        configs = self.get_series_configs()
        if configs:
            return configs[0]

        # Return an empty series if no data is available
        return {
            "type": "Line",
            "data": [],
            "options": {
                "color": self.color,
                "lineWidth": self.line_width,
                "priceLineVisible": False,
                "lastValueVisible": False,
            },
            "label": self.name
        }

    def get_series_configs(self) -> List[Dict[str, Any]]:
        """Returns a list of series configurations for overlay plotting"""
        series_configs = []

        # Process each pivot high
        for i in range(len(self.pivot_high_indices)):
            pivot_idx = self.pivot_high_indices[i]
            pivot_price = self.df['high'].iloc[pivot_idx]

            if self.realistic_mode:
                # In realistic mode, only show from confirmation onwards
                start_idx = pivot_idx + self.right_strength

                # Find where price closes above the pivot high or a new pivot is confirmed
                end_idx = None

                # Check for price closing above pivot high
                for j in range(start_idx + 1, len(self.df)):
                    if self.df['close'].iloc[j] > pivot_price:
                        end_idx = j
                        break

                    # Check if a new pivot high is confirmed at this point
                    for k in range(i + 1, len(self.pivot_high_indices)):
                        next_pivot_idx = self.pivot_high_indices[k]
                        next_pivot_confirmed_idx = next_pivot_idx + self.right_strength

                        if j == next_pivot_confirmed_idx:
                            end_idx = j
                            break

                    if end_idx is not None:
                        break

                # If no end condition found, extend to the last bar
                if end_idx is None:
                    end_idx = len(self.df)

                # Create data points for this segment
                segment_data = []
                for idx in range(start_idx, end_idx):
                    if idx < len(self.df):
                        segment_data.append({
                            "time": str(self.df['date'].iloc[idx]),
                            "value": pivot_price
                        })

                if segment_data:
                    series_configs.append({
                        "type": "Line",
                        "data": segment_data,
                        "options": {
                            "color": self.color,
                            "lineWidth": self.line_width,
                            "lineStyle": 0,  # Solid line
                            "lastValueVisible": False,
                            "priceLineVisible": False
                        }
                    })
            else:
                # In normal mode, show dashed line during confirmation period, then solid line

                # Find where price closes above the pivot high or a new pivot is confirmed
                end_idx = None

                # Check for price closing above pivot high
                for j in range(pivot_idx + 1, len(self.df)):
                    if self.df['close'].iloc[j] > pivot_price:
                        end_idx = j
                        break

                    # Check if a new pivot high is confirmed at this point
                    for k in range(i + 1, len(self.pivot_high_indices)):
                        next_pivot_idx = self.pivot_high_indices[k]
                        next_pivot_confirmed_idx = next_pivot_idx + self.right_strength

                        # If we've reached the confirmation point of the next pivot
                        if j >= next_pivot_confirmed_idx:
                            end_idx = next_pivot_confirmed_idx
                            break

                    if end_idx is not None:
                        break

                # If no end condition found, extend to the last bar
                if end_idx is None:
                    end_idx = len(self.df)

                # 1. Dashed line (first right_strength bars)
                dashed_end_idx = min(pivot_idx + self.right_strength, end_idx)
                dashed_segment_data = []
                for idx in range(pivot_idx, dashed_end_idx):
                    if idx < len(self.df):
                        dashed_segment_data.append({
                            "time": str(self.df['date'].iloc[idx]),
                            "value": pivot_price
                        })

                if dashed_segment_data:
                    series_configs.append({
                        "type": "Line",
                        "data": dashed_segment_data,
                        "options": {
                            "color": self.color,
                            "lineWidth": self.line_width,
                            "lineStyle": 1,  # Dashed line
                            "lastValueVisible": False,
                            "priceLineVisible": False
                        }
                    })

                # 2. Solid line (after right_strength bars)
                solid_segment_data = []
                for idx in range(dashed_end_idx, end_idx):
                    if idx < len(self.df):
                        solid_segment_data.append({
                            "time": str(self.df['date'].iloc[idx]),
                            "value": pivot_price
                        })

                if solid_segment_data:
                    series_configs.append({
                        "type": "Line",
                        "data": solid_segment_data,
                        "options": {
                            "color": self.color,
                            "lineWidth": self.line_width,
                            "lineStyle": 0,  # Solid line
                            "lastValueVisible": False,
                            "priceLineVisible": False
                        }
                    })

        return series_configs