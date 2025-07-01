import vue from "@vitejs/plugin-vue";
import path from "path";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    fs: {
      allow: [
        path.resolve(__dirname, "../.."), // allows access one level up
      ],
    },
  },
  resolve: {
    alias: {
      "@root": path.resolve(__dirname, "../"),
    },
  },
});
