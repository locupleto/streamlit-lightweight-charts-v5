from abc import ABC, abstractmethod
from typing import Dict, Any, List, Literal, Optional
import pandas as pd
import numpy as np
from chart_themes import ChartTheme, ChartThemes

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
                 style: Literal["Candlestick", "Bar", "Line", "Area"] = "Candlestick",
                 overlays: Optional[List[Any]] = None, 
                 markers: Optional[List[Dict[str, Any]]] = None,
                 rectangles: Optional[List[Dict[str, Any]]] = None,  # Add rectangles parameter
                 theme: Optional[ChartTheme] = None):
        super().__init__(df, height, theme)
        self.style = style
        self.overlays = overlays or []
        self.markers = markers or []
        self.rectangles = rectangles or []  # Initialize rectangles list
        self.title = title or "<Add your own chart title>"

    def calculate(self) -> None:
        # Calculate any overlay indicators
        for overlay in self.overlays:
            overlay.calculate()

    def pane(self) -> Dict[str, Any]:
        # Prepare main price series data
        price_data = self.df[['date', 'open', 'high', 'low', 'close']].copy()
        price_data.rename(columns={'date': 'time'}, inplace=True)

        # First, prepare price_records outside the style conditions
        price_records = price_data.to_dict(orient="records")

        # Ensure dates are properly formatted strings
        if isinstance(price_data['time'].iloc[0], (pd.Timestamp, np.datetime64)):
            price_data['time'] = price_data['time'].dt.strftime('%Y-%m-%d')
        else:
            price_data['time'] = pd.to_datetime(price_data['time']).dt.strftime('%Y-%m-%d')

        # Calculate percentage change
        try:
            last_close = self.df['close'].iloc[-1]
            prev_close = self.df['close'].iloc[-2]
            pct_change = ((last_close - prev_close) / prev_close) * 100
            pct_change_str = f" ({'+' if pct_change >= 0 else ''}{pct_change:.2f}%)"
        except (IndexError, ValueError, ZeroDivisionError, AttributeError):
            pct_change_str = ""

        # Append percentage change to title
        display_title = f"{self.title}{pct_change_str}"

        # Determine if using dark theme
        is_dark_theme = "dark" in str(self.theme).lower() or "black" in str(self.theme).lower()

        # Configure series based on style
        if self.style == "Area":
            colors = self._get_performance_colors(is_dark_theme)
            area_data = self.df[['date', 'close']].copy()
            area_data.rename(columns={'date': 'time', 'close': 'value'}, inplace=True)
            area_data['time'] = area_data['time'].astype(str)
            area_records = area_data.to_dict(orient="records")
            series_config = {
                "type": "Area",
                "data": area_records,
                "options": {
                    "lineColor": colors["line"],
                    "topColor": colors["top"],
                    "bottomColor": colors["bottom"],
                    "lineWidth": 2,
                    "priceFormat": {
                        "type": 'price',
                        "precision": 2,
                        "minMove": 0.01,
                    },
                    "priceLineVisible": False
                }
            }
        elif self.style == "Candlestick":
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

        # Add markers if present
        if self.markers:
            series_configs[0]["markers"] = self.markers

        # Add rectangles if present
        if self.rectangles:
            series_configs[0]["rectangles"] = self.rectangles

        # Get base chart config from theme
        chart_config = self.get_chart_config()

        return {
            "chart": chart_config,
            "series": series_configs,
            "height": self.height,
            "title": display_title
        } 

    def calculate(self) -> None:
        # Calculate any overlay indicators
        for overlay in self.overlays:
            overlay.calculate()
            
    def _get_performance_colors(self, is_dark_theme: bool) -> Dict[str, str]:
        """Determine colors based on performance and theme"""
        # Calculate performance
        first_close = self.df['close'].iloc[0]
        last_close = self.df['close'].iloc[-1]
        performance = ((last_close / first_close) - 1) * 100
        is_bullish = performance >= 0

        if is_bullish:
            if is_dark_theme:
                return {
                    "line": "rgba(76, 175, 80, 1)",  # Green
                    "top": "rgba(76, 175, 80, 0.4)",
                    "bottom": "rgba(76, 175, 80, 0.1)"
                }
            else:
                return {
                    "line": "rgba(0, 128, 0, 1)",  # Darker Green
                    "top": "rgba(0, 128, 0, 0.4)",
                    "bottom": "rgba(0, 128, 0, 0.1)"
                }
        else:
            if is_dark_theme:
                return {
                    "line": "rgba(255, 82, 82, 1)",  # Red
                    "top": "rgba(255, 82, 82, 0.4)",
                    "bottom": "rgba(255, 82, 82, 0.1)"
                }
            else:
                return {
                    "line": "rgba(178, 34, 34, 1)",  # Darker Red
                    "top": "rgba(178, 34, 34, 0.4)",
                    "bottom": "rgba(178, 34, 34, 0.1)"
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
