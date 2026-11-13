// vite.config.js — Vite is the dev server + bundler for React.
//
// PROXY ANALOGY: The React app calls "/api/..." on its OWN address
// (localhost:5173). Vite quietly forwards those calls to FastAPI on
// localhost:8000, like a receptionist transferring a phone call.
// So the browser never sees a cross-origin request in development.
// In production there is no proxy: `npm run build` creates frontend/dist,
// and FastAPI serves those files itself, so /api is already the same server.
//
// "ASSETS": the build turns all of src/ into one .js and one .css file with
// random names (e.g. dist/assets/index-4uLnT91l.js). The name changes
// whenever the code changes, so browsers never use an old cached copy.
// They are GENERATED files: never edit them; they are git-ignored.
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
});
