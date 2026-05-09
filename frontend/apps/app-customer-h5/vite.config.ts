import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({ base: "/micro/customer/", plugins: [vue()], server: { port: 17305, proxy: { "/api": "http://127.0.0.1:18080" } } })
