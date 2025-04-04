/**
 * LightweightChartsComponent
 *
 * A React component that creates multi-pane financial charts using the
 * lightweight-charts library. This component handles multiple chart panes
 * with different types of financial data visualization including candlesticks,
 * histograms, lines, areas, and overlay indicators.
 *
 * KEY FEATURES:
 * 1. Supports Multiple panes in one chart with synchronized time scales
 * 2. Support for various chart types: Candlestick, Line, Area, Histogram
 * 3. Overlay indicator support (e.g., moving averages on price charts)
 * 4. Pane titles (top-left) with configurable font and size, Cross-hairs...
 * 5. Save chart image to file using takeScreenshot()
 *
 * NOTES ON KEY CHALLENGES & SOLUTIONS:
 *
 * 1. Pane Height Initialization:
 * Initial challenge was achieving at least reasonable accurate initial pane
 * heights. Following the example in the documentation didn't work.
 * The current solution involves:
 * - Setting pane heights from bottom to top (reverse order)
 * - Using async/await with small delays between height settings
 * - Ensuring sequential height application before other chart operations
 *
 * 2. Window Resize Race Condition:
 * Aggressive window resizing could trigger "Object is disposed" errors
 * during chart's internal paint cycle. Solution for this involves:
 * - Debouncing resize events with 300ms delay (found optimal through testing)
 * - Tracking chart disposal state with refs
 * - Making chart invisible before disposal to prevent paint operations
 * - Disabling user interactions during cleanup
 * This fix preserves critical timing-dependent features like pane heights,
 * theme handling, and screenshot functionality.
 */

import React, { useEffect, useRef, useState } from "react"
import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import {
  createChart,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  AreaSeries,
  BarSeries,
  ISeriesApi,
  createTextWatermark,
  createSeriesMarkers,
  IChartApi,
} from "lightweight-charts"

import {
  StaticRectangle,
  RectangleOptions,
} from "./plugins/StaticRectanglePlugin"

/**
 * Defines the configuration for a single marker within a series.
 * Markers can be used to e.g. show Buy and Sell points in a chart
 */
interface SeriesMarker {
  time: string
  position: "aboveBar" | "belowBar" | "inBar"
  color: string
  shape: "circle" | "square" | "arrowUp" | "arrowDown"
  text: string
}

/**
 * Defines the configuration for a single series within a pane
 * Supports all major chart types and includes overlay configuration
 */
interface SeriesConfig {
  type: "Candlestick" | "Histogram" | "Line" | "Area" | "Bar"
  data: any[] // The series data points
  options?: any // Series-specific options including overlay settings
  priceScale?: {
    // Price scale configuration
    scaleMargins?: {
      top: number
      bottom: number
    }
    independent?: boolean // Whether this series uses its own price scale
    alignLabels?: boolean
  }
  markers?: SeriesMarker[]
  label?: string // Series label (especially useful for overlays)
  rectangles?: RectangleData[] // Add this line for rectangles
}

/**
 * Defines the configuration for a single chart pane
 * Can contain multiple series (main series + overlays)
 */
interface ChartConfig {
  chart?: {
    layout?: {
      background?: {
        color: string
      }
      textColor?: string
      fontFamily?: string
      fontSize?: number
      panes?: {
        separatorColor?: string
        separatorHoverColor?: string
        enableResize?: boolean
      }
    }
    grid?: {
      vertLines?: {
        color: string
      }
      horzLines?: {
        color: string
      }
    }
    timeScale?: {
      visible?: boolean
    }
    titleOptions?: {
      fontSize?: number
      fontFamily?: string
      fontStyle?: string
    }
    yieldCurve?: {
      baseResolution?: number
      minimumTimeRange?: number
      startTimeRange?: number
    }
    priceScaleBorderColor?: string
    timeScaleBorderColor?: string
  }
  series: SeriesConfig[] // Array of series (including overlays) to display in this pane
  height: number // Desired height of the pane in pixels
  title?: string // title property for pane watermark display
}

interface RectangleData {
  startTime: string
  startPrice: number
  endTime: string
  endPrice: number
  fillColor: string
  borderColor?: string
  borderWidth?: number
  opacity?: number
  zOrder?: "top" | "bottom" // Add z-order parameter
}

