import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({ base: "/micro/ticket/", plugins: [vue()], server: { port: 17304, proxy: { "/api": "http://127.0.0.1:18080" } } })
