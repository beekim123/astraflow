import { defineStore } from "pinia"
import { clearTokens, isLoggedIn, setTokens } from "@astraflow/shared-auth"
import { getMe, login } from "../api"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as null | { username: string; nickname: string; roles: string[]; permissions: string[] },
  }),
  getters: {
    loggedIn: () => isLoggedIn(),
  },
  actions: {
    async login(username: string, password: string) {
      const tokens = await login(username, password)
      setTokens(tokens)
      this.user = await getMe()
    },
    async loadMe() {
      if (isLoggedIn()) this.user = await getMe()
    },
    logout() {
      clearTokens()
      this.user = null
    },
  },
})

