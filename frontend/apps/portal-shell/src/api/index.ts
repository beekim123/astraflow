import { api, unwrap } from "@astraflow/shared-api"

export type MenuItem = {
  id: string
  code: string
  name: string
  menu_type: string
  app_key?: string | null
  path: string
  component: string
  icon: string
  sort: number
  visible?: boolean
  status?: string
  children?: MenuItem[]
}

export function getGateStatus() {
  return unwrap<{ gate_passed: boolean }>(api.get("/security/visitor-gate/status"))
}

export function getCaptcha() {
  return unwrap<{ captcha_id: string; question: string }>(api.get("/security/visitor-captcha"))
}

export function verifyCaptcha(captcha_id: string, answer: string) {
  return unwrap<{ gate_passed: boolean }>(api.post("/security/visitor-captcha/verify", { captcha_id, answer }))
}

export function login(username: string, password: string) {
  return unwrap<{ access_token: string; refresh_token: string }>(api.post("/auth/login", { username, password }))
}

export function getMe() {
  return unwrap<{ username: string; nickname: string; roles: string[]; permissions: string[] }>(api.get("/auth/me"))
}

export function getMenus() {
  return unwrap<MenuItem[]>(api.get("/menus/me"))
}

export type LearnUserInfo = {
  id: string
  username: string
  nickname: string
  email?: string | null
  phone?: string | null
  status: string
  is_superuser: boolean
  organization_id: string
}

export function getLearnInfo() {
  return unwrap<LearnUserInfo>(api.get("/learn/getInfo"))
}

export function getLearnInfoFromDb() {
  return unwrap<LearnUserInfo>(api.get("/learn/getInfoFromDb"))
}
