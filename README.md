# AstraFlow AI

企业级 AI 工作流与智能审核平台，第一阶段只实现平台底座，不做真实 AI。

## 已生成目录

```text
backend/   FastAPI 后端
frontend/  Vue 3 微前端 monorepo
infra/     Docker Compose、Nginx、本地脚本
```

## 一键启动

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj
docker compose -f infra/docker-compose.local.yml up --build
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

## 本地开发启动

先启动数据库和缓存：

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj
docker compose -f infra/docker-compose.local.yml up -d postgres redis
```

启动后端：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
python -m app.db.init_db
uvicorn app.main:app --reload --port 18080
```

启动前端：

```bash
cd ../frontend
pnpm install
pnpm dev
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
