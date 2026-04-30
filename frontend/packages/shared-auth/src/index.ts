export type TokenPair = {
  access_token: string
  refresh_token: string
}

const ACCESS_KEY = "astraflow_access_token"
const REFRESH_KEY = "astraflow_refresh_token"

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY)
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY)
}

export function setTokens(tokens: TokenPair) {
  localStorage.setItem(ACCESS_KEY, tokens.access_token)
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

export function isLoggedIn() {
  return Boolean(getAccessToken())
}

export function redirectToLogin() {
  const portalUrl = import.meta.env.VITE_PORTAL_URL || "http://localhost:17300"
  const redirect = encodeURIComponent(window.location.href)
  window.location.href = `${portalUrl}/login?redirect=${redirect}`
}

export function ensureStandaloneAuth() {
  if (!isLoggedIn()) {
    redirectToLogin()
  }
}
