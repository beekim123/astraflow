import { createApp } from "vue"
import { ensureStandaloneAuth } from "@astraflow/shared-auth"
import ChatPlaceholder from "./ChatPlaceholder.vue"
import "./style.css"

if (!window.__MICRO_APP_ENVIRONMENT__) ensureStandaloneAuth()
createApp(ChatPlaceholder).mount("#app")

