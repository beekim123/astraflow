import { createApp } from "vue"
import { ensureStandaloneAuth } from "@astraflow/shared-auth"
import CustomerH5Placeholder from "./CustomerH5Placeholder.vue"
import "./style.css"

if (!window.__MICRO_APP_ENVIRONMENT__) ensureStandaloneAuth()
createApp(CustomerH5Placeholder).mount("#app")

