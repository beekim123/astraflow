import axios from "axios"
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "@astraflow/shared-auth"

export type ApiResult<T> = {
  code: number
  message: string
  data: T
}

export const apiBaseURL = import.meta.env.VITE_API_BASE_URL || "/api"

export const api = axios.create({
  baseURL: apiBaseURL,
  timeout: 20000,
  withCredentials: true,
})

let refreshing: Promise<string | null> | null = null

function createRequestId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID()
  }
  return `req-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`
}

export function buildApiUrl(path: string) {
  const base = apiBaseURL.replace(/\/$/, "")
  const normalizedPath = path.startsWith("/") ? path : `/${path}`
  return `${base}${normalizedPath}`
}

function createAuthHeaders(headers?: HeadersInit, token = getAccessToken()) {
  const merged = new Headers(headers)
  if (token) {
    merged.set("Authorization", `Bearer ${token}`)
  }
  if (!merged.has("X-Request-ID")) {
    merged.set("X-Request-ID", createRequestId())
  }
  return merged
}

async function getFreshAccessToken() {
  if (!refreshing) {
    refreshing = refreshAccessToken()
  }
  const token = await refreshing
  refreshing = null
  return token
}

export async function authFetch(path: string, init: RequestInit = {}) {
  const url = buildApiUrl(path)
  const request = {
    ...init,
    headers: createAuthHeaders(init.headers),
  }
  let response = await fetch(url, request)
  if (response.status !== 401) return response

  const token = await getFreshAccessToken()
  if (!token) return response

  response = await fetch(url, {
    ...init,
    headers: createAuthHeaders(init.headers, token),
  })
  return response
}

api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  config.headers["X-Request-ID"] = createRequestId()
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original.__retried) {
      original.__retried = true
      if (!refreshing) {
        refreshing = refreshAccessToken()
      }
      const token = await refreshing
      refreshing = null
      if (token) {
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      }
    }
    return Promise.reject(error)
  },
)

async function refreshAccessToken() {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return null
  try {
    const { data } = await axios.post<ApiResult<{ access_token: string; refresh_token: string }>>(
      buildApiUrl("/auth/refresh"),
      { refresh_token: refreshToken },
      { withCredentials: true },
    )
    setTokens(data.data)
    return data.data.access_token
  } catch {
    clearTokens()
    return null
  }
}

export async function unwrap<T>(request: Promise<{ data: ApiResult<T> }>) {
  const response = await request
  return response.data.data
}

export function getApiErrorMessage(error: unknown, fallback = "操作失败") {
  const err = error as {
    response?: { data?: { message?: string }; status?: number }
    message?: string
  }
  const message = err.response?.data?.message
  if (message) return message
  if (err.response?.status && err.response.status >= 500) return "系统繁忙，请稍后再试"
  return err.message || fallback
}
