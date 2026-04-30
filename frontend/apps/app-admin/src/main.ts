import { createApp } from "vue"
import ElementPlus from "element-plus"
import "element-plus/dist/index.css"
import { ensureStandaloneAuth } from "@astraflow/shared-auth"
import App from "./App.vue"
import "./style.css"

if (!window.__MICRO_APP_ENVIRONMENT__) {
  ensureStandaloneAuth()
}

createApp(App).use(ElementPlus).mount("#app")
