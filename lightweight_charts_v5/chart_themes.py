from dataclasses import dataclass
from typing import Optional, Dict, Any, Literal

@dataclass
class ChartTheme:
    """Base theme configuration for charts"""
    # Basic chart colors
    background_color: str = "#FFFFFF"
    text_color: str = "#000000"

    # Global default font settings
    font_family: str = "Arial"
    font_size: int = 12

    # Title font settings (overrides global if set)
    title_font_size: int = 14
    title_font_family: str = "Arial"
    title_font_style: str = "normal"

    # Grid settings
    grid_vert_color: str = "#e1e3e8"
    grid_horz_color: str = "#e1e3e8"
    grid_lines_visible: bool = True

    # Pane dividers
    pane_separator_color: str = "#FF0000"
    pane_separator_hover_color: str = "#363A45"
    enable_pane_resize: bool = True

    # Scale borders
    price_scale_border_color: str = "#2B2B43"
    time_scale_border_color: str = "#2B2B43"
    
    # Series colors
    up_color: str = "rgb(54,116,217)"
    down_color: str = "rgb(225,50,85)"
    volume_up_color: str = "rgba(38,166,154,0.8)"
    volume_down_color: str = "rgba(239,83,80,0.8)"

    # Default line colors for indicators
    primary_line_color: str = "rgba(0, 0, 255, 1)"
    secondary_line_color: str = "rgba(255, 140, 0, 0.8)"
    tertiary_line_color: str = "rgba(25, 118, 210, 0.8)"

    # Crosshair settings
    crosshair_vert_color: str = "rgba(0, 0, 255, 0.4)"
    crosshair_horz_color: str = "rgba(0, 0, 255, 0.4)"
    crosshair_vert_label_background: str = "rgba(0, 0, 255, 1)" 
    crosshair_horz_label_background: str = "rgba(0, 0, 255, 1)" 
    crosshair_mode: Literal["normal", "magnet"] = "normal"
    crosshair_vert_width: int = 2
    crosshair_horz_width: int = 2
    crosshair_vert_style: Literal["solid", "dotted", "dashed", "large_dashed", "sparse_dotted"] = "dashed"
    crosshair_horz_style: Literal["solid", "dotted", "dashed", "large_dashed", "sparse_dotted"] = "dashed"  

    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to chart configuration dictionary"""
        # Map our style names to LightweightCharts LineStyle values
        line_style_map = {
            "solid": 0,
            "dotted": 1,
            "dashed": 2,
            "large_dashed": 3,
            "sparse_dotted": 4
        }
        return {
            "layout": {
                "background": {"color": self.background_color},
                "textColor": self.text_color,
                "fontFamily": self.font_family, 
                "fontSize": self.font_size,
                "panes": {
                    "separatorColor": self.pane_separator_color,
                    "separatorHoverColor": self.pane_separator_hover_color,
                    "enableResize": self.enable_pane_resize,
                },
            },
            "grid": {
                "vertLines": {
                    "color": self.grid_vert_color,
                    "visible": self.grid_lines_visible
                },
                "horzLines": {
                    "color": self.grid_horz_color,
                    "visible": self.grid_lines_visible
                }
            },
            "titleOptions": {
                "fontSize": self.title_font_size,
                "fontFamily": self.title_font_family,
                "fontStyle": self.title_font_style
            },
            "seriesColors": {
                "upColor": self.up_color,
                "downColor": self.down_color,
                "volumeUpColor": self.volume_up_color,
                "volumeDownColor": self.volume_down_color,
            },
            "indicatorColors": {
                "primary": self.primary_line_color,
                "secondary": self.secondary_line_color,
                "tertiary": self.tertiary_line_color,
            },
            "crosshair": {
                "mode": self.crosshair_mode,
                "vertLine": {
                    "width": self.crosshair_vert_width,
                    "color": self.crosshair_vert_color,
                    "style": line_style_map[self.crosshair_vert_style],
                    "labelBackgroundColor": self.crosshair_vert_label_background,
                },
                "horzLine": {
                    "width": self.crosshair_horz_width,
                    "color": self.crosshair_horz_color,
                    "style": line_style_map[self.crosshair_horz_style],
                    "labelBackgroundColor": self.crosshair_horz_label_background,
                },
            },
            "priceScale": {
                "borderColor": self.price_scale_border_color,
                "borderVisible": True,
            },
            "timeScale": {
                "borderColor": self.time_scale_border_color,
                "borderVisible": True,
            },
            "priceScaleBorderColor": self.price_scale_border_color,
            "timeScaleBorderColor": self.time_scale_border_color,
        }

class ChartThemes:
    """Collection of predefined chart themes"""

    @staticmethod
    def light() -> ChartTheme:
        return ChartTheme(
            # Basic chart colors
            background_color="#FFFFFF",
            text_color="#000000",

            # Global default font settings
            font_family = "Arial",
            font_size = 12,

            # Title font settings (overrides global)
            title_font_size= 14,
            title_font_family = "Arial",
            title_font_style = "normal",

            # Grid settings
            grid_vert_color="#e1e3e8",
            grid_horz_color="#e1e3e8",
            grid_lines_visible = True,

            # Pane dividers
            pane_separator_color="#E0E3EB",
            pane_separator_hover_color="#B2B5BE",
            enable_pane_resize = True,

            # Scale borders
            price_scale_border_color = "#2B2B43",
            time_scale_border_color = "#2B2B43",

            # Series colors
            up_color="rgb(54,116,217)",
            down_color="rgb(225,50,85)",
            volume_up_color="rgba(38,166,154,0.8)",
            volume_down_color="rgba(239,83,80,0.8)",

            # Line colors for indicators
            primary_line_color="rgba(0, 0, 255, 1)",
            secondary_line_color="rgba(255, 140, 0, 0.8)",
            tertiary_line_color="rgba(25, 118, 210, 0.8)",

            # Crosshair settings
            crosshair_vert_color = "rgba(0, 0, 255, 0.4)",
            crosshair_horz_color = "rgba(0, 0, 255, 0.4)",
            crosshair_vert_label_background = "rgba(0, 0, 255, 1)",
            crosshair_horz_label_background = "rgba(0, 0, 255, 1)", 
            crosshair_mode = "normal",
            crosshair_vert_width = 2,
            crosshair_horz_width = 2,
            crosshair_vert_style = "dashed",
            crosshair_horz_style = "dashed", 
        )

    @staticmethod
    def dark() -> ChartTheme:
        return ChartTheme(
            # Basic chart colors
            background_color="#131722",
            text_color="#D1D4DC",

            # Global default font settings
            font_family = "Arial",
            font_size = 12,

            # Title font settings (overrides global)
            title_font_size= 14,
            title_font_family = "Arial",
            title_font_style = "normal",

            # Grid settings
            grid_vert_color="#363C4E",
            grid_horz_color="#363C4E",
            grid_lines_visible = True,
            
            # Pane dividers
            pane_separator_color="#363A45",
            pane_separator_hover_color="#787B86",
            enable_pane_resize = True,

            # Scale borders
            price_scale_border_color = "#2B2B43",
            time_scale_border_color = "#2B2B43",

            # Series colors
            up_color="rgb(54,116,217)",
            down_color="rgb(225,50,85)",
            volume_up_color="rgba(38,166,154,0.8)",
            volume_down_color="rgba(239,83,80,0.8)",

            # Line colors for indicators
            primary_line_color="rgba(0, 0, 255, 1)",
            secondary_line_color="rgba(255, 140, 0, 0.8)",
            tertiary_line_color="rgba(25, 118, 210, 0.8)",

            # Crosshair settings
            crosshair_vert_color="#9B7DFF",
            crosshair_horz_color="#9B7DFF",
            crosshair_vert_label_background="#9B7DFF",
            crosshair_horz_label_background="#9B7DFF",
            crosshair_mode = "normal",
            crosshair_vert_width = 2,
            crosshair_horz_width = 2,
            crosshair_vert_style = "dashed",
            crosshair_horz_style = "dashed", 
        )

    @staticmethod
    def black() -> ChartTheme:
        return ChartTheme(
            # Basic chart colors
            background_color="#000000",
            text_color="#FFFFFF",

            # Global default font settings
            font_family = "Arial",
            font_size = 12,

            # Title font settings (overrides global)
            title_font_size= 14,
            title_font_family = "Arial",
            title_font_style = "normal",

            # Grid settings
            grid_vert_color="#333333",
            grid_horz_color="#333333",
            grid_lines_visible = True,

            # Pane dividers
            pane_separator_color="#363636",
            pane_separator_hover_color="#787878",
            enable_pane_resize = True,

            # Scale borders
            price_scale_border_color = "#2B2B43",
            time_scale_border_color = "#2B2B43",

            # Series colors
            up_color="rgb(54,116,217)",
            down_color="rgb(225,50,85)",
            volume_up_color="rgba(38,166,154,0.8)",
            volume_down_color="rgba(239,83,80,0.8)",

            # Line colors for indicators
            primary_line_color="rgba(0, 0, 255, 1)",
            secondary_line_color="rgba(255, 140, 0, 0.8)",
            tertiary_line_color="rgba(25, 118, 210, 0.8)",

            # Crosshair settings
            crosshair_vert_color="#9B7DFF",
            crosshair_horz_color="#9B7DFF",
            crosshair_vert_label_background="#9B7DFF",
            crosshair_horz_label_background="#9B7DFF",
            crosshair_mode = "normal",
            crosshair_vert_width = 2,
            crosshair_horz_width = 2,
            crosshair_vert_style = "dashed",
            crosshair_horz_style = "dashed", 
        )

    @staticmethod
    def custom() -> ChartTheme:
        return ChartTheme(
            # Basic chart colors
            background_color="#FFFFFF",
            text_color="rgba(0, 5, 175, 1.0)",

            # Global default font settings 
            font_family = "Patrick Hand SC",
            font_size = 14,

            # Title specific font settings (overrides global)
            title_font_size=16,
            title_font_family="Patrick Hand SC",
            title_font_style="bold",

            # Grid settings
            grid_vert_color="rgba(35, 157, 245, 0.4)",
            grid_horz_color="rgba(35, 157, 245, 0.4)",
            grid_lines_visible = True,

            # Pane dividers
            pane_separator_color="rgba(255,255,255,1.0)",
            pane_separator_hover_color="rgba(255,235,59,0.5)",
            enable_pane_resize = True,
            
            # Scale borders
            price_scale_border_color = "#fb7e6c",
            time_scale_border_color = "#fb7e6c",

            # Series colors
            up_color="rgb(54,116,217)",
            down_color="rgb(225,50,85)",
            volume_up_color="rgba(38,166,154,0.8)",
            volume_down_color="rgba(239,83,80,0.8)",

            # Line colors for indicators
            primary_line_color="rgba(0, 0, 255, 1)",
            secondary_line_color="rgba(255, 140, 0, 0.8)",
            tertiary_line_color="rgba(25, 118, 210, 0.8)",

            # Crosshair settings
            crosshair_vert_color="#9B7DFF",
            crosshair_horz_color="#9B7DFF",
            crosshair_vert_label_background="#9B7DFF",
            crosshair_horz_label_background="#9B7DFF",
            crosshair_mode = "normal",
            crosshair_vert_width = 2,
            crosshair_horz_width = 2,
            crosshair_vert_style = "dashed",
            crosshair_horz_style = "dashed", 
        )