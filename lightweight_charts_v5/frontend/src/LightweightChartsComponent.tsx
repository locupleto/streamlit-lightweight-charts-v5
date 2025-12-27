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
 * Uses the setStretchFactor() API (introduced in v5.0.8) to set relative
 * pane heights. This eliminates the need for the previous elaborate workaround
 * that involved async delays and bottom-to-top sequential height setting.
 * The new approach is synchronous, faster, and more reliable.
 *
 * 2. Window Resize Race Condition:
 * Aggressive window resizing could trigger "Object is disposed" errors
 * during chart's internal paint cycle. Solution for this involves:
 * - Debouncing resize events with 800ms delay
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
    visualHeightFraction?: number // Height as fraction of chart (e.g., 0.1 for 10%)
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

/**
 * Calculate the maximum value in a dataset
 */
function calculateMaxValue(data: any[]): number {
  if (!data || data.length === 0) return 0

  const values = data
    .map(d => d.value)
    .filter(v => v != null && !isNaN(v) && isFinite(v))

  if (values.length === 0) return 0
  return Math.max(...values)
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
  const isResizing = useRef(false)
  const lastResizeTime = useRef(Date.now())
  const MIN_RESIZE_INTERVAL = 500 // 1 second minimum between resizes
  const [chartStable, setChartStable] = useState(false)
  const stabilityTimeout = useRef<number | null>(null)

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
     * Third Phase: Apply visual height fraction to price scales
     * Uses setVisibleRange() API to control overlay height
     */
    charts.forEach((paneConfig: ChartConfig, paneIndex: number) => {
      paneConfig.series.forEach((s: SeriesConfig, seriesIndex: number) => {
        // Only process series with visualHeightFraction specified
        if (s.priceScale?.visualHeightFraction && s.data && s.options?.priceScaleId) {
          const priceScaleId = s.options.priceScaleId

          // Get the price scale API
          const priceScale = chart.priceScale(priceScaleId)

          // Calculate max value from data
          const maxValue = calculateMaxValue(s.data)

          if (maxValue > 0) {
            // Calculate padded range (e.g., 10x for 10% height)
            const paddingMultiplier = 1 / s.priceScale.visualHeightFraction
            const paddedMax = maxValue * paddingMultiplier

            // Set explicit visible range
            priceScale.setVisibleRange({
              from: 0,
              to: paddedMax
            })
          }
        }
      })
    })

    /**
     * Fourth Phase: Set markers for the series that have them
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
     * Fifth Phase: Add rectangles to series that have them
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
     * Pane Height Initialization using setStretchFactor()
     *
     * Uses the v5.0.8+ setStretchFactor() API to set relative pane heights.
     * This is synchronous and eliminates the need for async delays.
     *
     * Stretch factors are relative proportions - if pane1 has factor 0.7 and
     * pane2 has factor 0.3, they will take 70% and 30% of total height respectively.
     */
    const initializePaneHeights = () => {
      const panes = chart.panes()

      // Calculate total height from all pane configs
      const totalConfigHeight = charts.reduce((sum: number, config: ChartConfig) => sum + config.height, 0)

      // Set stretch factor for each pane based on its proportion of total height
      panes.forEach((pane, index) => {
        const targetHeight = charts[index].height
        const stretchFactor = targetHeight / totalConfigHeight
        pane.setStretchFactor(stretchFactor)
      })
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
     *
     * Uses setStretchFactor() for consistent behavior with initialization.
     * Stretch factors are relative and automatically adapt to container size.
     */
    const setRelativeHeights = () => {
      if (!chartRef.current) return

      const panes = chartRef.current.panes()
      const totalConfigHeight = charts.reduce((sum: number, config: ChartConfig) => sum + config.height, 0)

      panes.forEach((pane, index) => {
        if (pane) {
          const targetHeight = charts[index].height
          const stretchFactor = targetHeight / totalConfigHeight
          pane.setStretchFactor(stretchFactor)
        }
      })
    }

    // Initialize pane heights (synchronous with setStretchFactor)
    initializePaneHeights()

    // Set up chart view immediately after height initialization
    if (chartRef.current) {
      // Set initial zoom level after heights are established
      const mainSeriesData = charts[0].series[0].data
      if (mainSeriesData?.length >= zoom_level) {
        chartRef.current.timeScale().setVisibleRange({
          from: mainSeriesData[mainSeriesData.length - zoom_level].time,
          to: mainSeriesData[mainSeriesData.length - 1].time,
        })
      } else {
        chartRef.current.timeScale().fitContent()
      }

      // Mark chart as initialized
      setChartStable(true)

      // Set a timeout to mark the chart as stable after initial rendering
      if (stabilityTimeout.current) {
        window.clearTimeout(stabilityTimeout.current)
      }
      stabilityTimeout.current = window.setTimeout(() => {
        setChartStable(true)
      }, 2000) // 2 seconds should be enough for initial rendering
    }

    // Handle window resize events
    const handleResize = () => {
      // Clear any existing timeout
      if (resizeTimeoutRef.current) {
        window.clearTimeout(resizeTimeoutRef.current)
      }

      // Set new timeout with moderate debounce
      resizeTimeoutRef.current = window.setTimeout(() => {
        if (
          chartContainerRef.current &&
          !isDisposed.current &&
          chartRef.current
        ) {
          isResizing.current = true
          lastResizeTime.current = Date.now()

          try {
            // Get new dimensions
            const newWidth = chartContainerRef.current.clientWidth

            // Store visible range before resize
            const visibleRange = chartRef.current.timeScale().getVisibleRange()

            // Perform resize
            chartRef.current.resize(newWidth, totalHeight)

            // Apply heights after a short delay
            setTimeout(() => {
              try {
                if (chartRef.current) {
                  setRelativeHeights() // Use the existing function for consistent height setting

                  // Restore visible range
                  if (visibleRange) {
                    chartRef.current.timeScale().setVisibleRange(visibleRange)
                  }
                }

                // Release resize lock
                setTimeout(() => {
                  isResizing.current = false
                }, 200)
              } catch (e) {
                console.error("Error during height adjustment:", e)
                isResizing.current = false
              }
            }, 100)
          } catch (e) {
            console.error("Error during resize:", e)
            isResizing.current = false
          }
        }
      }, 250) // Reduced debounce time for better responsiveness
    }

    // Set up resize listener
    window.addEventListener("resize", handleResize)

    const resizeObserver = new ResizeObserver((entries) => {
      // Force handleResize to be called when container size changes
      requestAnimationFrame(() => {
        handleResize()
      })
    })

    // Observe the container element
    if (chartContainerRef.current) {
      resizeObserver.observe(chartContainerRef.current)
    }

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
        if (chartRef.current) {
          const screenshot = chartRef.current.takeScreenshot()
          const dataUrl = screenshot.toDataURL("image/png")
          await new Promise((resolve) => setTimeout(resolve, 100))

          Streamlit.setComponentValue({
            type: "screenshot",
            data: dataUrl,
          })
        }
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

      // Clear stability timeout
      if (stabilityTimeout.current) {
        window.clearTimeout(stabilityTimeout.current)
      }

      // Disconnect the observer
      resizeObserver.disconnect()

      window.removeEventListener("resize", handleResize)
      chart.remove()
      setThemeApplied(false)
    }
  }, [
    JSON.stringify(charts),
    JSON.stringify(theme),
    zoom_level,
    fontsLoaded,
    configureTimeScale,
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
          if (chartRef.current) {
            const screenshot = chartRef.current.takeScreenshot()
            const dataUrl = screenshot.toDataURL("image/png")
            await new Promise((resolve) => setTimeout(resolve, 100))

            Streamlit.setComponentValue({
              type: "screenshot",
              data: dataUrl,
            })
          }
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
