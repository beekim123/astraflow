# AstraFlow Frontend

第一阶段前端采用 `微前端 + monorepo`：

```text
apps/portal-shell       主门户，访问门禁、登录、SSO、系统入口、micro-app 加载
apps/app-admin          管理系统，用户/角色/菜单/权限/操作日志
apps/app-chat           AI 对话占位
apps/app-audit          智能审核占位
apps/app-ticket         AI 工单占位
apps/app-customer-h5    H5 客服占位
apps/app-marketing      内容营销助手占位
packages/shared-auth    Token 和登录态
packages/shared-api     Axios 封装、刷新 Token
packages/shared-ui      公共 UI 预留
```

## 本地断点调试

前端本地调试需要后端已经在 `http://127.0.0.1:18080` 启动。`portal-shell` 会把 `/api` 代理到后端，把 `/micro/*` 代理到各子应用，保证浏览器侧同源。

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj/frontend
test -f .env.local || cp .env.example .env.local
pnpm install
pnpm dev:portal
```

只看登录、访问门禁、当前用户、菜单这条主链路时，启动 `portal-shell` 就够了：

```bash
pnpm dev:portal
```

如果要同时进入各个微前端子应用，启动全部应用：

```bash
pnpm dev
```

也可以单独启动某个子应用：

```bash
pnpm dev:admin
pnpm dev:chat
pnpm dev:audit
pnpm dev:ticket
pnpm dev:customer
pnpm dev:marketing
```

端口：

```text
portal-shell: http://localhost:17300
app-admin:    http://localhost:17300/micro/admin/
app-chat:     http://localhost:17300/micro/chat/
app-audit:    http://localhost:17300/micro/audit/
app-ticket:   http://localhost:17300/micro/ticket/
customer-h5:  http://localhost:17300/micro/customer/
marketing:    http://localhost:17300/micro/marketing/
```

本地前端配置在 `.env.local`，不要提交到仓库。默认配置来自 `.env.example`：

```text
VITE_API_BASE_URL=/api
VITE_PORTAL_URL=http://localhost:17300
VITE_APP_ADMIN_URL=/micro/admin/
VITE_APP_CHAT_URL=/micro/chat/
VITE_APP_AUDIT_URL=/micro/audit/
VITE_APP_TICKET_URL=/micro/ticket/
VITE_APP_CUSTOMER_H5_URL=/micro/customer/
VITE_APP_MARKETING_URL=/micro/marketing/
```

## Token 说明

第一阶段为了本地开发方便，`access_token` 和 `refresh_token` 存在 `localStorage`。生产环境建议换成更严格的策略，例如 HttpOnly Cookie、CSP 和更完整的 XSS 防护。
