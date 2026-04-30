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

## 本地开发

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj/frontend
pnpm install
pnpm dev
```

单独启动：

```bash
pnpm dev:portal
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
app-admin:    http://localhost:17301
app-chat:     http://localhost:17302
app-audit:    http://localhost:17303
app-ticket:   http://localhost:17304
customer-h5:  http://localhost:17305
marketing:    http://localhost:17306
```

## Token 说明

第一阶段为了本地开发方便，`access_token` 和 `refresh_token` 存在 `localStorage`。生产环境建议换成更严格的策略，例如 HttpOnly Cookie、CSP 和更完整的 XSS 防护。
