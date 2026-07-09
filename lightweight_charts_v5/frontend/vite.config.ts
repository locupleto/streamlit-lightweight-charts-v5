import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

// https://vitejs.dev/config/
export default defineConfig({
  // React 16.13 predates the automatic JSX runtime, so use the classic one
  plugins: [react({ jsxRuntime: "classic" })],
  // Relative asset paths — the component is served from a subdirectory by Streamlit
  base: "./",
  server: {
    // IPv4 explicitly — the Python dev-server probe connects to 127.0.0.1
    host: "127.0.0.1",
    port: 3001,
    strictPort: true,
  },
  build: {
    // Keep the same output directory CRA used so the Python side needs no changes
    outDir: "build",
  },
})
