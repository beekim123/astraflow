import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({ base: "/micro/marketing/", plugins: [vue()], server: { port: 17306, proxy: { "/api": "http://localhost:18080" } } })
