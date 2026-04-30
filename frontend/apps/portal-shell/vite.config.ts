import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 17300,
    proxy: {
      "/api": "http://localhost:18080",
    },
  },
})
