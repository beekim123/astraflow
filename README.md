# AstraFlow AI

企业级 AI 工作流与智能审核平台，第一阶段只实现平台底座，不做真实 AI。

## 已生成目录

```text
backend/   FastAPI 后端
frontend/  Vue 3 微前端 monorepo
infra/     Docker Compose、Nginx、本地脚本
```

## 启动方式选择

### 模式一：全量 Docker 启动

适合快速看完整系统、验证 Docker/Nginx/前后端联调效果。这个模式不适合逐行断点调试业务代码。

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj
docker compose -f infra/docker-compose.local.yml --profile full up --build
```

访问：

```text
门户入口: http://localhost:18000
后端文档: http://localhost:18080/docs
```

默认账号：

```text
admin / Admin@123456
member / Member@123456
```

停止全量 Docker：

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj
docker compose -f infra/docker-compose.local.yml --profile full down
```

### 模式二：本地断点调试启动

适合学习数据从前端到后端的完整流转。这个模式只用 Docker 跑 PostgreSQL 和 Redis，前端、后端都在本机启动，方便热更新和 IDE 断点。

如果之前跑过全量 Docker，先停掉全量环境：

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj
docker compose -f infra/docker-compose.local.yml --profile full down
```

先启动数据库和缓存：

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj
docker compose -f infra/docker-compose.local.yml up -d postgres redis
```

也可以用脚本：

```bash
./infra/scripts/debug-infra-up.sh
```

启动后端：

```bash
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
test -f .env || cp .env.example .env
python -m alembic upgrade head
python -m app.db.init_db
python -m uvicorn app.main:app --reload --port 18080
```

启动前端：

```bash
cd ../frontend
test -f .env.local || cp .env.example .env.local
pnpm install
pnpm dev:portal
```

本地断点调试入口：

```text
门户入口: http://localhost:17300
后端文档: http://localhost:18080/docs
```

如果要同时看所有微前端子应用，把 `pnpm dev:portal` 换成：

```bash
pnpm dev
```

## 配置隔离原则

- `infra/docker-compose.local.yml` 默认只启动 PostgreSQL 和 Redis；加 `--profile full` 才启动完整 Docker 应用栈。
- Docker 后端使用 `postgres:5432` 和 `redis:6379`，配置写在 `infra/docker-compose.local.yml`。
- 本地后端使用 `localhost:15432` 和 `localhost:16379`，配置写在 `backend/.env`。
- 本地前端使用 Vite 代理 `/api` 到 `http://127.0.0.1:18080`，并通过 `portal-shell` 把 `/micro/*` 代理到各子应用，避免跨端口导致 token/localStorage 不共享。
- 生产部署只使用 `infra/docker-compose.prod.yml` 和 `infra/env/.env.prod`，不要把本地调试配置写进生产文件。

## 断点建议

建议按这条链路看：

```text
浏览器进入页面 -> 访问门禁/验证码 -> 登录 -> 获取当前用户 -> 获取菜单
```

重点文件：

```text
frontend/apps/portal-shell/src/router/index.ts
frontend/packages/shared-api/src/index.ts
frontend/apps/portal-shell/src/stores/auth.ts
backend/app/modules/security_gate/router.py
backend/app/modules/identity/router.py
backend/app/core/deps.py
backend/app/core/cache.py
```

## 第一阶段功能

- 访问门禁和数字验证码。
- 登录、JWT、Refresh Token、退出。
- RBAC 权限和动态菜单。
- 微前端主门户和多系统入口。
- 管理系统：用户、角色、菜单、权限、操作日志。
- 业务系统占位：AI 对话、智能审核、AI 工单、H5 客服、内容营销助手。
- PostgreSQL、Redis、Docker Compose、Nginx。
- RequestID 中间件和操作日志。
- `AgentClient` / `MockAgentClient` AI 边界预留。

## 第一阶段故意不做

- 不接真实模型。
- 不做 MCP 服务。
- 不做 RAG、OCR、数字人。
- 不上 Nacos。
- 不拆多仓库微服务。

## 第二阶段扩展方向

第二阶段按文档里的 `mcp-demo` 思路演进：

```text
backend-api -> ai-gateway -> MCP Client -> mcp-llm-gateway / mcp-prompt-hub
```

业务后端继续保存确定性状态，AI Gateway 和 MCP 服务负责模型、Prompt、配额、成本和工具调用。
