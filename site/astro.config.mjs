import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const REPO_ROOT = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  site: "https://business-capabilities.turbo-ea.org",
  integrations: [react()],
  outDir: join(REPO_ROOT, "dist", "site"),
  // Copy the static JSON API artefacts emitted by `npm run build:api`
  // into the deployed site so /api/*.json is served alongside HTML.
  publicDir: "./public",
  vite: {
    resolve: {
      alias: {
        "@catalogue-data": join(REPO_ROOT, "dist", "api"),
      },
    },
  },
});
