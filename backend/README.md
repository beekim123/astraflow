# AstraFlow Backend

后端从第一阶段模块化单体演进到第二阶段服务化拆分：

- FastAPI + Pydantic v2
- SQLAlchemy 2.x AsyncSession + asyncpg
- PostgreSQL 持久化
- Redis 访问门禁验证码
- JWT + Refresh Token
- RBAC 权限、动态菜单
- 操作日志和 RequestID
- AI 边界：`AgentClient` + `HttpAgentClient`

## 阶段 2 服务边界

本阶段仍然共用一个后端代码仓库和镜像，但运行时拆成三个进程/容器：

```text
backend-api       通用业务 API：登录、RBAC、菜单、聊天业务状态、附件、产物落库
ai-gateway        AI 编排服务：安全检查、模型路由、Prompt、RAG 预留、模型调用日志
mcp-llm-gateway   模型工具服务：mock/openai-compatible Provider 和流式模型调用
```

聊天模块只依赖 `AgentClient`，通过 `AI_GATEWAY_URL` 调用 `ai-gateway`，不再直接 import AI 编排函数。

## 本地断点调试

后端本地调试时，只让 Docker 跑 PostgreSQL 和 Redis，后端进程在本机启动。

先在项目根目录启动基础设施：

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj
./infra/scripts/debug-infra-up.sh
```

再启动后端：

```bash
cd /Users/key_/Desktop/CURRGO/AI/AstraFlow/proj/backend
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
test -f .env || cp .env.example .env
python -m alembic upgrade head
python -m app.db.init_db
python -m uvicorn app.main:app --reload --port 18080
```

如果要在本机直接调试聊天接口，还需要同时启动 `ai-gateway` 和 `mcp-llm-gateway`，或使用 `infra/docker-compose.local.yml --profile full` 启动完整链路。

`backend/.env.example` 默认连接本机端口：

```text
DATABASE_URL=postgresql+asyncpg://astraflow:astraflow@localhost:15432/astraflow
REDIS_URL=redis://localhost:16379/0
```

不要把这里改成 `postgres:5432` 或 `redis:6379`，那是 Docker 容器内部使用的地址。

Swagger：

```text
http://localhost:18080/docs
```

默认账号：

```text
admin / Admin@123456
member / Member@123456
```

## 测试

基础测试不依赖真实数据库：

```bash
pytest
```

登录成功测试需要先启动 PostgreSQL 并初始化种子数据：

```bash
RUN_DB_TESTS=1 pytest app/tests/test_auth.py
```

## 第一阶段故意不做

- 不接真实大模型。
- 不做 RAG。
- 不做 OCR。
- 不拆微服务。
- 不接 Nacos。

第二阶段已把 `MockAgentClient` 主链路替换为调用 `ai-gateway` 的 HTTP 客户端，再由 `ai-gateway` 统一转发到 `mcp-llm-gateway`。