function LightweightChartsComponent({
  args,
  theme,
}: ComponentProps): React.ReactElement {
  const {
    charts,
    take_screenshot,
    zoom_level = 200,
    fonts = [],
    configureTimeScale = false,
  } = args
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const [hasSetInitialValue, setHasSetInitialValue] = useState(false)
  const [themeApplied, setThemeApplied] = useState(false)
  const resizeTimeoutRef = useRef<number | null>(null)
  const isDisposed = useRef(false)
  const [fontsLoaded, setFontsLoaded] = useState(false) // Add state to track font loading

  // Separate useEffect for font loading
  useEffect(() => {
    if (fonts && fonts.length > 0) {
      const loadFonts = async () => {
        try {
          // Create font URLs (converting spaces to +)
          const fontLinks: HTMLLinkElement[] = fonts.map((font: string) => {
            const fontLink: HTMLLinkElement = document.createElement("link")
            // Fix the URL construction - remove extra }
            const formattedFont = font.replace(/\s+/g, "+")
            fontLink.href = `https://fonts.googleapis.com/css2?family=${formattedFont}&display=swap`
            fontLink.rel = "stylesheet"
            return fontLink
          })

          // Add all font links to document head
          fontLinks.forEach((link: HTMLLinkElement) =>
            document.head.appendChild(link)
          )

          // Wait for all fonts to load
          await Promise.all(
            fonts.map((font: string) => document.fonts.load(`12px "${font}"`))
          )
          setFontsLoaded(true)
        } catch (error) {
          console.error("Error loading fonts:", error)
        }
      }

      loadFonts()
    }
  }, [fonts])

  useEffect(() => {
    if (!chartContainerRef.current || !charts?.length) {
      console.error("No valid charts config provided.")
      return
    }

    // Reset disposed flag on new effect
    isDisposed.current = false

    // Calculate total height for all panes
    const totalHeight = charts.reduce(
      (sum: number, pane: ChartConfig) => sum + pane.height,
      0
    )

    const containerWidth = chartContainerRef.current.clientWidth

    // Initialize the main chart container with base configuration
    const chart = createChart(chartContainerRef.current, {
      width: containerWidth,
      height: totalHeight,
      layout: theme
        ? {
            background: { color: theme.backgroundColor },
            textColor: theme.textColor,
          }
        : {},
      grid: {},
      ...charts[0].chart,
    })

    // Apply font settings after chart creation to match documentation approach
    if (charts[0].chart?.layout?.fontFamily) {
      chart.applyOptions({
        layout: {
          fontFamily: charts[0].chart.layout.fontFamily,
        },
      })
    }
    if (charts[0].chart?.layout?.fontSize) {
      chart.applyOptions({
        layout: {
          fontSize: charts[0].chart.layout.fontSize,
        },
      })
    }

    // Apply current theme color of scales to the chart
    const chartConfig = charts[0].chart || {}
    chart.priceScale("right").applyOptions({
      borderColor: chartConfig.priceScaleBorderColor || "#2B2B43",
      borderVisible: true,
      textColor: chartConfig.priceScaleTextColor,
    })

    chart.timeScale().applyOptions({
      borderColor: chartConfig.timeScaleBorderColor || "#2B2B43",
      borderVisible: true,
    })

    // Apply additional time scale configuration only if configureTimeScale is true
    if (configureTimeScale) {
      chart.timeScale().applyOptions({
        rightOffset: 12,
        barSpacing: 6,
        fixLeftEdge: true,
        lockVisibleTimeRangeOnResize: true,
        rightBarStaysOnScroll: true,
        timeVisible: true,
      })
    }

    // Store chart instance in ref
    chartRef.current = chart

    /**
     * First Phase: Create all series including overlays
     * Each pane can have multiple series, where additional series after the first
     * are treated as overlays sharing the same price scale
     */
    const seriesInstances: ISeriesApi<
      "Candlestick" | "Histogram" | "Line" | "Area" | "Bar"
    >[][] = charts.map((paneConfig: ChartConfig, index: number) =>
      paneConfig.series.map((s: SeriesConfig) => {
        // Combine series options with price scale settings
        const seriesOptions = {
          ...s.options,
          ...(s.priceScale && { priceScale: s.priceScale }),
        }

        // Create the appropriate series type
        switch (s.type) {
          case "Candlestick":
            return chart.addSeries(CandlestickSeries, seriesOptions, index)
          case "Histogram":
            return chart.addSeries(HistogramSeries, seriesOptions, index)
          case "Line":
            return chart.addSeries(LineSeries, seriesOptions, index)
          case "Area":
            return chart.addSeries(AreaSeries, seriesOptions, index)
          case "Bar":
            return chart.addSeries(BarSeries, seriesOptions, index)
          default:
            throw new Error(`Unsupported series type: ${s.type}`)
        }
      })
    )

    /**
     * Second Phase: Set data for all series and overlays
     * Each series in a pane gets its data set independently
     */
    charts.forEach((paneConfig: ChartConfig, paneIndex: number) => {
      paneConfig.series.forEach((s: SeriesConfig, seriesIndex: number) => {
        if (s.data && seriesInstances[paneIndex][seriesIndex]) {
          seriesInstances[paneIndex][seriesIndex].setData(s.data)
        }
      })
    })

    /**
     * Third Phase: Set markers for the series that have them
     */
    charts.forEach((paneConfig: ChartConfig, paneIndex: number) => {
      paneConfig.series.forEach((s: SeriesConfig, seriesIndex: number) => {
        if (
          s.markers &&
          s.markers.length > 0 &&
          seriesInstances[paneIndex][seriesIndex]
        ) {
          // Use createSeriesMarkers instead of setMarkers
          createSeriesMarkers(
            seriesInstances[paneIndex][seriesIndex],
            s.markers
          )
        }
      })
    })

    /**
     * Fourth Phase: Add rectangles to series that have them
     */
    const rectangleInstances: StaticRectangle[] = []
    charts.forEach((paneConfig: ChartConfig, paneIndex: number) => {
      paneConfig.series.forEach((s: SeriesConfig, seriesIndex: number) => {
        if (
          s.rectangles &&
          s.rectangles.length > 0 &&
          seriesInstances[paneIndex][seriesIndex]
        ) {
          s.rectangles.forEach((rect: RectangleData) => {
            // Create the rectangle with proper coordinates
            const rectangle = new StaticRectangle(
              chart,
              seriesInstances[paneIndex][seriesIndex],
              {
                startTime: rect.startTime,
                startPrice: rect.startPrice,
                endTime: rect.endTime,
                endPrice: rect.endPrice,
                fillColor: rect.fillColor,
                borderColor: rect.borderColor || "#000000",
                borderWidth: rect.borderWidth || 2,
                opacity: rect.opacity || 0.7,
                zOrder: rect.zOrder || "bottom", // Add z-order parameter with default
              }
            )
            rectangleInstances.push(rectangle)
          })
        }
      })
    })
    /**
     * CRITICAL SECTION: Pane Height Initialization
     *
     * This async function is key to achieving correct pane heights.
     * It works by:
     * 1. Processing panes from bottom to top (reverse order)
     * 2. Setting each height with a small delay between operations
     * 3. Ensuring sequential execution through async/await
     *
     * This approach prevents the "collapse" effect where middle panes
     * would minimize to their smallest possible height.
     */
    const initializePaneHeights = async () => {
      const panes = chart.panes()

      // Critical: Process panes from bottom to top
      for (let i = panes.length - 1; i >= 0; i--) {
        const pane = panes[i]
        const targetHeight = charts[i].height

        // Set height and wait for it to settle
        await new Promise((resolve) => {
          pane.setHeight(targetHeight)
          setTimeout(resolve, 10) // Small delay allows layout to stabilize
        })
      }
    }

    // Get all panes after series creation
    const panes = chart.panes()

    /**
     * Add watermark titles to each pane
     *
     * Note that a somewhat hacky approach has been taken to introduce small
     * horizontal and vertical margins since the API lacks suitable support for
     * that. Vertical spacing can be controlled by setting the line height of
     * an empty text line. The Horisontal spacing is fixed to one space char.
     */
    //
    panes.forEach((pane, index) => {
      if (charts[index].title && pane) {
        const textColor =
          charts[0].chart?.layout?.textColor || "rgba(0, 0, 0, 1)"

        // Get font settings from chart config
        const titleOptions = charts[index].chart?.titleOptions || {
          fontSize: 18,
          fontFamily: "Arial",
          fontStyle: "bold",
        }

        createTextWatermark(pane, {
          horzAlign: "left",
          vertAlign: "top",
          lines: [
            {
              text: " ",
              lineHeight: 8.0,
            },
            {
              text: "  " + (charts[index].title || ""),
              color: textColor,
              fontSize: titleOptions.fontSize,
              fontFamily: titleOptions.fontFamily,
              fontStyle: titleOptions.fontStyle,
              lineHeight: 1.5,
            },
          ],
        })
      }
    })

    /**
     * Regular resize height handling
     * Used for window resize events after initial setup
     */
    const setRelativeHeights = () => {
      const currentTotalHeight =
        chartContainerRef.current?.clientHeight || totalHeight
      const panes = chart.panes()

      panes.forEach((pane, index) => {
        if (pane) {
          const targetHeight = charts[index].height
          const proportion = targetHeight / totalHeight
          const allocatedHeight = Math.floor(currentTotalHeight * proportion)
          pane.setHeight(Math.max(allocatedHeight, 30)) // Ensure minimum height
        }
      })
    }

    // Initialize pane heights and then set up chart view
    initializePaneHeights().then(() => {
      // Set initial zoom level after heights are established
      const mainSeriesData = charts[0].series[0].data
      if (mainSeriesData?.length >= zoom_level) {
        chart.timeScale().setVisibleRange({
          from: mainSeriesData[mainSeriesData.length - zoom_level].time,
          to: mainSeriesData[mainSeriesData.length - 1].time,
        })
      } else {
        chart.timeScale().fitContent()
      }
    })

    // Handle window resize events
    const handleResize = () => {
      // Clear any existing timeout
      if (resizeTimeoutRef.current) {
        window.clearTimeout(resizeTimeoutRef.current)
      }

      // Set new timeout
      resizeTimeoutRef.current = window.setTimeout(() => {
        if (chartContainerRef.current && !isDisposed.current) {
          const newWidth = chartContainerRef.current.clientWidth
          chart.resize(newWidth, totalHeight)
          setRelativeHeights()
        }
      }, 300) // 300ms debounce
    }

    // Set up resize listener
    window.addEventListener("resize", handleResize)

    // Only set initial value once and not during screenshot
    if (!hasSetInitialValue && !take_screenshot) {
      Streamlit.setComponentValue(0)
      setHasSetInitialValue(true)
    }

    // Mark theme as applied after a short delay
    setTimeout(() => {
      setThemeApplied(true)
    }, 100)

    const takeDelayedScreenshot = async () => {
      try {
        await new Promise((resolve) =>
          requestAnimationFrame(() => {
            setTimeout(resolve, 250)
          })
        )
        const screenshot = chartRef.current!.takeScreenshot()
        const dataUrl = screenshot.toDataURL("image/png")
        await new Promise((resolve) => setTimeout(resolve, 100))

        Streamlit.setComponentValue({
          type: "screenshot",
          data: dataUrl,
        })
      } catch (error) {
        console.error("Screenshot error:", error)
        Streamlit.setComponentValue({
          type: "error",
          message: String(error),
        })
      }
    }

    takeDelayedScreenshot()

    // Cleanup function
    return () => {
      // Prevent new paint operations by disabling chart
      try {
        if (chart) {
          chart.applyOptions({
            layout: {
              background: { color: "transparent" },
              textColor: "transparent",
            },
            handleScale: false,
            handleScroll: false,
          })
        }
      } catch (e) {
        console.warn("Chart disposal: Could not update options", e)
      }

      // Mark as disposed
      isDisposed.current = true

      // Clear any pending resize timeout
      if (resizeTimeoutRef.current) {
        window.clearTimeout(resizeTimeoutRef.current)
      }

      window.removeEventListener("resize", handleResize)
      chart.remove()
      setThemeApplied(false)
    }
  }, [
    charts,
    theme,
    hasSetInitialValue,
    take_screenshot,
    zoom_level,
    fontsLoaded,
  ])

  // Separate effect for screenshot handling stays unchanged
  useEffect(() => {
    if (take_screenshot && chartRef.current && themeApplied) {
      const takeDelayedScreenshot = async () => {
        try {
          await new Promise((resolve) =>
            requestAnimationFrame(() => {
              setTimeout(resolve, 250)
            })
          )
          const screenshot = chartRef.current!.takeScreenshot()
          const dataUrl = screenshot.toDataURL("image/png")
          await new Promise((resolve) => setTimeout(resolve, 100))

          Streamlit.setComponentValue({
            type: "screenshot",
            data: dataUrl,
          })
        } catch (error) {
          console.error("Screenshot error:", error)
          Streamlit.setComponentValue({
            type: "error",
            message: String(error),
          })
        }
      }

      takeDelayedScreenshot()
    }
  }, [take_screenshot, themeApplied])

  return (
    <div
      style={{
        width: "100%",
        height: `${charts.reduce(
          (sum: number, pane: ChartConfig) => sum + pane.height,
          0
        )}px`,
      }}
      ref={chartContainerRef}
    />
  )
}

export default withStreamlitConnection(LightweightChartsComponent)
