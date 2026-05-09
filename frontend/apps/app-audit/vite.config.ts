import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({ base: "/micro/audit/", plugins: [vue()], server: { port: 17303, proxy: { "/api": "http://127.0.0.1:18080" } } })
