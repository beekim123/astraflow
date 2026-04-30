import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({ base: "/micro/chat/", plugins: [vue()], server: { port: 17302, proxy: { "/api": "http://localhost:18080" } } })
