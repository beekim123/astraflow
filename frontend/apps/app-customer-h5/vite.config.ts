import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({ base: "/micro/customer/", plugins: [vue()], server: { port: 17305, proxy: { "/api": "http://localhost:18080" } } })
