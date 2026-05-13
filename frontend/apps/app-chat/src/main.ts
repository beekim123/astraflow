import { createApp } from "vue"
import { ensureStandaloneAuth } from "@astraflow/shared-auth"
import ElementPlus from "element-plus"
import "element-plus/dist/index.css"
import ChatWorkbench from "./ChatWorkbench.vue"
import "./style.css"

if (!window.__MICRO_APP_ENVIRONMENT__) ensureStandaloneAuth()
createApp(ChatWorkbench).use(ElementPlus).mount("#app")
