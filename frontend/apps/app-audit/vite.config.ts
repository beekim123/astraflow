import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({ base: "/micro/audit/", plugins: [vue()], server: { port: 17303, proxy: { "/api": "http://localhost:18080" } } })
