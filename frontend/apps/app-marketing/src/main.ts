import { createApp } from "vue"
import { ensureStandaloneAuth } from "@astraflow/shared-auth"
import MarketingPlaceholder from "./MarketingPlaceholder.vue"
import "./style.css"

if (!window.__MICRO_APP_ENVIRONMENT__) ensureStandaloneAuth()
createApp(MarketingPlaceholder).mount("#app")

