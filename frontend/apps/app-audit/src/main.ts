import { createApp } from "vue"
import { ensureStandaloneAuth } from "@astraflow/shared-auth"
import AuditPlaceholder from "./AuditPlaceholder.vue"
import "./style.css"

if (!window.__MICRO_APP_ENVIRONMENT__) ensureStandaloneAuth()
createApp(AuditPlaceholder).mount("#app")
