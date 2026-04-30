import { createApp } from "vue"
import { ensureStandaloneAuth } from "@astraflow/shared-auth"
import TicketPlaceholder from "./TicketPlaceholder.vue"
import "./style.css"

if (!window.__MICRO_APP_ENVIRONMENT__) ensureStandaloneAuth()
createApp(TicketPlaceholder).mount("#app")
