import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

const microAppProxy = {
  changeOrigin: true,
  ws: true,
}

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 17300,
    proxy: {
      "/api": "http://127.0.0.1:18080",
      "/micro/admin": { target: "http://127.0.0.1:17301", ...microAppProxy },
      "/micro/chat": { target: "http://127.0.0.1:17302", ...microAppProxy },
      "/micro/audit": { target: "http://127.0.0.1:17303", ...microAppProxy },
      "/micro/ticket": { target: "http://127.0.0.1:17304", ...microAppProxy },
      "/micro/customer": { target: "http://127.0.0.1:17305", ...microAppProxy },
      "/micro/marketing": { target: "http://127.0.0.1:17306", ...microAppProxy },
    },
  },
})
