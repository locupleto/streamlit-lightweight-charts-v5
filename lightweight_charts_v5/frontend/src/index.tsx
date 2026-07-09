import React from "react"
import { createRoot } from "react-dom/client"
import LightweightChartsComponent from "./LightweightChartsComponent"

const root = createRoot(document.getElementById("root")!)
root.render(
  <React.StrictMode>
    <LightweightChartsComponent />
  </React.StrictMode>
)
