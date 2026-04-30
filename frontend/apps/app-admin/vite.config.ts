import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({
  base: "/micro/admin/",
  plugins: [vue()],
  server: {
    port: 17301,
    proxy: { "/api": "http://localhost:18080" },
  },
})
