import { defineConfig } from "vitest/config";
import { fileURLToPath, URL } from "node:url";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  // Dev-server proxy so the same-origin "/api" base works in `vite dev` too.
  // In the production container the SPA and API are same-origin, so no proxy is needed.
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  // `npm run build` keeps Vite's default outDir: apps/client/dist
  test: {
    environment: "jsdom",
    // Absolute API base so fetch calls become "http://localhost/api/..." which
    // MSW can match. Also sets a stable jsdom page URL for the same reason.
    env: {
      VITE_API_URL: "http://localhost/api",
    },
    environmentOptions: {
      jsdom: { url: "http://localhost" },
    },
    globals: true,
    setupFiles: ["allure-vitest/setup", "./src/test/setup.ts"],
    css: true,
    // Only pick up *.spec.{ts,tsx} files — the renamed convention.
    include: ["src/**/*.spec.{ts,tsx}"],
    reporters: [
      "default",
      ["allure-vitest/reporter", { resultsDir: "allure-results" }],
    ],
    coverage: {
      provider: "v8",
      // Instrument all source TS/TSX under src/.
      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        // Bootstrap entry point — requires a real DOM #root element; not business logic.
        "src/main.tsx",
        // shadcn-generated UI primitives — vendored/generated; not authored by us.
        "src/components/ui/**",
        // Vitest setup infrastructure — not app code.
        "src/test/**",
      ],
      reporter: ["text", "html"],
      thresholds: {
        statements: 100,
        branches: 100,
        functions: 100,
        lines: 100,
      },
    },
  },
});
